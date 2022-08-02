import base64
from curses.ascii import isdigit
from ssl import Purpose
from urllib import request
from django.shortcuts import render, redirect
from datetime import date, datetime
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
        CustomerName=request.session['CustomerName']
        CustomerNumber=request.session['CustomerNo']
        MemberNo=request.session['MemberNo']
        CustomerEmail=request.session['CustomerEmail']
        stage=request.session['stage']

        LoanProduct = config.O_DATA.format("/LoanProducts")
        LoanProductResponse = session.get(LoanProduct, timeout=10).json()
        loanProducts = LoanProductResponse['value']

        if request.method == 'POST':
            try:
                calculatorType = int(request.POST.get('calculatorType'))
                loanType =request.POST.get('loanType')
                requestedAmount = float(request.POST.get('requestedAmount'))
                disbursementDate =datetime.strptime( request.POST.get('disbursementDate'), '%Y-%m-%d').date()
                repaymentStartDate = datetime.strptime(request.POST.get('repaymentStartDate'), '%Y-%m-%d').date()
            except ValueError:
                messages.info(request,"Missing Input!")
                return redirect('Loan_Calculator')
            try:
                response = config.CLIENT.service.FnLoanCalculator(
                    calculatorType, loanType,requestedAmount,disbursementDate,repaymentStartDate)
                print(response)
                return JsonResponse(response)
            except Exception as e:
                print(e)
                messages.info(request, e)
                return redirect('Loan_Calculator')

        ctx = {"today": todays_date,"full": CustomerName,"stage":stage,
                "loanProducts":loanProducts,
           }
    except KeyError as e:
        print(e)
        messages.info(request, "Session Expired. Please Login")
        return redirect('auth')
    return render(request, 'calculator.html', ctx)


# Delete leave Planner Header


def Loan_Request(request):
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
    return render(request, 'loan.html', ctx)


def ApplyLoan(request):
    if request.method == 'POST':
        try:
            loanNo = request.POST.get('loanNo')
            clientCode = request.session['MemberNo']
            studentCount = int(request.POST.get('studentCount'))
            noOfTeachers = int(request.POST.get('noOfTeachers'))
            minFeesPerStudent = float(request.POST.get('minFeesPerStudent'))
            maxFeesPerStudent = float(request.POST.get('maxFeesPerStudent'))
            branchCode = request.POST.get('branchName')
            subBranchCode = request.POST.get('subBranch')
            loanProduct = request.POST.get('loanProduct')
            subProductCode = ""
            loanPurpose = request.POST.get('loanPurpose')
            appliedAmount = float(request.POST.get('appliedAmount'))
            myAction = request.POST.get('myAction')
        except ValueError as e:
            print(e)
            messages.error(request,"Missing Input")
            return redirect('loan')
        except KeyError:
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth')
        print(clientCode)
        try:
            response = config.CLIENT.service.FnLoanApplication(
                loanNo, clientCode, studentCount, noOfTeachers, minFeesPerStudent,
                maxFeesPerStudent, branchCode,subBranchCode, loanProduct,subProductCode,
                loanPurpose,appliedAmount,myAction)
            
            print(response)
            messages.success(request, "Request Successful")
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

def subProductCode(request):
    session = requests.Session()
    session.auth = config.AUTHS
    subProduct = config.O_DATA.format("/LoanSubProducts")
    LoanCode = request.GET.get('LoanCode')
    try:
        Sub_res = session.get(subProduct, timeout=10).json()
        return JsonResponse(Sub_res)

    except  Exception as e:
        pass
    return redirect('loan')


def LoanDetail(request,pk):
    try:
        CustomerName=request.session['CustomerName']
        CustomerNumber=request.session['CustomerNo']
        MemberNo=request.session['MemberNo']
        CustomerEmail=request.session['CustomerEmail']
        stage=request.session['stage']
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
            Loans = config.O_DATA.format("/Loans")
            response = session.get(Loans, timeout=10).json()
            for loan in response['value']:
                if loan['Loan_Number'] == pk:
                    Loan = loan
            ExpenseHead = config.O_DATA.format("/SchoolExpenses")
            ExpenseHeadResponse = session.get(ExpenseHead, timeout=10).json()
            Expense = ExpenseHeadResponse['value']
        except requests.exceptions.RequestException as e:
            print(e)
            messages.info(request, "Whoops! Something went wrong. Please Login to Continue")
            return redirect('auth')

        todays_date = dt.datetime.now().strftime("%b. %d, %Y %A")
        
    except KeyError:
        messages.info(request, "Session Expired. Please Login")
        return redirect('auth')

    ctx = {"today": todays_date, "loanProducts":loanProducts,
        "stage":stage, "data":res, "res":Loan,"Expense":Expense
            }
    return render(request, 'loanDetail.html', ctx)

def FnSchoolLoanRevenue(request,pk):
    if request.method == 'POST':
        try:
            entryNo = 0
            applicantNo = request.session['CustomerNo']
            edpClass = request.POST.get('edpClass')
            streams = int(request.POST.get('streams'))
            termOneFees = float(request.POST.get('termOneFees'))
            termTwoFees = float(request.POST.get('termTwoFees'))
            termThreeFees = float(request.POST.get('termThreeFees'))
            newStudentAdmission = float(request.POST.get('newStudentAdmission'))
            admissionFees = float(request.POST.get('admissionFees'))
            myAction = 'insert'
        except ValueError:
            messages.info(request,"Missing Input!")
            return redirect('LoanDetail',pk=pk)
        except KeyError:
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth')

        try:
            response = config.CLIENT.service.FnSchoolLoanRevenue(
                entryNo, applicantNo,edpClass,streams, termOneFees,termTwoFees,termThreeFees,
                newStudentAdmission,admissionFees, myAction)
            print(response)
            messages.success(request, "Successfully Added")
            return redirect('LoanDetail',pk=pk)
        except Exception as e:
            print(e)
            messages.info(request, e)
            return redirect('LoanDetail',pk=pk)
    return redirect('LoanDetail',pk=pk)

def FnSchoolLoanExpenses(request,pk):
    if request.method == 'POST':
        try:
            entryNo = 0
            applicantNo = request.session['CustomerNo']
            expenseHead = request.POST.get('expenseHead')
            monthlyExpense = float(request.POST.get('monthlyExpense'))
            multiplierFactor = float(request.POST.get('multiplierFactor'))
            myAction = 'insert'
        except ValueError:
            messages.info(request,"Missing Input!")
            return redirect('LoanDetail',pk=pk)
        except KeyError:
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth')

        try:
            response = config.CLIENT.service.FnSchoolLoanExpenses(
                entryNo, applicantNo,expenseHead,monthlyExpense,multiplierFactor,myAction)
            print(response)
            messages.success(request, "Successfully Added")
            return redirect('LoanDetail',pk=pk)
        except Exception as e:
            print(e)
            messages.info(request, e)
            return redirect('LoanDetail',pk=pk)
    return redirect('LoanDetail',pk=pk)


def FnSchoolLoanEnrolment(request,pk):
    if request.method == 'POST':
        try:
            entryNo = 0
            applicantNo = request.session['CustomerNo']
            academicYear = request.POST.get('academicYear')
            schoolStrength = request.POST.get('schoolStrength')
            myAction = request.POST.get('myAction')
        except KeyError:
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth')
        
        if academicYear.isdigit() == False:
            messages.info(request, "Academic year has to be an integer")
            return redirect('LoanDetail',pk=pk)
        try:
            response = config.CLIENT.service.FnSchoolEnrolment(
                entryNo, applicantNo, int(academicYear), schoolStrength, myAction)
            print(response)
            messages.success(request, "Successfully Added")
            return redirect('LoanDetail',pk=pk)
        except Exception as e:
            print(e)
            messages.info(request, e)
            return redirect('LoanDetail',pk=pk)
    return redirect('LoanDetail',pk=pk)


def FnSchoolLoanPassRate(request,pk):
    if request.method == 'POST':
        try:
            entryNo = 0
            applicantNo = request.session['CustomerNo']
            kcpeStudents = request.POST.get('kcpeStudents')
            passRate = request.POST.get('passRate')
            year = request.POST.get('year')
            myAction = request.POST.get('myAction')
        except ValueError:
            messages.info(request,"Missing Input!")
            return redirect('LoanDetail',pk=pk)
        except KeyError:
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth')
        if year.isdigit() == False:
            messages.info(request, "Year has to be an number")
            return redirect('LoanDetail',pk=pk)

        try:
            response = config.CLIENT.service.FnSchoolPassRate(
                entryNo, applicantNo,kcpeStudents,passRate, int(year), myAction)
            messages.success(request, "Successfully Added")
            print(response)
            return redirect('LoanDetail',pk=pk)
        except Exception as e:
            print(e)
            messages.info(request, e)
            return redirect('LoanDetail',pk=pk)
    return redirect('LoanDetail',pk=pk)


def FnSchoolLoanProjectDetails(request,pk):
    if request.method == 'POST':
        try:
            entryNo = 0
            applicantNo = request.session['CustomerNo']
            projectDescription = request.POST.get('projectDescription')
            estimatedCost = float(request.POST.get('estimatedCost'))
            costType = int(request.POST.get('costType'))
            myAction = request.POST.get('myAction')
        except ValueError:
            messages.info(request,"Missing Input!")
            return redirect('LoanDetail',pk=pk)
        except KeyError:
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth')

        try:
            response = config.CLIENT.service.FnSchoolProjectDetails(
                entryNo, applicantNo,projectDescription,estimatedCost, costType, myAction)
            print(response)
            messages.success(request, "Successfully Added")
            return redirect('LoanDetail',pk=pk)
        except Exception as e:
            print(e)
            messages.info(request, e)
            return redirect('LoanDetail',pk=pk)
    return redirect('LoanDetail',pk=pk)

def FnSchoolLoanTransportDetails(request,pk):
    if request.method == 'POST':
        try:
            entryNo = 0
            applicantNo = request.session['CustomerNo']
            transportDescription = request.POST.get('transportDescription')
            count = int(request.POST.get('count'))
            myAction = request.POST.get('myAction')
        except ValueError:
            messages.info(request,"Missing Input!")
            return redirect('LoanDetail',pk=pk)
        except KeyError:
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth')

        try:
            response = config.CLIENT.service.FnSchoolTransportDetails(
                entryNo, applicantNo,transportDescription,count,myAction)
            print(response)
            messages.success(request, "Successfully Added")
            return redirect('LoanDetail',pk=pk)
        except Exception as e:
            print(e)
            messages.info(request, e)
            return redirect('LoanDetail',pk=pk)
    return redirect('LoanDetail',pk=pk)

def FnCustomerAssets(request,pk):
    if request.method == 'POST':
        try:
            entryNo = 0
            applicantNo = request.session['CustomerNo']
            assetName = request.POST.get('assetName')
            estimatedValue = float(request.POST.get('estimatedValue'))
            assetOwner = request.POST.get('assetOwner')
            myAction = request.POST.get('myAction')
        except ValueError:
            messages.info(request,"Missing Input!")
            return redirect('LoanDetail',pk=pk)
        except KeyError:
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth')

        try:
            response = config.CLIENT.service.FnSchoolCoapplicantAssets(
                entryNo, applicantNo,assetName,estimatedValue,assetOwner,myAction)
            print(response)
            messages.success(request, "Successfully Added")
            return redirect('LoanDetail',pk=pk)
        except Exception as e:
            print(e)
            messages.info(request, e)
            return redirect('LoanDetail',pk=pk)
    return redirect('LoanDetail',pk=pk)

def FnCustomerLiabilities(request,pk):
    if request.method == 'POST':
        try:
            entryNo = 0
            applicantNo = request.session['CustomerNo']
            nameofborrower = request.POST.get('nameofborrower')
            bankName = request.POST.get('bankName')
            loanAmount = float(request.POST.get('loanAmount'))
            loanBalance = float(request.POST.get('loanBalance'))
            expectedMonthlyInstalment = request.POST.get('expectedMonthlyInstalment')
            loanTenures = request.POST.get('loanTenure')
            TenurePeriod = request.POST.get('TenurePeriod')
            balanceTenures = request.POST.get('balanceTenure')
            TenureBalancePeriod = request.POST.get('TenureBalancePeriod')
            myAction = request.POST.get('myAction')
        except ValueError:
            messages.info(request,"Missing Input!")
            return redirect('LoanDetail',pk=pk)
        except KeyError:
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth')
        loanTenure = loanTenures + TenurePeriod
        balanceTenure = balanceTenures + TenureBalancePeriod
        try:
            response = config.CLIENT.service.FnSchoolLiabilities(
                entryNo, applicantNo,nameofborrower,bankName,loanAmount,
                loanBalance,expectedMonthlyInstalment,loanTenure,balanceTenure,myAction)
            print(response)
            messages.success(request, "Successfully Added")
            return redirect('LoanDetail',pk=pk)
        except Exception as e:
            print(e)
            messages.info(request, e)
            return redirect('LoanDetail',pk=pk)
    return redirect('LoanDetail',pk=pk)

def FnCustomerCommitments(request,pk):
    if request.method == 'POST':
        try:
            entryNo = 0
            applicantNo = request.session['CustomerNo']
            nameOfProduct = request.POST.get('nameOfProduct')
            monthlyCommitment = float(request.POST.get('monthlyCommitment'))
            annualCommitment = float(request.POST.get('annualCommitment'))
            myAction = request.POST.get('myAction')
        except ValueError:
            messages.info(request,"Missing Input!")
            return redirect('LoanDetail',pk=pk)
        except KeyError:
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth')

        try:
            response = config.CLIENT.service.FnSchoolCommitments(
                entryNo, applicantNo,nameOfProduct,monthlyCommitment,
                annualCommitment,myAction)
            print(response)
            messages.success(request, "Successfully Added")
            return redirect('LoanDetail',pk=pk)
        except Exception as e:
            print(e)
            messages.info(request, e)
            return redirect('LoanDetail',pk=pk)
    return redirect('LoanDetail',pk=pk)

def FnCustomerSecurityProvided(request,pk):
    if request.method == 'POST':
        try:
            entryNo = 0
            applicantNo = request.session['CustomerNo']
            typeOfSecurity = request.POST.get('typeOfSecurity')
            available = eval(request.POST.get('available'))
            myAction = request.POST.get('myAction')
        except ValueError:
            messages.info(request,"Missing Input!")
            return redirect('LoanDetail',pk=pk)
        except KeyError:
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth')

        try:
            response = config.CLIENT.service.FnSchoolSecurityProvided(
                entryNo, applicantNo,typeOfSecurity,available,myAction)
            print(response)
            messages.success(request, "Successfully Added")
            return redirect('LoanDetail',pk=pk)
        except Exception as e:
            print(e)
            messages.info(request, e)
            return redirect('LoanDetail',pk=pk)
    return redirect('LoanDetail',pk=pk)

def FnCustomerVehicleSecurity(request,pk):
    if request.method == 'POST':
        try:
            entryNo = 0
            applicantNo = request.session['CustomerNo']
            registrationNo = request.POST.get('registrationNo')
            ownerName = request.POST.get('ownerName')
            yearOfManufacture = request.POST.get('yearOfManufacture')
            approximateValue = float(request.POST.get('yearOfManufacture'))
            myAction = request.POST.get('myAction')
        except ValueError:
            messages.info(request,"Missing Input!")
            return redirect('LoanDetail',pk=pk)
        except KeyError:
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth')

        try:
            response = config.CLIENT.service.FnSchoolVehicleSecurity(
                entryNo, applicantNo,registrationNo,ownerName,yearOfManufacture,
                approximateValue,myAction)
            print(response)
            messages.success(request, "Successfully Added")
            return redirect('LoanDetail',pk=pk)
        except Exception as e:
            print(e)
            messages.info(request, e)
            return redirect('LoanDetail',pk=pk)
    return redirect('LoanDetail',pk=pk)

def FnCustomerProjectSecurityDetails(request,pk):
    if request.method == 'POST':
        try:
            entryNo = 0
            applicantNo = request.session['CustomerNo']
            propertySecurityDetails = request.POST.get('propertySecurityDetails')
            description = request.POST.get('description')
            myAction = request.POST.get('myAction')
        except ValueError:
            messages.info(request,"Missing Input!")
            return redirect('LoanDetail',pk=pk)
        except KeyError as e:
            print(e)
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth')

        try:
            response = config.CLIENT.service.FnSchoolProjectSecurityDetails(
                entryNo, applicantNo,propertySecurityDetails,description,myAction)
            print(response)
            messages.success(request, "Successfully Added")
            return redirect('LoanDetail',pk=pk)
        except Exception as e:
            print(e)
            messages.info(request, e)
            return redirect('LoanDetail',pk=pk)
    return redirect('LoanDetail',pk=pk)

def TopUpsRequest(request):
    try:
        CustomerName=request.session['CustomerName']
        CustomerNumber=request.session['CustomerNo']
        MemberNo=request.session['MemberNo']
        CustomerEmail=request.session['CustomerEmail']
        stage=request.session['stage']

        session = requests.Session()
        session.auth = config.AUTHS
       
        Loans = config.O_DATA.format("/Loans")
        response = session.get(Loans, timeout=10).json()
        Approved = []

        for document in response['value']:
            if document['Approval_Status'] == 'Released' and document['Member_Number'] == MemberNo:
                output_json = json.dumps(document)
                Approved.append(json.loads(output_json))
        counts = len(Approved)
        todays_date = dt.datetime.now().strftime("%b. %d, %Y %A")
    except KeyError:
        messages.info(request, "Session Expired. Please Login")
        return redirect('auth')
    ctx = {"today": todays_date,"full": CustomerName,"stage":stage,
            "count": counts, "response": Approved}
    return render(request, 'topUps.html', ctx)


def FnLoanTopUp(request,pk):
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
            return redirect('LoanDetail',pk=pk)
        if not requestNo:
            requestNo = ""
        
        if not trainingNeed:
            trainingNeed = ''
        try:
            response = config.CLIENT.service.FnLoanTopUp(
                requestNo, employeeNo, usersId, isAdhoc, trainingNeed, myAction)
            messages.success(request, "Successfully Added!!")
            print(response)
        except Exception as e:
            messages.error(request, e)
            print(e)
            return redirect('LoanDetail',pk=pk)
    return redirect('LoanDetail',pk=pk)


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