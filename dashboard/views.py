from curses.ascii import isdigit
from django.shortcuts import render, redirect
import requests
from requests import Session
from requests_ntlm import HttpNtlmAuth
import json
from django.conf import settings as config
import datetime
from django.contrib.sessions.models import Session
from django.contrib import messages
import datetime as dt
from django.http import JsonResponse
# Create your views here.


def dashboard(request):
    LeadRes = ''
    Coordinates = ''
    PotentialRes = ''
    CustomerRes =''
    try:
        session = requests.Session()
        session.auth = config.AUTHS
        todays_date = datetime.datetime.now().strftime("%b. %d, %Y %A")
        CustomerName=request.session['CustomerName']
        CustomerNumber=request.session['CustomerNo']
        MemberNo=request.session['MemberNo']
        CustomerEmail=request.session['CustomerEmail']
        stage=request.session['stage']

        LeadsData = config.O_DATA.format("/LeadsList")
        LeadsResponse = session.get(LeadsData, timeout=10).json()  
        for lead in LeadsResponse['value']:
            if lead['No'] == CustomerNumber and lead['Email_Address']==CustomerEmail:
                LeadRes = lead 
                Coordinates = lead['Coordinates'] 
        PotentialData = config.O_DATA.format("/PotentialsList")
        PotentialResponse = session.get(PotentialData, timeout=10).json()  
        for potential in PotentialResponse['value']:
            if potential['No'] == CustomerNumber and potential['Email_Address']==CustomerEmail:
                PotentialRes = potential
                Coordinates = potential['Coordinates'] 
        CustomerData = config.O_DATA.format("/CustomersList")
        CustomerResponse = session.get(CustomerData, timeout=10).json()  
        for customer in CustomerResponse['value']:
            if customer['No'] == CustomerNumber and customer['Email_Address']==CustomerEmail:
                CustomerRes = customer
        Loans = config.O_DATA.format("/Loans")
        LoanResponse = session.get(Loans, timeout=10).json()
        openDoc = []
        ApprovedLoans = []
        RejectedLoans = []
        PendingLoans = []
        for document in LoanResponse['value']:
                if document['Member_Number'] == MemberNo and document['Approval_Status'] == 'Open':
                    output_json = json.dumps(document)
                    openDoc.append(json.loads(output_json))
                if document['Member_Number'] == MemberNo and document['Approval_Status'] == 'Approved':
                    output_json = json.dumps(document)
                    ApprovedLoans.append(json.loads(output_json))
                if document['Member_Number'] == MemberNo and document['Approval_Status'] == 'Disapproved':
                    output_json = json.dumps(document)
                    RejectedLoans.append(json.loads(output_json))
                if document['Member_Number'] == MemberNo and document['Approval_Status'] == "Pending Approval":
                    output_json = json.dumps(document)
                    PendingLoans.append(json.loads(output_json))
    except KeyError as e:
        messages.success(request, "Session Expired. Please Login")
        print(e)
        return redirect('auth') 
    except requests.exceptions.RequestException as e:
        print(e)
        messages.info(request, e)
        return redirect('auth')
    openCount= len(openDoc)
    appCount = len(ApprovedLoans)
    rejCount = len(RejectedLoans)
    pendCount = len(PendingLoans)
    ctx = {"today": todays_date,"LeadRes": LeadRes, "full": CustomerName,
            "CustomerNumber": CustomerNumber, "CustomerEmail": CustomerEmail,
            "MemberNo": MemberNo,"stage":stage, "Coordinates":Coordinates,
            "PotentialRes":PotentialRes, "customer":CustomerRes,"openLoans":openCount,
            "appCount":appCount,"rejCount":rejCount,"pendCount":pendCount
            }
    return render(request, 'main/dashboard.html', ctx)

def ApplicationDetails(request):
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
        except KeyError:
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth')

        try:
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
        except KeyError:
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth')

        try:
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
        except ValueError:
            messages.info(request,"Missing Input!")
            return redirect('ApplicationDetails')
        except KeyError:
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth')

        try:
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
        except ValueError:
            messages.info(request,"Missing Input!")
            return redirect('ApplicationDetails')
        except KeyError:
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth')

        try:
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
        except ValueError:
            messages.info(request,"Missing Input!")
            return redirect('ApplicationDetails')
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
        except ValueError:
            messages.info(request,"Missing Input!")
            return redirect('ApplicationDetails')
        except KeyError:
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth')

        try:
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
        except ValueError:
            messages.info(request,"Missing Input!")
            return redirect('ApplicationDetails')
        except KeyError:
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth')

        try:
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
        except ValueError:
            messages.info(request,"Missing Input!")
            return redirect('ApplicationDetails')
        except KeyError:
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth')

        try:
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
        except ValueError:
            messages.info(request,"Missing Input!")
            return redirect('ApplicationDetails')
        except KeyError as e:
            print(e)
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth')

        try:
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
        except KeyError:
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth')
        try:
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
        except KeyError:
            messages.info(request, "Session Expired. Please Login")
            return redirect('login')
        try:
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