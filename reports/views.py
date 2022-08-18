from django.shortcuts import render,redirect
import requests
from requests import Session
import json
from django.conf import settings as config
from django.contrib import messages
from django.http import JsonResponse,HttpResponse
import simplejson as jsons
import datetime as dt
import base64
import io as BytesIO
# Create your views here.
def Reports(request):
    try:
        CustomerName=request.session['CustomerName']
        CustomerNumber=request.session['CustomerNo']
        MemberNo=request.session['MemberNo']
        stage=request.session['stage']
        todays_date = dt.datetime.now().strftime("%b. %d, %Y %A")
        session = requests.Session()
        session.auth = config.AUTHS
        Loans = config.O_DATA.format("/Loans?$filter=Member_Number%20eq%20%27{MemberNo}%27").format(MemberNo=MemberNo)
        try:
            response = session.get(Loans, timeout=10).json()
            Approved = []
            for document in response['value']:
                if document['Approval_Status'] == 'Approved':
                    output_json = json.dumps(document)
                    Approved.append(json.loads(output_json))
        except requests.exceptions.RequestException as e:
            print(e)
            messages.info(request, "Whoops! Something went wrong. Please Login to Continue")
            return redirect('auth')
    except KeyError:
        messages.info(request, "Session Expired. Please Login")
        return redirect('login')
    ctx = {"today": todays_date,"full": CustomerName,"stage":stage,"loans":Approved
           }
    return render(request,'reports.html',ctx)

def FnDetailedCustomerReport(request):
    if request.method == 'POST':
            clientCode = request.session['MemberNo']
            filenameFromApp = "ClientDetailedReport"
            try:
                response = config.CLIENT.service.FnDetailedCustomerReport(
                    clientCode, filenameFromApp)
                try:
                    buffer = BytesIO.BytesIO()
                    content = base64.b64decode(response)
                    buffer.write(content)
                    responses = HttpResponse(
                        buffer.getvalue(),
                        content_type="application/pdf",
                    )
                    responses['Content-Disposition'] = f'inline;filename={filenameFromApp}'
                    return responses
                except:
                    messages.error(request, "Request Not successful")
                    return redirect('Reports')
            except Exception as e:
                print(e)
                messages.info(request, e)
    return redirect('Reports')

def FnLoanStatementReport(request):
    if request.method == 'POST':
            clientCode = request.session['MemberNo']
            loanNo = request.POST.get('loanNo')
            filenameFromApp = "LoanStatement"
            try:
                response = config.CLIENT.service.FnLoanStatementReport(loanNo,
                    clientCode, filenameFromApp)
                try:
                    buffer = BytesIO.BytesIO()
                    content = base64.b64decode(response)
                    buffer.write(content)
                    responses = HttpResponse(
                        buffer.getvalue(),
                        content_type="application/pdf",
                    )
                    responses['Content-Disposition'] = f'inline;filename={filenameFromApp}'
                    return responses
                except:
                    messages.error(request, "Request Not successful")
                    return redirect('Reports')
            except Exception as e:
                print(e)
                messages.info(request, e)
    return redirect('Reports')

def FnLoanRepaymentScheduleReport(request):
    if request.method == 'POST':
            loanNo = request.POST.get('loanNo')
            filenameFromApp = "LoanRepaymentScheduleReport"
            try:
                response = config.CLIENT.service.FnLoanRepaymentScheduleReport(loanNo,
                     filenameFromApp)
                try:
                    buffer = BytesIO.BytesIO()
                    content = base64.b64decode(response)
                    buffer.write(content)
                    responses = HttpResponse(
                        buffer.getvalue(),
                        content_type="application/pdf",
                    )
                    responses['Content-Disposition'] = f'inline;filename={filenameFromApp}'
                    return responses
                except:
                    messages.error(request, "Request Not successful")
                    return redirect('Reports')
            except Exception as e:
                print(e)
                messages.info(request, e)
    return redirect('Reports')

def FnCalculatorScheduleReport(request):
    if request.method == 'POST':
            filenameFromApp = "CalculatorScheduleReport"
            try:
                response = config.CLIENT.service.FnCalculatorScheduleReport(
                     filenameFromApp)
                try:
                    buffer = BytesIO.BytesIO()
                    content = base64.b64decode(response)
                    buffer.write(content)
                    responses = HttpResponse(
                        buffer.getvalue(),
                        content_type="application/pdf",
                    )
                    responses['Content-Disposition'] = f'inline;filename={filenameFromApp}'
                    return responses
                except:
                    messages.error(request, "Request Not successful")
                    return redirect('Loan_Calculator')
            except Exception as e:
                print(e)
                messages.info(request, e)
    return redirect('Loan_Calculator')
