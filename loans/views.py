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
from django.http import JsonResponse
import simplejson as jsons

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

                print("Month Repayment:", response)
                mp = jsons.dumps(response,use_decimal=True)
                print(type(mp))
                return JsonResponse(mp,safe=False)
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
        stage=request.session['stage']
        session = requests.Session()
        session.auth = config.AUTHS

        LoanProduct = config.O_DATA.format("/LoanProducts")
        Loans = config.O_DATA.format("/Loans?$filter=Member_Number%20eq%20%27{MemberNo}%27").format(MemberNo=MemberNo)
        try:
            response = session.get(Loans, timeout=10).json()
            openDoc = []
            Approved = []
            Rejected = []
            Pending = []
            for document in response['value']:
                if document['Approval_Status'] == 'Open':
                    output_json = json.dumps(document)
                    openDoc.append(json.loads(output_json))
                if document['Approval_Status'] == 'Approved':
                    output_json = json.dumps(document)
                    Approved.append(json.loads(output_json))
                if document['Approval_Status'] == 'Disapproved':
                    output_json = json.dumps(document)
                    Rejected.append(json.loads(output_json))
                if document['Approval_Status'] == "Pending Approval":
                    output_json = json.dumps(document)
                    Pending.append(json.loads(output_json))
            LoanProductResponse = session.get(LoanProduct, timeout=10).json()
            loanProducts = LoanProductResponse['value']
            
            LoanPurposes = config.O_DATA.format("/LoanPurposes")
            LoanPurposesResponse = session.get(LoanPurposes, timeout=10).json()
            Purpose = LoanPurposesResponse['value']
            EDPBranch = config.O_DATA.format("/DimensionValues?$filter=Dimension_Code%20eq%20%27BRANCH%27")
            BranchResponse = session.get(EDPBranch, timeout=10).json()
            Branch = []
            for branch in BranchResponse['value']:
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
            "pending": Pending, "Purpose":Purpose,"full":CustomerName
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
            if response['return_value'] == True:
                messages.success(request, "Request Successful")
                return redirect('LoanDetail', pk=response['loanNo'])
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
        stage=request.session['stage']
        session = requests.Session()
        session.auth = config.AUTHS

        LoanProduct = config.O_DATA.format("/LoanProducts")
        Applicant = config.O_DATA.format("/ApplicantsList?$filter=No%20eq%20%27{No}%27").format(No=CustomerNumber)
        Approved =[]
        try:
            LoanProductResponse = session.get(LoanProduct, timeout=10).json()
            loanProducts = LoanProductResponse['value']
            ApplicantResponse = session.get(Applicant, timeout=10).json()
            for applicant in ApplicantResponse['value']:
                    res = applicant
            Loans = config.O_DATA.format("/Loans?$filter=Loan_Number%20eq%20%27{pk}%27").format(pk=pk)
            response = session.get(Loans, timeout=10).json()
            for loan in response['value']:
                loanRes=loan
                if loan['Approval_Status'] == 'Approved' and loan['Member_Number'] == MemberNo:
                    output_json = json.dumps(loan)
                    Approved.append(json.loads(output_json))
            ExpenseHead = config.O_DATA.format("/SchoolExpenses")
            ExpenseHeadResponse = session.get(ExpenseHead, timeout=10).json()
            Expense = ExpenseHeadResponse['value']
            SchoolEnrollment = config.O_DATA.format("/SchoolEnrollment?$filter=Document_No%20eq%20%27{pk}%27").format(pk=pk)
            SchoolEnrollmentResponse = session.get(SchoolEnrollment, timeout=10).json()
            Enrollment = []
            for enroll in SchoolEnrollmentResponse['value']:
                output_json = json.dumps(enroll)
                Enrollment.append(json.loads(output_json))
            SchoolPassRate=config.O_DATA.format("/SchoolPassRate?$filter=Document_No%20eq%20%27{pk}%27").format(pk=pk)
            PassRate = []
            PassRateResponse = session.get(SchoolPassRate, timeout=10).json()
            for rate in PassRateResponse['value']:
                output_json = json.dumps(rate)
                PassRate.append(json.loads(output_json))
            SchoolProjectDetails=config.O_DATA.format("/SchoolProjectDetails?$filter=Document_No%20eq%20%27{pk}%27").format(pk=pk)
            Project = []
            ProjectResponse = session.get(SchoolProjectDetails, timeout=10).json()
            for project in ProjectResponse['value']:
                output_json = json.dumps(project)
                Project.append(json.loads(output_json))
            LoanSchoolRevenue=config.O_DATA.format("/LoanSchoolRevenue?$filter=Loan_No%20eq%20%27{pk}%27").format(pk=pk)
            Revenue = []
            RevenueResponse = session.get(LoanSchoolRevenue,timeout=10).json()
            for revenue in RevenueResponse['value']:
                output_json = json.dumps(revenue)
                Revenue.append(json.loads(output_json))
            LoanSchoolExpenses=config.O_DATA.format("/LoanSchoolExpenses?$filter=Loan_No%20eq%20%27{pk}%27").format(pk=pk)
            Expenses = []
            RevenueResponse = session.get(LoanSchoolExpenses, timeout=10).json()
            for expense in RevenueResponse['value']:
                output_json = json.dumps(expense)
                Expenses.append(json.loads(output_json))
        except requests.exceptions.RequestException as e:
            print(e)
            messages.info(request, "Whoops! Something went wrong. Please Login to Continue")
            return redirect('auth')

        todays_date = dt.datetime.now().strftime("%b. %d, %Y %A")
        
    except KeyError as e:
        print(e)
        messages.info(request, "Session Expired. Please Login")
        return redirect('auth')

    ctx = {"today": todays_date, "loanProducts":loanProducts,
        "stage":stage, "data":res, "res":loanRes,"Expense":Expense,
        "response": Approved, "Enrollment":Enrollment,"PassRate":PassRate,
        "Project":Project,"Revenue":Revenue,"Expenses":Expenses, "full":CustomerName}
    return render(request, 'loanDetail.html', ctx)

def FnSchoolLoanRevenue(request):
    if request.method == 'POST':
        try:
            entryNo = int(request.POST.get('entryNo'))
            applicantNo = request.POST.get('applicantNo')
            edpClass = request.POST.get('edpClass')
            streams = int(request.POST.get('streams'))
            termOneFees = float(request.POST.get('termOneFees'))
            termTwoFees = float(request.POST.get('termTwoFees'))
            termThreeFees = float(request.POST.get('termThreeFees'))
            newStudentAdmission = float(request.POST.get('newStudentAdmission'))
            admissionFees = float(request.POST.get('admissionFees'))
            myAction = request.POST.get('myAction')
        except KeyError:
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth')
        try:
            response = config.CLIENT.service.FnSchoolLoanRevenue(
                entryNo, applicantNo,edpClass,streams, termOneFees,termTwoFees,termThreeFees,
                newStudentAdmission,admissionFees, myAction)
            print(response)
            if response['return_value'] == True:
                messages.success(request,"Successfully Added.")
                return redirect('LoanDetail',pk=applicantNo)
        except Exception as e:
            print(e)
            messages.info(request, e)
    return redirect('LoanDetail',pk=applicantNo)

def FnSchoolLoanExpenses(request):
    if request.method == 'POST':
        try:
            entryNo = int(request.POST.get('entryNo'))
            applicantNo = request.POST.get('applicantNo')
            expenseHead = request.POST.get('expenseHead')
            monthlyExpense = float(request.POST.get('monthlyExpense'))
            multiplierFactor = float(request.POST.get('multiplierFactor'))
            myAction = request.POST.get('myAction')
        except KeyError:
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth')

        try:
            response = config.CLIENT.service.FnSchoolLoanExpenses(
                entryNo, applicantNo,expenseHead,monthlyExpense,multiplierFactor,myAction)
            print("Response:",response)
            if response['return_value'] == True:
                messages.success(request,"Successfully Added.")
                return redirect('LoanDetail',pk=applicantNo)
        except Exception as e:
            print(e)
            messages.info(request, e)
    return redirect('LoanDetail',pk=applicantNo)

def FnSchoolLoanEnrolment(request):
    if request.method == 'POST':
        entryNo = int(request.POST.get('entryNo'))
        applicantNo = request.POST.get('applicantNo')
        academicYear = request.POST.get('academicYear')
        schoolStrength = request.POST.get('schoolStrength')
        myAction = request.POST.get('myAction')
        print("entryNo:",entryNo)
        print("applicantNo:",applicantNo)
        print("academicYear:",academicYear)
        print("schoolStrength:",schoolStrength)
        print("myAction:",myAction)
        try:
            response = config.CLIENT.service.FnSchoolEnrolment(
                entryNo, applicantNo, int(academicYear), schoolStrength, myAction)
            print(response)
            if response['return_value'] == True:
                messages.success(request,"Successfully Added.")
                return redirect('LoanDetail',pk=applicantNo)
        except Exception as e:
            print(e)
            messages.info(request, e)
    return redirect('LoanDetail',pk=applicantNo)

def FnSchoolLoanPassRate(request):
    if request.method == 'POST':
        try:
            entryNo = int(request.POST.get('entryNo'))
            applicantNo = request.POST.get('applicantNo')
            kcpeStudents = request.POST.get('kcpeStudents')
            passRate = request.POST.get('passRate')
            year = request.POST.get('year')
            myAction = request.POST.get('myAction')
        except KeyError:
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth')
        try:
            response = config.CLIENT.service.FnSchoolPassRate(
                entryNo, applicantNo,kcpeStudents,passRate, int(year), myAction)
            print(response)
            if response['return_value'] == True:
                messages.success(request,"Successfully Added.")
                return redirect('LoanDetail',pk=applicantNo)
        except Exception as e:
            print(e)
            messages.info(request, e)
    return redirect('LoanDetail',pk=applicantNo)


def FnSchoolLoanProjectDetails(request):
    if request.method == 'POST':
        try:
            entryNo = int(request.POST.get('entryNo'))
            applicantNo = request.POST.get('applicantNo')
            projectDescription = request.POST.get('projectDescription')
            estimatedCost = float(request.POST.get('estimatedCost'))
            costType = int(request.POST.get('costType'))
            myAction = request.POST.get('myAction')
        except KeyError:
            messages.info(request, "Session Expired. Please Login")
            return redirect('login')
        try:
            response = config.CLIENT.service.FnSchoolProjectDetails(
                entryNo, applicantNo,projectDescription,estimatedCost, costType, myAction)
            print("Response:", response)
            if response['return_value'] == True:
                messages.success(request,"Successfully Added.")
                return redirect('LoanDetail',pk=applicantNo)
        except Exception as e:
            print(e)
            messages.info(request, e)
    return redirect('LoanDetail',pk=applicantNo)

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

def FnUploadAttachedDocument(request):
    if request.method == "POST":
        try:
            docNo = request.POST.get('docNo')
            fileName = request.FILES['attachment'].name
            attach = request.FILES.get('attachment')
            tableID = 50004
            attachment = base64.b64encode(attach.read())
            try:
                response = config.CLIENT.service.FnUploadAttachedDocument(
                    docNo, fileName, attachment, tableID)
                print("Response:",response)
                if response == True:
                    messages.success(request, "Upload Successful")
                    return redirect('LoanDetail',pk=docNo)
            except Exception as e:
                messages.error(request, e)
                print(e)
                return redirect('LoanDetail',pk=docNo)
        except Exception as e:
            print(e)
    return redirect('LoanDetail',pk=docNo)