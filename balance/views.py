from django.shortcuts import render,redirect
import requests
from requests import Session
import json
from django.conf import settings as config
from django.contrib import messages
from django.http import JsonResponse
import simplejson as jsons
# Create your views here.
def BalanceEnquiry(request):
    try:
        CustomerName=request.session['CustomerName']
        CustomerNumber=request.session['CustomerNo']
        MemberNo=request.session['MemberNo']
        CustomerEmail=request.session['CustomerEmail']
        stage=request.session['stage']
        session = requests.Session()
        session.auth = config.AUTHS
        Loans = config.O_DATA.format("/Loans")
        try:
            response = session.get(Loans, timeout=10).json()
            Approved = []
            for document in response['value']:
                if document['Approval_Status'] == 'Approved' and document['Member_Number'] == MemberNo:
                    output_json = json.dumps(document)
                    Approved.append(json.loads(output_json))
        except requests.exceptions.RequestException as e:
            print(e)
            messages.info(request, "Whoops! Something went wrong. Please Login to Continue")
            return redirect('auth')
        if request.method == 'POST':
            loanNo = request.POST.get('loanNo')
            outstandingBalance =float(request.POST.get('outstandingBalance'))
            outstandingInterest = float(request.POST.get('outstandingInterest'))
            try:
                response = config.CLIENT.service.FnBalanceInquiries(
                    loanNo, outstandingBalance,outstandingInterest)
                print("Month Repayment:", response)
                if response['return_value'] == True:
                    mp = jsons.dumps(response,use_decimal=True)
                    return JsonResponse(mp,safe=False)
                if response['return_value'] == False:
                    return JsonResponse("Null",safe=False)
            except Exception as e:
                print(e)
                messages.info(request, e)
                return redirect('BalanceEnquiry')
    except KeyError:
        messages.info(request, "Session Expired. Please Login")
        return redirect('auth')
    ctx = {"loans":Approved}
    return render(request,"balance.html",ctx)