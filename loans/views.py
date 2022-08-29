import base64
from curses.ascii import isdigit
from django.shortcuts import render, redirect
from datetime import  datetime
import requests
import json
from django.conf import settings as config
import datetime as dt
from django.contrib import messages
from django.http import JsonResponse
import simplejson as jsons
from django.views import View
# Create your views here.

class UserObjectMixin(object):
    model =None
    session = requests.Session()
    session.auth = config.AUTHS
    todays_date = dt.datetime.now().strftime("%b. %d, %Y %A")
    def get_object(self,endpoint):
        response = self.session.get(endpoint, timeout=10).json()
        return response

class Loan_Calculator(UserObjectMixin,View):
    def get(self,request):
        try:

            CustomerName=request.session['CustomerName']
            stage=request.session['stage']

            LoanProduct = config.O_DATA.format("/LoanProducts")
            LoanProductResponse = self.get_object(LoanProduct)
            loanProducts = LoanProductResponse['value']

            ctx = {"today": self.todays_date,"full": CustomerName,"stage":stage,
                    "loanProducts":loanProducts,
            }
        except Exception as e:
            print(e)
            messages.info(request, e)
            return redirect('Loan_Calculator')
        return render(request, 'calculator.html', ctx)
    def post(self,request):
        if request.method == 'POST':
                try:
                    calculatorType = int(request.POST.get('calculatorType'))
                    loanType =request.POST.get('loanType')
                    requestedAmount = float(request.POST.get('requestedAmount'))
                    disbursementDate =datetime.strptime( request.POST.get('disbursementDate'), '%Y-%m-%d').date()
                    repaymentStartDate = datetime.strptime(request.POST.get('repaymentStartDate'), '%Y-%m-%d').date()

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


class Loan_Request(UserObjectMixin,View):
    def get(self,request):
        try:
            CustomerName=request.session['CustomerName']
            MemberNo=request.session['MemberNo']
            stage=request.session['stage']

            Loans = config.O_DATA.format(f"/Loans?$filter=Member_Number%20eq%20%27{MemberNo}%27")
            response = self.get_object(Loans)
            openLoans = [x for x in response['value'] if x['Approval_Status'] == 'Open']
            pendingLoans = [x for x in response['value'] if x['Approval_Status'] == 'Pending Approval']
            approvedLoans = [x for x in response['value'] if x['Approval_Status'] == 'Approved']
            rejectedLoans = [x for x in response['value'] if x['Approval_Status'] == 'Disapproved']

            LoanProduct = config.O_DATA.format("/LoanProducts")
            LoanProductResponse = self.get_object(LoanProduct)
            loanProducts = LoanProductResponse['value']
                
            LoanPurposes = config.O_DATA.format("/LoanPurposes")
            LoanPurposesResponse = self.get_object(LoanPurposes)
            Purpose = LoanPurposesResponse['value']

        except requests.exceptions.RequestException as e:
            print(e)
            messages.info(request, "Whoops! Something went wrong. Please Login to Continue")
            return redirect('loan')
            
        except KeyError:
            messages.info(request, "Session Expired. Please Login")
            return redirect('loan')

        counts = len(openLoans)
        counter = len(approvedLoans)
        reject = len(rejectedLoans)
        pend = len(pendingLoans)

        ctx = {"today": self.todays_date, "loanProducts":loanProducts,
            "stage":stage, "res": openLoans,"count": counts, "response": approvedLoans,
                "counter": counter, "rej": rejectedLoans,
                'reject': reject, "pend": pend,
                "pending": pendingLoans, "Purpose":Purpose,"full":CustomerName
                }
        return render(request, 'loan.html', ctx)
    
    def post(self, request):
        if request.method == 'POST':
            try:
                loanNo = request.POST.get('loanNo')
                clientCode = request.session['MemberNo']
                studentCount = int(request.POST.get('studentCount'))
                noOfTeachers = int(request.POST.get('noOfTeachers'))
                minFeesPerStudent = float(request.POST.get('minFeesPerStudent'))
                maxFeesPerStudent = float(request.POST.get('maxFeesPerStudent'))
                loanProduct = request.POST.get('loanProduct')
                subProductCode = ""
                loanPurpose = request.POST.get('loanPurpose')
                appliedAmount = float(request.POST.get('appliedAmount'))
                myAction = request.POST.get('myAction')

                response = config.CLIENT.service.FnLoanApplication(
                    loanNo, clientCode, studentCount, noOfTeachers, minFeesPerStudent,
                    maxFeesPerStudent, loanProduct,subProductCode,
                    loanPurpose,appliedAmount,myAction)
                print(response)
                if response['return_value'] == True:
                    messages.success(request, "Request Successful")
                    return redirect('LoanDetail', pk=response['loanNo'])
            except ValueError as e:
                print(e)
                messages.error(request,"Missing Input")
                return redirect('loan')
            except KeyError:
                messages.info(request, "Session Expired. Please Login")
                return redirect('auth')
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


class LoanDetail(UserObjectMixin,View):
    def get(self,request,pk):
        try:
            CustomerName=request.session['CustomerName']
            CustomerNumber=request.session['CustomerNo']
            MemberNo=request.session['MemberNo']
            stage=request.session['stage']

            LoanProduct = config.O_DATA.format("/LoanProducts")
            LoanProductResponse = self.get_object(LoanProduct)
            loanProducts = LoanProductResponse['value']

            Applicant = config.O_DATA.format(f"/ApplicantsList?$filter=No%20eq%20%27{CustomerNumber}%27")
            ApplicantResponse = self.get_object(Applicant)
            res = [x for x in ApplicantResponse['value']]

            Loans = config.O_DATA.format(f"/Loans?$filter=Loan_Number%20eq%20%27{pk}%27")
            response = self.get_object(Loans)

            for loan in response['value']:
                loanRes=loan

            ExpenseHead = config.O_DATA.format("/SchoolExpenses")
            ExpenseHeadResponse = self.get_object(ExpenseHead)
            Expense = ExpenseHeadResponse['value']

            SchoolEnrollment = config.O_DATA.format(f"/SchoolEnrollment?$filter=Document_No%20eq%20%27{pk}%27")
            SchoolEnrollmentResponse = self.get_object(SchoolEnrollment)
            Enrollment = [x for x in SchoolEnrollmentResponse['value']]

            SchoolPassRate=config.O_DATA.format(f"/SchoolPassRate?$filter=Document_No%20eq%20%27{pk}%27")
            PassRateResponse = self.get_object(SchoolPassRate)
            PassRate = [x for x in PassRateResponse['value']]

            SchoolProjectDetails=config.O_DATA.format(f"/SchoolProjectDetails?$filter=Document_No%20eq%20%27{pk}%27")
            ProjectResponse = self.get_object(SchoolProjectDetails)
            Project = [x for x in ProjectResponse['value']]

            LoanSchoolRevenue=config.O_DATA.format(f"/LoanSchoolRevenue?$filter=Loan_No%20eq%20%27{pk}%27")
            RevenueResponse = self.get_object(LoanSchoolRevenue)
            Revenue = [x for x in RevenueResponse['value']]

            LoanSchoolExpenses=config.O_DATA.format(f"/LoanSchoolExpenses?$filter=Loan_No%20eq%20%27{pk}%27")
            RevenueResponse = self.get_object(LoanSchoolExpenses)
            Expenses = [x for x in RevenueResponse['value']]

        except requests.exceptions.RequestException as e:
            print(e)
            messages.info(request, "Whoops! Something went wrong. Please Login to Continue")
            return redirect('LoanDetail',pk=pk)
            
        except KeyError as e:
            print(e)
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth')

        ctx = {"today": self.todays_date, "loanProducts":loanProducts,
            "stage":stage, "data":res, "res":loanRes,"Expense":Expense,
             "Enrollment":Enrollment,"PassRate":PassRate,
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

            loanTenure = loanTenures + TenurePeriod
            balanceTenure = balanceTenures + TenureBalancePeriod

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
            tableID = 50140
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


class loanRepayment(UserObjectMixin,View):
    def get(self, request):
        try:
            CustomerName=request.session['CustomerName']
            MemberNo=request.session['MemberNo']
            stage=request.session['stage']

            Loans = config.O_DATA.format(f"/LoanBalances?$filter=Member_Number%20eq%20%27{MemberNo}%27")
            response = self.get_object(Loans)
            Approved=[x for x in response['value']]
        except KeyError as e:
            messages.info(request, "Session Expired. Please Login")
            print(e)
            return redirect('auth')
        except requests.exceptions.RequestException as e:
            print(e)
            messages.info(request, "Whoops! Something went wrong. Please Login to Continue")
            return redirect('auth')

        ctx = {"loans":Approved,"today": self.todays_date,"full": CustomerName,"stage":stage,}
        return render(request,"repay.html",ctx)

class loanFilter(UserObjectMixin,View):
    def get(self, request):
        try:
            MemberNo=request.session['MemberNo']
            loanNo = request.GET.get('loanNo')

            SingleLoan = config.O_DATA.format(f"/LoanBalances?$filter=Member_Number%20eq%20%27{MemberNo}%27%20and%20Loan_Number%20eq%20%27{loanNo}%27")
            LoanResponse = self.get_object(SingleLoan)
        except KeyError as e:
            messages.info(request, "Session Expired. Please Login")
            print(e)
            return redirect('auth')
        except requests.exceptions.RequestException as e:
            print(e)
            messages.info(request, "Whoops! Something went wrong. Please Login to Continue")
            return redirect('auth')
        return JsonResponse(LoanResponse)
