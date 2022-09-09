from curses.ascii import isdigit
from django.shortcuts import render, redirect
import requests
from requests import Session
from requests_ntlm import HttpNtlmAuth
import json
from django.conf import settings as config
from datetime import date,datetime
from django.contrib.sessions.models import Session
from django.contrib import messages
import datetime as dt
from django.http import JsonResponse
from django.views import View
import base64
from django.http import HttpResponse
import io as BytesIO
# Create your views here.

class UserObjectMixin(object):
    model =None
    session = requests.Session()
    session.auth = config.AUTHS
    todays_date = dt.datetime.now().strftime("%b. %d, %Y %A")
    def get_object(self,endpoint):
        response = self.session.get(endpoint, timeout=10).json()
        return response
class Dashboard(UserObjectMixin,View):
    def get(self,request):
        allFiles = []
        try:
            CustomerName=request.session['CustomerName']
            CustomerNumber=request.session['CustomerNo']
            MemberNo=request.session['MemberNo']
            CustomerEmail=request.session['CustomerEmail']
            stage=request.session['stage']
            LeadRes =''
            PotentialRes = ''
            CustomerRes = ''
            Coordinates = ''
            nextDueDate = ''

            LeadsData = config.O_DATA.format(f"/LeadsList?$filter=No%20eq%20%27{CustomerNumber}%27%20and%20Email_Address%20eq%20%27{CustomerEmail}%27")
            LeadsResponse = self.get_object(LeadsData) 
            for lead in LeadsResponse['value']:
                LeadRes = lead 
                Coordinates = lead['Coordinates'] 

            PotentialData = config.O_DATA.format(f"/PotentialsList?$filter=No%20eq%20%27{CustomerNumber}%27%20and%20Email_Address%20eq%20%27{CustomerEmail}%27")
            PotentialResponse = self.get_object(PotentialData) 
            for potential in PotentialResponse['value']:
                PotentialRes = potential
                Coordinates = potential['Coordinates'] 
                Access_File = config.O_DATA.format(f"/AttachedDocuments?$filter=No%20eq%20%27{potential['No']}%27")
                res_file = self.get_object(Access_File)
                allFiles = [x for x in res_file['value']]

            CustomerData = config.O_DATA.format(f"/CustomersList?$filter=No%20eq%20%27{CustomerNumber}%27%20and%20Email_Address%20eq%20%27{CustomerEmail}%27")
            CustomerResponse = self.get_object(CustomerData) 
            for customer in CustomerResponse['value']:
                CustomerRes = customer

            Loans = config.O_DATA.format(f"/Loans?$filter=Member_Number%20eq%20%27{MemberNo}%27")
            LoanResponse = self.get_object(Loans)
            openCount = len([x for x in LoanResponse['value'] if x['Approval_Status'] == 'Open'])
            pendCount = len([x for x in LoanResponse['value'] if x['Approval_Status'] == 'Pending Approval'])
            appCount = len([x for x in LoanResponse['value'] if x['Approval_Status'] == 'Approved'])
            rejCount = len([x for x in LoanResponse['value'] if x['Approval_Status'] == 'Disapproved'])

            Loans = config.O_DATA.format(f"/LoanBalances?$filter=Member_Number%20eq%20%27{MemberNo}%27")
            myResponse = self.get_object(Loans)
            loanBalance = 0
            amountDue = 0
            DaysInArrears = 0
            today = date.today()
            test_date_list = []
            for balances in myResponse['value']:
                loanBalance += int(balances['Outstanding_Balance'])
                amountDue += int(balances['Total_Payable_Amount'])
                DaysInArrears += int(balances['Days_in_Arrears'])
                dates = test_date_list.append(datetime.strptime(balances['Due_Date'], '%Y-%m-%d').date())
            res = min(test_date_list, key=lambda sub: abs(sub - today))
        
            nextDueDate=str(res)
        except KeyError as e:
            messages.success(request, "Session Expired. Please Login")
            print(e)
            return redirect('auth') 
        except requests.exceptions.RequestException as e:
            print(e)
            messages.info(request, e)
            return redirect('auth')
        except ValueError:
            pass

        ctx = {"today": self.todays_date,"LeadRes": LeadRes, "full": CustomerName,
                "CustomerNumber": CustomerNumber, "CustomerEmail": CustomerEmail,
                "MemberNo": MemberNo,"stage":stage, "Coordinates":Coordinates,
                "PotentialRes":PotentialRes, "customer":CustomerRes,"openLoans":openCount,
                "appCount":appCount,"rejCount":rejCount,"pendCount":pendCount,
                "loanBalance":loanBalance,"amountDue":amountDue,"DaysInArrears":DaysInArrears,
                "nextDueDate":nextDueDate,"file":allFiles
                }
        return render(request, 'main/dashboard.html', ctx)

def FnPotentialLoanAmount(request):
    if request.method == "POST":
        docNo = request.POST.get('docNo')
        loanAmount= float(request.POST.get('loanAmount'))
        try:
            response = config.CLIENT.service.FnPotentialLoanAmount(
                docNo,loanAmount)
            print(response)
            return redirect('dashboard')
            if response == True:
                messages.success(request, "Sent Successfully ")
                return redirect('dashboard')
        except Exception as e:
            messages.error(request, e)
            print(e)
    return redirect('dashboard')

def UploadPotentialAttachment(request):
    if request.method == "POST":
        try:
            docNo = request.POST.get('docNo')
            attach = request.FILES.get('attachment')
            filename = request.FILES['attachment'].name
            documentType = int(request.POST.get('documentType'))
            tableID = 50401
            attachment = base64.b64encode(attach.read())

            try:
                response = config.CLIENT.service.FnUploadAttachedDocument(
                    docNo, filename,attachment,documentType, tableID)
                print(response)
                if response == True:
                    messages.success(request, "Upload Successful")
                    return redirect('dashboard')
                else:
                    messages.error(request, "Failed, Try Again")
                    return redirect('dashboard')
            except Exception as e:
                messages.error(request, e)
                print(e)
                return redirect('dashboard')
        except Exception as e:
            print(e)        
    return redirect('dashboard')


def DeleteAttachment(request,pk):
    if request.method == "POST":

        attachmentID = int(request.POST.get('attachmentID'))
        tableID= int(request.POST.get('tableID'))
        docID = request.POST.get('docID')
        try:
            response = config.CLIENT.service.FnDeleteDocumentAttachment(
                attachmentID,docID,tableID)
            print(response)
            if response == True:
                messages.success(request, "Deleted Successfully ")
                return redirect('dashboard')
        except Exception as e:
            messages.error(request, e)
            print(e)
    return redirect('dashboard')

def viewDocs(request):
    if request.method == 'POST':
        docNo = request.POST.get('docNo')
        attachmentID = int(request.POST.get('attachmentID'))
        File_Name = request.POST.get('File_Name')
        File_Extension = request.POST.get('File_Extension')
        tableID = int(request.POST.get('tableID'))

        try:
            response = config.CLIENT.service.FnGetDocumentAttachment(
                docNo, attachmentID, tableID)
            
            filenameFromApp = File_Name + "." + File_Extension
            buffer = BytesIO.BytesIO()
            content = base64.b64decode(response)
            buffer.write(content)
            responses = HttpResponse(
                buffer.getvalue(),
                content_type="application/ms-excel",
            )
            responses['Content-Disposition'] = f'inline;filename={filenameFromApp}'
            return responses
        except Exception as e:
            messages.info(request, e)
            return redirect('dashboard')
    return redirect('dashboard')

class ApplicationDetails(UserObjectMixin,View):
    def get(self,request):
        try:
            CustomerName=request.session['CustomerName']
            CustomerNumber=request.session['CustomerNo']
            stage=request.session['stage']

            LoanProduct = config.O_DATA.format("/LoanProducts")
            LoanProductResponse = self.get_object(LoanProduct)
            loanProducts = LoanProductResponse['value']

            Applicant = config.O_DATA.format(f"/ApplicantsList?$filter=No%20eq%20%27{CustomerNumber}%27")
            ApplicantResponse = self.get_object(Applicant)
            res = [x for x in ApplicantResponse['value']]

            ExpenseHead = config.O_DATA.format("/SchoolExpenses")
            ExpenseHeadResponse = self.get_object(ExpenseHead)
            Expense = ExpenseHeadResponse['value']                
        except requests.exceptions.RequestException as e:
            print(e)
            messages.info(request, "Whoops! Something went wrong. Please Login to Continue")
            return redirect('auth')
            
        except KeyError:
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth')

        ctx = {"today": self.todays_date, "loanProducts":loanProducts,
            "stage":stage, "data":res,"full": CustomerName,"Expense":Expense,
                }
        return render(request,'main/AppDetails.html',ctx)



def FnSchoolRevenue(request):
    if request.method == 'POST':
        try:
            entryNo = 0
            applicantNo = request.session['CustomerNo']
            edpClass = request.POST.get('edpClass')
            streams = request.POST.get('streams')
            termOneFees = float(request.POST.get('termOneFees'))
            termTwoFees = float(request.POST.get('termTwoFees'))
            termThreeFees = float(request.POST.get('termThreeFees'))
            newStudentAdmission = float(request.POST.get('newStudentAdmission'))
            admissionFees = float(request.POST.get('admissionFees'))
            myAction = 'insert'

            response = config.CLIENT.service.FnSchoolRevenue(
                entryNo, applicantNo,edpClass,streams, termOneFees,termTwoFees,termThreeFees,
                newStudentAdmission,admissionFees, myAction)
            print(response)
            if response['return_value'] == True:
                messages.success(request,"Successfully Added.")
                return redirect('ApplicationDetails')
            if response['return_value'] == False:
                messages.error(request,"Not Added.")
                return redirect('ApplicationDetails')
        except Exception as e:
            print(e)
            messages.info(request, e)
    return redirect('ApplicationDetails')

def FnSchoolExpenses(request):
    if request.method == 'POST':
        try:
            entryNo = 0
            applicantNo = request.session['CustomerNo']
            expenseHead = request.POST.get('expenseHead')
            monthlyExpense = float(request.POST.get('monthlyExpense'))
            multiplierFactor = float(request.POST.get('multiplierFactor'))
            myAction = 'insert'

            response = config.CLIENT.service.FnSchoolExpenses(
                entryNo, applicantNo,expenseHead,monthlyExpense,multiplierFactor,myAction)
            print(response)
            if response['return_value'] == True:
                messages.success(request,"Successfully Added.")
                return redirect('ApplicationDetails')
            if response['return_value'] == False:
                messages.error(request,"Not Added.")
                return redirect('ApplicationDetails')
        except Exception as e:
            print(e)
            messages.info(request, e)
    return redirect('ApplicationDetails')

def FnSchoolTransportDetails(request):
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
            return redirect('ApplicationDetails')
        except Exception as e:
            print(e)
            messages.info(request, e)
            return redirect('ApplicationDetails')
    return redirect('ApplicationDetails')

def FnSchoolCoapplicantAssets(request):
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
            return redirect('ApplicationDetails')
        except Exception as e:
            print(e)
            messages.info(request, e)
            return redirect('ApplicationDetails')
    return redirect('ApplicationDetails')

def FnSchoolLiabilities(request):
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
            return redirect('ApplicationDetails')
        except Exception as e:
            print(e)
            messages.info(request, e)
            return redirect('ApplicationDetails')
    return redirect('ApplicationDetails')

def FnSchoolCommitments(request):
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
            return redirect('ApplicationDetails')
        except Exception as e:
            print(e)
            messages.info(request, e)
            return redirect('ApplicationDetails')
    return redirect('ApplicationDetails')

def FnSchoolSecurityProvided(request):
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
            return redirect('ApplicationDetails')
        except Exception as e:
            print(e)
            messages.info(request, e)
            return redirect('ApplicationDetails')
    return redirect('ApplicationDetails')

def FnSchoolVehicleSecurity(request):
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
            return redirect('ApplicationDetails')
        except Exception as e:
            print(e)
            messages.info(request, e)
            return redirect('ApplicationDetails')
    return redirect('ApplicationDetails')

def FnSchoolProjectSecurityDetails(request):
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
            return redirect('ApplicationDetails')
        except Exception as e:
            print(e)
            messages.info(request, e)
            return redirect('ApplicationDetails')
    return redirect('ApplicationDetails')


def Canvas(request):

    fullname =  request.session['User_ID']
    ctx = {"fullname": fullname}
    return render(request, "offcanvas.html", ctx)

def SchoolEnrolment(request):
    if request.method == 'POST':
        entryNo = 0
        applicantNo =  request.session['CustomerNo']
        academicYear = request.POST.get('academicYear')
        schoolStrength = request.POST.get('schoolStrength')
        myAction = 'insert'
        try:
            response = config.CLIENT.service.FnSchoolEnrolment(
                entryNo, applicantNo, int(academicYear), schoolStrength, myAction)
            print(response)
            if response['return_value'] == True:
                messages.success(request,"Successfully Added.")
                return redirect('ApplicationDetails')
            if response['return_value'] == False:
                messages.error(request,"Not Added.")
                return redirect('ApplicationDetails')
        except Exception as e:
            print(e)
            messages.info(request, e)
    return redirect('ApplicationDetails')

def SchoolPassRate(request):
    if request.method == 'POST':
        try:
            entryNo = 0
            applicantNo = request.session['CustomerNo']
            kcpeStudents = request.POST.get('kcpeStudents')
            passRate = request.POST.get('passRate')
            year = request.POST.get('year')
            myAction = 'insert'

            response = config.CLIENT.service.FnSchoolPassRate(
                entryNo, applicantNo,kcpeStudents,passRate, int(year), myAction)
            print(response)
            if response['return_value'] == True:
                messages.success(request,"Successfully Added.")
                return redirect('ApplicationDetails')
            if response['return_value'] == False:
                messages.error(request,"Not Added.")
                return redirect('ApplicationDetails')
        except Exception as e:
            print(e)
            messages.info(request, e)
    return redirect('ApplicationDetails')

def SchoolProjectDetails(request):
    if request.method == 'POST':
        try:
            entryNo = 0
            applicantNo = request.session['CustomerNo']
            projectDescription = request.POST.get('projectDescription')
            estimatedCost = float(request.POST.get('estimatedCost'))
            costType = int(request.POST.get('costType'))
            myAction = 'insert'
        
            response = config.CLIENT.service.FnSchoolProjectDetails(
                entryNo, applicantNo,projectDescription,estimatedCost, costType, myAction)
            if response['return_value'] == True:
                messages.success(request,"Successfully Added.")
                return redirect('ApplicationDetails')
            if response['return_value'] == False:
                messages.error(request,"Not Added.")
                return redirect('ApplicationDetails')
        except Exception as e:
            print(e)
            messages.info(request, e)
    return redirect('ApplicationDetails')

class Manual(UserObjectMixin,View):
    def get(self, request):
        try:
            CustomerName=request.session['CustomerName']
            MemberNo=request.session['MemberNo']
            stage=request.session['stage']
        except KeyError as e:
            messages.info(request, "Session Expired. Please Login")
            print(e)
            return redirect('auth')
        ctx = {"today": self.todays_date,"full": CustomerName,"stage":stage,}
        return render(request,"manual.html",ctx)
