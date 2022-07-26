import base64
from curses.ascii import isdigit
from urllib import request
from django.shortcuts import render, redirect
from datetime import date, datetime
from isodate import date_isoformat
import requests
from requests import Session
from requests_ntlm import HttpNtlmAuth
import json
from django.conf import settings as config
import datetime as dt
from django.contrib import messages
from django.http import HttpResponse
import io as BytesIO
import secrets
import string
from django.http import JsonResponse

# Create your views here.


def Loan_Calculator(request):
    try:
        session = requests.Session()
        session.auth = config.AUTHS

        todays_date = dt.datetime.now().strftime("%b. %d, %Y %A")
        ctx = {"today": todays_date
           }
    except KeyError as e:
        messages.info(request, "Session Expired. Please Login")
        return redirect('auth')
    return render(request, 'calculator.html', ctx)


def CreatePlanner(request):
    plannerNo = ""
    employeeNo = request.session['Employee_No_']
    myAction = ""
    if request.method == 'POST':
        try:
            myAction = request.POST.get('myAction')
        except ValueError as e:
            messages.error(request, "Not sent. Invalid Input, Try Again!!")
            return redirect('LeavePlanner')
        try:
            response = config.CLIENT.service.FnLeavePlannerHeader(
                plannerNo, employeeNo, myAction)
            messages.success(request, "Request Successful")
            print(response)
        
        except Exception as e:
            messages.error(request, e)
            print(e)
    return redirect('LeavePlanner')


def FnSubmitLeavePlanner(request, pk):
    plannerNo = pk
    employeeNo = request.session['Employee_No_']
    if request.method == 'POST':
        try:
            response = config.CLIENT.service.FnSubmitLeavePlanner(
                plannerNo, employeeNo)
            messages.success(request, "Request Successful")
            print(response)
        except Exception as e:
            messages.error(request, e)
            print(e)
    return redirect('PlanDetail', pk=pk)

# Delete leave Planner Header

def CreatePlannerLine(request, pk):
    lineNo = ""
    plannerNo = pk
    startDate = ""
    endDate = ""
    myAction = ""

    if request.method == 'POST':
        try:
            lineNo = int(request.POST.get('lineNo'))
            startDate = datetime.strptime(
                (request.POST.get('startDate')), '%Y-%m-%d').date()
            endDate = datetime.strptime(
                (request.POST.get('endDate')), '%Y-%m-%d').date()
            myAction = request.POST.get('myAction')
        except ValueError as e:
            messages.error(request, "Not sent. Invalid Input, Try Again!!")
            return redirect('PlanDetail', pk=pk)
    if not lineNo:
        lineNo = 0
    try:
        response = config.CLIENT.service.FnLeavePlannerLine(
            lineNo, plannerNo, startDate, endDate, myAction)
        messages.success(request, "Request Successful")
        print(response)
    except Exception as e:
        messages.error(request, e)
        print(e)
    return redirect('PlanDetail', pk=pk)


def FnDeleteLeavePlannerLine(request, pk):
    plannerNo = pk
    lineNo = ""

    if request.method == 'POST':
        try:
            lineNo = int(request.POST.get('lineNo'))
        except ValueError as e:
            messages.error(request, "Not sent. Invalid Input, Try Again!!")
            return redirect('PlanDetail', pk=pk)
        print(plannerNo,lineNo)
        try:
            response = config.CLIENT.service.FnDeleteLeavePlannerLine(plannerNo,
                                                                    lineNo)
            messages.success(request, "Successfully  Deleted!!")
            print(response)
        except Exception as e:
            messages.error(request, e)
            print(e)
    return redirect('PlanDetail', pk=pk)


def Loan_Request(request):
    try:
        stage = 'Customer'
        CustomerNumber= '00002'
        # CustomerName=request.session['CustomerName']
        # CustomerNumber=request.session['CustomerNo']
        # MemberNo=request.session['MemberNo']
        # CustomerEmail=request.session['CustomerEmail']
        # stage=request.session['stage']
        # Coordinates=request.session['Coordinates'] 
        session = requests.Session()
        session.auth = config.AUTHS

        LoanProduct = config.O_DATA.format("/LoanProducts")
        EDPBranch = config.O_DATA.format("/DimensionValues")
        Loans = config.O_DATA.format("/Loans")
        try:
            response = session.get(Loans, timeout=10).json()
            open = []
            Approved = []
            Rejected = []
            Pending = []
            for document in response['value']:
                if document['Approval_Status'] == 'Open' and document['Member_Number'] == CustomerNumber:
                    output_json = json.dumps(document)
                    open.append(json.loads(output_json))
                if document['Approval_Status'] == 'Released' and document['Member_Number'] == CustomerNumber:
                    output_json = json.dumps(document)
                    Approved.append(json.loads(output_json))
                if document['Approval_Status'] == 'Disapproved' and document['Member_Number'] == CustomerNumber:
                    output_json = json.dumps(document)
                    Rejected.append(json.loads(output_json))
                if document['Approval_Status'] == "Pending Approval" and document['Member_Number'] == CustomerNumber:
                    output_json = json.dumps(document)
                    Pending.append(json.loads(output_json))
            LoanProductResponse = session.get(LoanProduct, timeout=10).json()
            loanProducts = LoanProductResponse['value']
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
    counts = len(open)
    counter = len(Approved)
    reject = len(Rejected)
    pend = len(Pending)
    ctx = {"today": todays_date, "loanProducts":loanProducts,
        "stage":stage, "branch":Branch, "res": open,
            "count": counts, "response": Approved,
            "counter": counter, "rej": Rejected,
            'reject': reject, "pend": pend,
            "pending": Pending, 
            }
    return render(request, 'loan.html', ctx)


def ApplyLoan(request):
    if request.method == 'POST':
        try:
            loanNo = ''
            clientCode = '0000001'
            # clientCode = request.session['CustomerNo']
            studentCount = int(request.POST.get('studentCount'))
            noOfTeachers = int(request.POST.get('noOfTeachers'))
            minFeesPerStudent = float(request.POST.get('minFeesPerStudent'))
            maxFeesPerStudent = float(request.POST.get('maxFeesPerStudent'))
            branchCode = request.POST.get('branchName')
            subBranchCode = request.POST.get('subBranch')
            loanProduct = request.POST.get('loanProduct')
            subProductCode = request.POST.get('subProductCode')
            loanPurpose = request.POST.get('loanPurpose')
            appliedAmount = float(request.POST.get('subProductCode'))
            myAction = request.POST.get('myAction')
        except ValueError:
            messages.error(request,"Missing Input")
            return redirect('loan')
        except KeyError:
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth')
        try:
            response = config.CLIENT.service.FnLoanApplication(
                loanNo, clientCode, studentCount, noOfTeachers, minFeesPerStudent,
                maxFeesPerStudent, branchCode,subBranchCode, loanProduct,subProductCode,
                loanPurpose,appliedAmount,myAction)
            messages.success(request, "Request Successful")
            print(response)
        except Exception as e:
            messages.error(request, e)
            print(e)
    return redirect('loan')

def SubBranch(request):
    session = requests.Session()
    session.auth = config.AUTHS
    Item = config.O_DATA.format("/DimensionValues")
    BranchCode = request.GET.get('BranchCode')
    try:
        Item_res = session.get(Item, timeout=10).json()
        return JsonResponse(Item_res)

    except  Exception as e:
        pass
    return redirect('loan')

def LoanDetail(request):
    try:
        stage = 'Customer'
        CustomerNumber= 'CRML00047'
        # CustomerName=request.session['CustomerName']
        # CustomerNumber=request.session['CustomerNo']
        # MemberNo=request.session['MemberNo']
        # CustomerEmail=request.session['CustomerEmail']
        # stage=request.session['stage']
        # Coordinates=request.session['Coordinates'] 
        session = requests.Session()
        session.auth = config.AUTHS

        LoanProduct = config.O_DATA.format("/LoanProducts")
        Applicant = config.O_DATA.format("/ApplicantsList")
        try:
            LoanProductResponse = session.get(LoanProduct, timeout=10).json()
            loanProducts = LoanProductResponse['value']
            ApplicantResponse = session.get(Applicant, timeout=10).json()
            for applicant in ApplicantResponse['value']:
                if applicant['No'] == CustomerNumber:
                    res = applicant
        except requests.exceptions.RequestException as e:
            print(e)
            messages.info(request, "Whoops! Something went wrong. Please Login to Continue")
            return redirect('auth')

        todays_date = dt.datetime.now().strftime("%b. %d, %Y %A")
        
    except KeyError:
        messages.info(request, "Session Expired. Please Login")
        return redirect('auth')

    ctx = {"today": todays_date, "loanProducts":loanProducts,
        "stage":stage, "data":res,
            }
    return render(request, 'loanDetail.html', ctx)

def FnSchoolLoanRevenue(request):
    if request.method == 'POST':
        try:
            entryNo = ""
            applicantNo = "000001"
            # applicantNo = request.session['CustomerNo']
            edpClass = request.POST.get('edpClass')
            streams = request.POST.get('streams')
            termOneFees = float(request.POST.get('termOneFees'))
            termTwoFees = float(request.POST.get('termTwoFees'))
            termThreeFees = float(request.POST.get('termThreeFees'))
            newStudentAdmission = float(request.POST.get('newStudentAdmission'))
            admissionFees = float(request.POST.get('admissionFees'))
            myAction = request.POST.get('myAction')
        except ValueError:
            messages.info(request,"Missing Input!")
            return redirect('LoanDetail')
        except KeyError:
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth')

        try:
            response = config.CLIENT.service.FnSchoolLoanRevenue(
                entryNo, applicantNo,edpClass,streams, termOneFees,termTwoFees,termThreeFees,
                newStudentAdmission,admissionFees, myAction)
            messages.success(request, "Successfully Added")
            print(response)
            return redirect('LoanDetail')
        except Exception as e:
            print(e)
            messages.info(request, e)
            return redirect('LoanDetail')
    return redirect('LoanDetail')

def FnSchoolLoanExpenses(request):
    if request.method == 'POST':
        try:
            entryNo = ""
            applicantNo = "000001"
            # applicantNo = request.session['CustomerNo']
            expenseHead = request.POST.get('expenseHead')
            monthlyExpense = float(request.POST.get('monthlyExpense'))
            multiplierFactor = float(request.POST.get('multiplierFactor'))
            myAction = request.POST.get('myAction')
        except ValueError:
            messages.info(request,"Missing Input!")
            return redirect('LoanDetail')
        except KeyError:
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth')

        try:
            response = config.CLIENT.service.FnSchoolLoanExpenses(
                entryNo, applicantNo,expenseHead,monthlyExpense,multiplierFactor,myAction)
            messages.success(request, "Successfully Added")
            print(response)
            return redirect('LoanDetail')
        except Exception as e:
            print(e)
            messages.info(request, e)
            return redirect('LoanDetail')
    return redirect('LoanDetail')


def UploadLeaveAttachment(request, pk):
    docNo = pk
    response = ""
    fileName = ""
    attachment = ""
    tableID = 52177494

    if request.method == "POST":
        try:
            attach = request.FILES.getlist('attachment')
        except Exception as e:
            return redirect('IMPDetails', pk=pk)
        for files in attach:
            fileName = request.FILES['attachment'].name
            attachment = base64.b64encode(files.read())
            try:
                response = config.CLIENT.service.FnUploadAttachedDocument(
                    docNo, fileName, attachment, tableID)
            except Exception as e:
                messages.error(request, e)
                print(e)
        if response == True:
            messages.success(request, "Successfully Sent !!")

            return redirect('LeaveDetail', pk=pk)
        else:
            messages.error(request, "Not Sent !!")
            return redirect('LeaveDetail', pk=pk)

    return redirect('LeaveDetail', pk=pk)


def LeaveApproval(request, pk):
    employeeNo = request.session['Employee_No_']
    applicationNo = ""
    if request.method == 'POST':
        try:
            applicationNo = request.POST.get('applicationNo')
        except ValueError as e:
            messages.error(request, "Not sent. Invalid Input, Try Again!!")
            return redirect('LeaveDetail', pk=pk)
    try:
        response = config.CLIENT.service.FnRequestLeaveApproval(
            employeeNo, applicationNo)
        messages.success(request, "Approval Request Successfully Sent!!")
        print(response)
        return redirect('LeaveDetail', pk=pk)
    except Exception as e:
        messages.error(request, e)
        print(e)
    return redirect('LeaveDetail', pk=pk)


def LeaveCancelApproval(request, pk):
    employeeNo = request.session['Employee_No_']
    applicationNo = ""
    if request.method == 'POST':
        try:
            applicationNo = request.POST.get('applicationNo')
        except ValueError as e:
            messages.error(request, "Not sent. Invalid Input, Try Again!!")
            return redirect('LeaveDetail', pk=pk)
    try:
        response = config.CLIENT.service.FnCancelLeaveApproval(
            employeeNo, applicationNo)
        messages.success(request, "Cancel Approval Request Successful !!")
        print(response)
        return redirect('LeaveDetail', pk=pk)
    except Exception as e:
        messages.error(request, e)
        print(e)
    return redirect('LeaveDetail', pk=pk)


def TopUpsRequest(request):
    try:
        fullname = request.session['User_ID']
        year = request.session['years']

        session = requests.Session()
        session.auth = config.AUTHS

        Access_Point = config.O_DATA.format("/QyTrainingRequests")
        currency = config.O_DATA.format("/QyCurrencies")
        trainingNeed = config.O_DATA.format("/QyTrainingNeeds")
       
        try:
            response = session.get(Access_Point, timeout=10).json()
            res_currency = session.get(currency, timeout=10).json()
            res_train = session.get(trainingNeed, timeout=10).json()
            
            open = []
            Approved = []
            Rejected = []
            Pending = []
            cur = res_currency['value']
            trains = res_train['value']

            for imprest in response['value']:
                if imprest['Status'] == 'Open' and imprest['Employee_No'] == request.session['Employee_No_']:
                    output_json = json.dumps(imprest)
                    open.append(json.loads(output_json))
                if imprest['Status'] == 'Released' and imprest['Employee_No'] == request.session['Employee_No_']:
                    output_json = json.dumps(imprest)
                    Approved.append(json.loads(output_json))
                if imprest['Status'] == 'Rejected' and imprest['Employee_No'] == request.session['Employee_No_']:
                    output_json = json.dumps(imprest)
                    Rejected.append(json.loads(output_json))
                if imprest['Status'] == 'Pending Approval' and imprest['Employee_No'] == request.session['Employee_No_']:
                    output_json = json.dumps(imprest)
                    Pending.append(json.loads(output_json))
            counts = len(open)

            counter = len(Approved)

            reject = len(Rejected)

            pend = len(Pending)
        except requests.exceptions.ConnectionError as e:
            print(e)
            messages.error(request,"500 Server Error, Try Again in a few")
            return redirect('dashboard')

        todays_date = dt.datetime.now().strftime("%b. %d, %Y %A")
        ctx = {"today": todays_date, "res": open,
            "count": counts, "response": Approved,
            "counter": counter, "rej": Rejected,
            'reject': reject, 'cur': cur,
            "train": trains,
            "pend": pend, "pending": Pending,
            "year": year, "full": fullname}
    except KeyError:
        messages.info(request, "Session Expired. Please Login")
        return redirect('auth')
    return render(request, 'topUps.html', ctx)


def CreateTrainingRequest(request):
    requestNo = ''
    employeeNo = request.session['Employee_No_']
    usersId = request.session['User_ID']
    isAdhoc = ""
    trainingNeed = ""
    myAction = ''
    if request.method == 'POST':
        try:
            requestNo = request.POST.get('requestNo')
            isAdhoc = eval(request.POST.get('isAdhoc'))
            trainingNeed = request.POST.get('trainingNeed')
            myAction = request.POST.get('myAction')
        except ValueError:
            messages.error(request, "Not sent. Invalid Input, Try Again!!")
            return redirect('training_request')
        if not requestNo:
            requestNo = ""
        
        if not trainingNeed:
            trainingNeed = ''
        try:
            response = config.CLIENT.service.FnTrainingRequest(
                requestNo, employeeNo, usersId, isAdhoc, trainingNeed, myAction)
            messages.success(request, "Successfully Added!!")
            print(response)
        except Exception as e:
            messages.error(request, e)
            print(e)
            return redirect('training_request')
    return redirect('training_request')


def TopUpDetail(request):
    session = requests.Session()
    session.auth = config.AUTHS
    todays_date = dt.datetime.now().strftime("%b. %d, %Y %A")
    ctx = {"today": todays_date}
    return render(request, 'topUpDetail.html', ctx)


def FnAdhocTrainingNeedRequest(request, pk):
    requestNo = pk
    no = ""
    employeeNo = request.session['Employee_No_']
    trainingName = ""
    trainingArea = ""
    trainingObjectives = ""
    venue = ""
    provider = ""
    myAction = "insert"
    if request.method == 'POST':
        try:
            trainingName = request.POST.get('trainingName')
            startDate = request.POST.get('startDate')
            endDate = request.POST.get('endDate')
            trainingArea = request.POST.get('trainingArea')
            trainingObjectives = request.POST.get('trainingObjectives')
            venue = request.POST.get('venue')
            sponsor = request.POST.get('sponsor')
            destination = request.POST.get('destination')
            OtherDestinationName = request.POST.get('OtherDestinationName')
            provider = request.POST.get('provider')

        except ValueError as e:
            messages.error(request, "Invalid Input, Try Again!!")
            return redirect('TrainingDetail', pk=pk)
        if not sponsor:
            sponsor = 0
        sponsor = int(sponsor)

        if not destination:
            destination = 'none'
        
        if not venue:
            venue = "Online"

        if OtherDestinationName:
            destination = OtherDestinationName
        try:
            response = config.CLIENT.service.FnAdhocTrainingNeedRequest(requestNo,
                                                                        no, employeeNo, trainingName, trainingArea, trainingObjectives, venue, provider, myAction,sponsor,startDate,endDate,destination)
            messages.success(request, "Successfully Added!!")
            print(response)
            return redirect('TrainingDetail', pk=pk)
        except Exception as e:
            messages.error(request, e)
            print(e)
    return redirect('TrainingDetail', pk=pk)


def UploadTrainingAttachment(request, pk):
    docNo = pk
    response = ""
    fileName = ""
    attachment = ""
    tableID = 52177501

    if request.method == "POST":
        try:
            attach = request.FILES.getlist('attachment')
        except Exception as e:
            return redirect('IMPDetails', pk=pk)
        for files in attach:
            fileName = request.FILES['attachment'].name
            attachment = base64.b64encode(files.read())
            try:
                response = config.CLIENT.service.FnUploadAttachedDocument(
                    docNo, fileName, attachment, tableID)
            except Exception as e:
                messages.error(request, e)
                print(e)
        if response == True:
            messages.success(request, "Successfully Sent !!")

            return redirect('TrainingDetail', pk=pk)
        else:
            messages.error(request, "Not Sent !!")
            return redirect('TrainingDetail', pk=pk)

    return redirect('TrainingDetail', pk=pk)


def FnAdhocTrainingEdit(request, pk, no):
    requestNo = pk
    no = no
    employeeNo = request.session['Employee_No_']
    trainingName = ""
    trainingArea = ""
    trainingObjectives = ""
    venue = ""
    provider = ""
    myAction = "modify"

    if request.method == 'POST':
        try:
            trainingName = request.POST.get('trainingName')
            trainingArea = request.POST.get('trainingArea')
            trainingObjectives = request.POST.get('trainingObjectives')
            venue = request.POST.get('venue')
            provider = request.POST.get('provider')

        except ValueError as e:
            messages.error(request, "Not sent. Invalid Input, Try Again!!")
            return redirect('TrainingDetail', pk=pk)
    try:
        response = config.CLIENT.service.FnAdhocTrainingNeedRequest(requestNo,
                                                                    no, employeeNo, trainingName, trainingArea, trainingObjectives, venue, provider, myAction)
        messages.success(request, "Successfully Edited!!")
        print(response)
        return redirect('TrainingDetail', pk=pk)
    except Exception as e:
        messages.error(request, e)
        print(e)
    return redirect('TrainingDetail', pk=pk)

def FnAdhocLineDelete(request, pk):
    requestNo = pk
    needNo = ''
    if request.method == 'POST':
        try:
            needNo = request.POST.get('needNo')
        except ValueError as e:
            messages.error(request, "Not sent. Invalid Input, Try Again!!")
            return redirect('TrainingDetail', pk=pk)
        print("requestNo", requestNo)
        print("needno", needNo)
        try:
            response = config.CLIENT.service.FnDeleteAdhocTrainingNeedRequest(
                needNo,requestNo)
            messages.success(request, "Successfully Deleted!!")
            print(response)
            return redirect('TrainingDetail', pk=pk)
        except Exception as e:
            messages.error(request, e)
            print(e)
    return redirect('TrainingDetail', pk=pk)


def TrainingApproval(request, pk):
    myUserID = request.session['User_ID']
    trainingNo = ""
    if request.method == 'POST':
        try:
            trainingNo = request.POST.get('trainingNo')
        except ValueError as e:
            messages.error(request, "Not sent. Invalid Input, Try Again!!")
            return redirect('TrainingDetail', pk=pk)
    try:
        response = config.CLIENT.service.FnRequestTrainingApproval(
            myUserID, trainingNo)
        messages.success(request, "Approval Request Successfully Sent!!")
        print(response)
        return redirect('TrainingDetail', pk=pk)
    except Exception as e:
        messages.error(request, e)
        print(e)
    return redirect('TrainingDetail', pk=pk)


def TrainingCancelApproval(request, pk):
    myUserID = request.session['User_ID']
    trainingNo = ""
    if request.method == 'POST':
        try:
            trainingNo = request.POST.get('trainingNo')
        except ValueError as e:
            messages.error(request, "Not sent. Invalid Input, Try Again!!")
            return redirect('TrainingDetail', pk=pk)
    try:
        response = config.CLIENT.service.FnCancelTrainingApproval(
            myUserID, trainingNo)
        messages.success(request, "Cancel Approval Request Successful !!")
        print(response)
        return redirect('TrainingDetail', pk=pk)
    except Exception as e:
        messages.error(request, e)
        print(e)
    return redirect('TrainingDetail', pk=pk)


def PNineRequest(request):
    try:
        nameChars = ''.join(secrets.choice(string.ascii_uppercase + string.digits)
                        for i in range(5))
        fullname = request.session['User_ID']
        year = request.session['years']
        todays_date = dt.datetime.now().strftime("%b. %d, %Y %A")
        session = requests.Session()
        session.auth = config.AUTHS
        
        Access_Point = config.O_DATA.format("/QyPayrollPeriods")
        
        try:
            response = session.get(Access_Point, timeout=10).json()
            res = response['value']
        except requests.exceptions.ConnectionError as e:
            print(e)
        employeeNo = request.session['Employee_No_']
        filenameFromApp = ""
        startDate = ""
        year = ''
        if request.method == 'POST':
            try:
                startDate = request.POST.get('startDate')[0:4]
            except ValueError as e:
                messages.error(request, "Not sent. Invalid Input, Try Again!!")
                return redirect('pNine')
            filenameFromApp = "P9_For_" + str(nameChars) + year + ".pdf"
            year = int(startDate)
            try:
                response = config.CLIENT.service.FnGeneratePNine(
                    employeeNo, filenameFromApp, year)
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
                    messages.error(request, "Payslip not found for the selected period")
                    return redirect('pNine')
            except Exception as e:
                messages.error(request, e)
                print(e)
                return redirect('pNine')
        ctx = {"today": todays_date, "year": year, "full": fullname,"res":res}
    except KeyError:
        messages.info(request, "Session Expired. Please Login")
        return redirect('auth')
    return render(request, "p9.html", ctx)


def PayslipRequest(request):
    try:
        nameChars = ''.join(secrets.choice(string.ascii_uppercase + string.digits)
                        for i in range(5))
        fullname = request.session['User_ID']
        year = request.session['years']
        session = requests.Session()
        session.auth = config.AUTHS
        
        Access_Point = config.O_DATA.format("/QyPayrollPeriods")
        try:
            response = session.get(Access_Point, timeout=10).json()
            res = response['value']
        except requests.exceptions.ConnectionError as e:
            print(e)
            
        todays_date = dt.datetime.now().strftime("%b. %d, %Y %A")
        employeeNo = request.session['Employee_No_']
        filenameFromApp = ""
        paymentPeriod = ""
        if request.method == 'POST':
            try:
                paymentPeriod = datetime.strptime(
                    request.POST.get('paymentPeriod'), '%Y-%m-%d').date()

            except ValueError as e:
                messages.error(request, "Not sent. Invalid Input, Try Again!!")
                return redirect('payslip')
            filenameFromApp = "Payslip" + str(paymentPeriod) + str(nameChars) + ".pdf"
            try:
                response = config.CLIENT.service.FnGeneratePayslip(
                    employeeNo, filenameFromApp, paymentPeriod)
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
                    messages.error(request, "Payslip not found for the selected period")
                    return redirect('payslip')
            except Exception as e:
                messages.error(request, e)
                print(e)
        ctx = {"today": todays_date, "year": year, "full": fullname,"res":res}
    except KeyError:
        messages.info(request, "Session Expired. Please Login")
        return redirect('auth')
    return render(request, "payslip.html", ctx)
# Leave Report


def FnGenerateLeaveReport(request, pk):
    nameChars = ''.join(secrets.choice(string.ascii_uppercase + string.digits)
                        for i in range(5))
    employeeNo = request.session['Employee_No_']
    filenameFromApp = ''
    applicationNo = pk
    if request.method == 'POST':
        try:
            filenameFromApp = pk
        except ValueError as e:
            messages.error(request, "Invalid Line number, Try Again!!")
            return redirect('LeaveDetail', pk=pk)
        filenameFromApp = filenameFromApp + str(nameChars) + ".pdf"
        print("filenameFromApp", filenameFromApp)
        print("applicationNo", applicationNo)
        try:
            response = config.CLIENT.service.FnGenerateLeaveReport(
                employeeNo, filenameFromApp, applicationNo)
            buffer = BytesIO.BytesIO()
            content = base64.b64decode(response)
            buffer.write(content)
            responses = HttpResponse(
                buffer.getvalue(),
                content_type="application/pdf",
            )
            responses['Content-Disposition'] = f'inline;filename={filenameFromApp}'
            return responses
        except Exception as e:
            messages.error(request, e)
            print(e)
    return redirect('LeaveDetail', pk=pk)
# Training report


def FnGenerateTrainingReport(request, pk):
    nameChars = ''.join(secrets.choice(string.ascii_uppercase + string.digits)
                        for i in range(5))
    employeeNo = request.session['Employee_No_']
    filenameFromApp = ''
    applicationNo = pk
    if request.method == 'POST':
        try:
            filenameFromApp = pk
        except ValueError as e:
            messages.error(request, "Invalid Line number, Try Again!!")
            return redirect('TrainingDetail', pk=pk)
    filenameFromApp = filenameFromApp + str(nameChars) + ".pdf"
    try:
        response = config.CLIENT.service.FnGenerateTrainingReport(
            employeeNo, filenameFromApp, applicationNo)
        buffer = BytesIO.BytesIO()
        content = base64.b64decode(response)
        buffer.write(content)
        responses = HttpResponse(
            buffer.getvalue(),
            content_type="application/pdf",
        )
        responses['Content-Disposition'] = f'inline;filename={filenameFromApp}'
        return responses
    except Exception as e:
        messages.error(request, e)
        print(e)
    return redirect('TrainingDetail', pk=pk)
def Disciplinary(request):
    fullname = request.session['User_ID']
    year = request.session['years']
    session = requests.Session()
    session.auth = config.AUTHS

    Access_Point = config.O_DATA.format("/QyEmployeeDisciplinaryCases")
    try:
        response = session.get(Access_Point, timeout=10).json()
        openCase = []
        for case in response['value']:
            if case['Employee_No'] == request.session['Employee_No_'] and case['Posted'] == False and case['Sent_to_employee'] == True and case['Submit'] == False:
                output_json = json.dumps(case)
                openCase.append(json.loads(output_json))
        counts = len(openCase)
        print(counts)
    except requests.exceptions.ConnectionError as e:
        print(e)

    todays_date = dt.datetime.now().strftime("%b. %d, %Y %A")
    ctx = {"today": todays_date, "res": openCase,
           "year": year, "full": fullname,
           "count": counts}
    return render(request,'disciplinary.html',ctx)

def DisciplineDetail(request,pk):
    fullname = request.session['User_ID']
    year = request.session['years']
    session = requests.Session()
    session.auth = config.AUTHS
    res = ''
    Access_Point = config.O_DATA.format("/QyEmployeeDisciplinaryCases")
    try:
        response = session.get(Access_Point, timeout=10).json()
        Case = []
        for case in response['value']:
            if case['Employee_No'] == request.session['Employee_No_'] and case['Posted'] == False and case['Sent_to_employee'] == True and case['Submit'] == False:
                output_json = json.dumps(case)
                Case.append(json.loads(output_json))
                for case in Case:
                    if case['Disciplinary_Nos'] == pk:
                        res = case
    except requests.exceptions.ConnectionError as e:
        print(e)
    Lines_Res = config.O_DATA.format("/QyEmployeeDisciplinaryLines")
    try:
        responses = session.get(Lines_Res, timeout=10).json()
        openLines = []
        for cases in responses['value']:
            if cases['Refference_No'] == pk and cases['Employee_No'] == request.session['Employee_No_']:
                output_json = json.dumps(cases)
                openLines.append(json.loads(output_json))
    except requests.exceptions.ConnectionError as e:
        print(e)
    todays_date = dt.datetime.now().strftime("%b. %d, %Y %A")
    ctx = {"today": todays_date, "res": res, "full": fullname, "year": year,"line": openLines}
    return render (request, 'disciplineDetail.html',ctx)

def DisciplinaryResponse(request, pk):

    employeeNo = request.session['Employee_No_']
    caseNo = pk
    myResponse = ''
    
    if request.method == 'POST':
        try:
            myResponse = request.POST.get('myResponse')
        except ValueError as e:
            messages.error(request, "Invalid, Try Again!!")
            return redirect('DisciplineDetail', pk=pk)
    try:
        response = config.CLIENT.service.FnEmployeeDisciplinaryResponse(
            employeeNo, caseNo, myResponse)
        messages.success(request, "Response Successful Sent!!")
        print(response)
        return redirect('DisciplineDetail', pk=pk)
    except Exception as e:
        messages.error(request, e)
        print(e)
    return redirect('DisciplineDetail', pk=pk)