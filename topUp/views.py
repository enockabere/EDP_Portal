from django.shortcuts import render,redirect
import requests
from requests import Session
from requests_ntlm import HttpNtlmAuth
import json
from django.conf import settings as config
import datetime as dt
from django.contrib import messages

# Create your views here.
def LoanTopUp(request):
    try:
        CustomerName=request.session['CustomerName']
        CustomerNumber=request.session['CustomerNo']
        MemberNo=request.session['MemberNo']
        CustomerEmail=request.session['CustomerEmail']
        stage=request.session['stage']
        session = requests.Session()
        session.auth = config.AUTHS

        LoanProduct = config.O_DATA.format("/LoanProducts")
        EDPBranch = config.O_DATA.format("/DimensionValues")
        Loans = config.O_DATA.format("/Loans")
        try:
            response = session.get(Loans, timeout=10).json()
            openDoc = []
            Approved = []
            Rejected = []
            Pending = []
            for document in response['value']:
                if document['Approval_Status'] == 'Open' and document['Member_Number'] == MemberNo:
                    output_json = json.dumps(document)
                    openDoc.append(json.loads(output_json))
                if document['Approval_Status'] == 'Approved' and document['Member_Number'] == MemberNo:
                    output_json = json.dumps(document)
                    Approved.append(json.loads(output_json))
                if document['Approval_Status'] == 'Disapproved' and document['Member_Number'] == MemberNo:
                    output_json = json.dumps(document)
                    Rejected.append(json.loads(output_json))
                if document['Approval_Status'] == "Pending Approval" and document['Member_Number'] == MemberNo:
                    output_json = json.dumps(document)
                    Pending.append(json.loads(output_json))
            LoanProductResponse = session.get(LoanProduct, timeout=10).json()
            loanProducts = LoanProductResponse['value']
            
            LoanPurposes = config.O_DATA.format("/LoanPurposes")
            LoanPurposesResponse = session.get(LoanPurposes, timeout=10).json()
            Purpose = LoanPurposesResponse['value']

            BranchResponse = session.get(EDPBranch, timeout=10).json()
            Branch = []
            for branch in BranchResponse['value']:
                if branch['Dimension_Code'] == 'BRANCH':
                    output_json = json.dumps(branch)
                    Branch.append(json.loads(output_json))
        except requests.exceptions.RequestException as e:
            print(e)
            messages.info(request, "Whoops! Something went wrong. Please Login to Continue")
            return redirect('auth')

        todays_date = dt.datetime.now().strftime("%b. %d, %Y %A")
        
    except KeyError:
        messages.info(request, "Session Expired. Please Login")
        return redirect('auth')
    counts = len(openDoc)
    counter = len(Approved)
    reject = len(Rejected)
    pend = len(Pending)
    ctx = {"today": todays_date, "loanProducts":loanProducts,
        "stage":stage, "branch":Branch, "res": openDoc,
            "count": counts, "response": Approved,
            "counter": counter, "rej": Rejected,
            'reject': reject, "pend": pend,
            "pending": Pending, "Purpose":Purpose
            }
    return render(request,"topUp.html",ctx)

def FnLoanTopUp(request,pk):
    if request.method == 'POST':
        try:
            loanNo = pk
            clientCode = request.session['MemberNo']
            loanToOffset = request.POST.get('loanToOffset')
            myAction = 'insert'
        except ValueError:
            messages.info(request,"Missing Input!")
            return redirect('LoanDetail',pk=pk)
        except KeyError:
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth')
        try:
            response = config.CLIENT.service.FnLoanTopUp(
                loanNo, clientCode,loanToOffset,myAction)
            print(response)
            messages.success(request, "Request Successfully")
            return redirect('LoanDetail',pk=pk)
        except Exception as e:
            print(e)
            messages.info(request, e)
            return redirect('LoanDetail',pk=pk)
    return redirect('LoanDetail',pk=pk)
