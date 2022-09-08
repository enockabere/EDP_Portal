from django.shortcuts import render,redirect
import requests
from requests import Session
import json
from django.conf import settings as config
from django.contrib import messages
from django.http import JsonResponse
import datetime as dt
import simplejson as jsons
from django.views import View
from datetime import  datetime

class UserObjectMixin(object):
    model =None
    session = requests.Session()
    session.auth = config.AUTHS
    todays_date = dt.datetime.now().strftime("%b. %d, %Y %A")
    def get_object(self,endpoint):
        response = self.session.get(endpoint, timeout=10).json()
        return response
        
class BalanceEnquiry(UserObjectMixin,View):
    def get(self,request):
        try:
            CustomerName=request.session['CustomerName']
            MemberNo=request.session['MemberNo']
            todays_date = dt.datetime.now().strftime("%b. %d, %Y %A")
            stage=request.session['stage']

            Loans = config.O_DATA.format(f"/Loans?$filter=Member_Number%20eq%20%27{MemberNo}%27%20and%20Approval_Status%20eq%20%27Approved%27")
            response = self.get_object(Loans)
            Approved = [ x for x in response['value']]

        except requests.exceptions.RequestException as e:
            print(e)
            messages.info(request, "Whoops! Something went wrong. Please Login to Continue")
            return redirect('auth')
        except KeyError:
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth')
        ctx = {"loans":Approved,"today": todays_date,"full": CustomerName,"stage":stage,}
        return render(request,"balance.html",ctx)
    def post(self, request):
        if request.method == 'POST':
                loanNo = request.POST.get('loanNo')
                outstandingBalance =0
                outstandingInterest = 0
                dueDate = datetime.strptime("2000-1-1", '%Y-%m-%d').date()
                amountPayable =0
                try:
                    response = config.CLIENT.service.FnBalanceInquiries(
                        loanNo, outstandingBalance,outstandingInterest,dueDate,amountPayable)
                    due = str(response['dueDate'])
                    if response['return_value'] == True:
                        outstanding = jsons.dumps(response['outstandingBalance'],use_decimal=True)
                        dueDate = jsons.dumps(due,use_decimal=True)
                        interest = jsons.dumps(response['outstandingInterest'],use_decimal=True)
                        amountPayables = jsons.dumps(response['amountPayable'],use_decimal=True)
                        Dict = {
                                "return_value":response['return_value'],
                                "outstandingBalance":outstanding,
                                "outstandingInterest":interest,
                                "dueDate":due,
                                "amountPayable":amountPayables
                                }
                        return JsonResponse(Dict,safe=False)
                    if response['return_value'] == False:
                        return JsonResponse("Null",safe=False)
                except Exception as e:
                    print(e)
                    messages.info(request, e)
                    return redirect('BalanceEnquiry')