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
# Create your views here.


def dashboard(request):
    try:
        session = requests.Session()
        session.auth = config.AUTHS
        todays_date = datetime.datetime.now().strftime("%b. %d, %Y %A")
        CustomerName=request.session['CustomerName']
        CustomerNumber=request.session['CustomerNo']
        MemberNo=request.session['MemberNo']
        CustomerEmail=request.session['CustomerEmail']
        stage=request.session['stage']
        Coordinates=request.session['Coordinates'] 

        LeadsData = config.O_DATA.format("/LeadsList")
        LeadsResponse = session.get(LeadsData, timeout=10).json()  
        for lead in LeadsResponse['value']:
            if lead['No'] == CustomerNumber and lead['Email_Address']==CustomerEmail:
                LeadRes = lead  
    except KeyError as e:
        messages.success(request, "Session Expired. Please Login")
        print(e)
        return redirect('auth') 
    except requests.exceptions.RequestException as e:
        print(e)
        messages.info(request, e)
        return redirect('auth')

    ctx = {"today": todays_date,"LeadRes": LeadRes, "full": CustomerName,
            "CustomerNumber": CustomerNumber, "CustomerEmail": CustomerEmail,
            "MemberNo": MemberNo,"stage":stage, "Coordinates":Coordinates,
            }
    return render(request, 'main/dashboard.html', ctx)

def ApplicationDetails(request):
    try:
        stage = 'application'
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
    return render(request,'main/AppDetails.html',ctx)

def FnSchoolEnrolment(request):
    if request.method == 'POST':
        try:
            entryNo = ""
            applicantNo = "000001"
            # applicantNo = request.session['CustomerNo']
            academicYear = int(request.POST.get('academicYear'))
            schoolStrength = request.POST.get('schoolStrength')
            myAction = request.POST.get('myAction')
        except ValueError:
            messages.info(request,"Missing Input!")
            return redirect('ApplicationDetails')
        except KeyError:
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth')

        try:
            response = config.CLIENT.service.FnSchoolEnrolment(
                entryNo, applicantNo, academicYear, schoolStrength, myAction)
            messages.success(request, "Successfully Added")
            print(response)
            return redirect('ApplicationDetails')
        except Exception as e:
            print(e)
            messages.info(request, e)
            return redirect('ApplicationDetails')
    return redirect('ApplicationDetails')

def FnSchoolPassRate(request):
    if request.method == 'POST':
        try:
            entryNo = ""
            applicantNo = "000001"
            # applicantNo = request.session['CustomerNo']
            kcpeStudents = request.POST.get('kcpeStudents')
            passRate = request.POST.get('passRate')
            year = int(request.POST.get('year'))
            myAction = request.POST.get('myAction')
        except ValueError:
            messages.info(request,"Missing Input!")
            return redirect('ApplicationDetails')
        except KeyError:
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth')

        try:
            response = config.CLIENT.service.FnSchoolPassRate(
                entryNo, applicantNo,kcpeStudents,passRate, year, myAction)
            messages.success(request, "Successfully Added")
            print(response)
            return redirect('ApplicationDetails')
        except Exception as e:
            print(e)
            messages.info(request, e)
            return redirect('ApplicationDetails')
    return redirect('ApplicationDetails')

def FnSchoolProjectDetails(request):
    if request.method == 'POST':
        try:
            entryNo = ""
            applicantNo = "000001"
            # applicantNo = request.session['CustomerNo']
            projectDescription = request.POST.get('projectDescription')
            estimatedCost = float(request.POST.get('estimatedCost'))
            costType = int(request.POST.get('costType'))
            myAction = request.POST.get('myAction')
        except ValueError:
            messages.info(request,"Missing Input!")
            return redirect('ApplicationDetails')
        except KeyError:
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth')

        try:
            response = config.CLIENT.service.FnSchoolProjectDetails(
                entryNo, applicantNo,projectDescription,estimatedCost, costType, myAction)
            messages.success(request, "Successfully Added")
            print(response)
            return redirect('ApplicationDetails')
        except Exception as e:
            print(e)
            messages.info(request, e)
            return redirect('ApplicationDetails')
    return redirect('ApplicationDetails')

def FnSchoolRevenue(request):
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
            return redirect('ApplicationDetails')
        except KeyError:
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth')

        try:
            response = config.CLIENT.service.FnSchoolRevenue(
                entryNo, applicantNo,edpClass,streams, termOneFees,termTwoFees,termThreeFees,
                newStudentAdmission,admissionFees, myAction)
            messages.success(request, "Successfully Added")
            print(response)
            return redirect('ApplicationDetails')
        except Exception as e:
            print(e)
            messages.info(request, e)
            return redirect('ApplicationDetails')
    return redirect('ApplicationDetails')

def FnSchoolExpenses(request):
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
            return redirect('ApplicationDetails')
        except KeyError:
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth')

        try:
            response = config.CLIENT.service.FnSchoolExpenses(
                entryNo, applicantNo,expenseHead,monthlyExpense,multiplierFactor,myAction)
            messages.success(request, "Successfully Added")
            print(response)
            return redirect('ApplicationDetails')
        except Exception as e:
            print(e)
            messages.info(request, e)
            return redirect('ApplicationDetails')
    return redirect('ApplicationDetails')

def FnSchoolTransportDetails(request):
    if request.method == 'POST':
        try:
            entryNo = ""
            applicantNo = "000001"
            # applicantNo = request.session['CustomerNo']
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
            messages.success(request, "Successfully Added")
            print(response)
            return redirect('ApplicationDetails')
        except Exception as e:
            print(e)
            messages.info(request, e)
            return redirect('ApplicationDetails')
    return redirect('ApplicationDetails')

def FnSchoolCoapplicantAssets(request):
    if request.method == 'POST':
        try:
            entryNo = ""
            applicantNo = "000001"
            # applicantNo = request.session['CustomerNo']
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
            messages.success(request, "Successfully Added")
            print(response)
            return redirect('ApplicationDetails')
        except Exception as e:
            print(e)
            messages.info(request, e)
            return redirect('ApplicationDetails')
    return redirect('ApplicationDetails')

def FnSchoolLiabilities(request):
    if request.method == 'POST':
        try:
            entryNo = ""
            applicantNo = "000001"
            # applicantNo = request.session['CustomerNo']
            nameofborrower = request.POST.get('nameofborrower')
            bankName = request.POST.get('bankName')
            loanAmount = float(request.POST.get('loanAmount'))
            loanBalance = float(request.POST.get('loanBalance'))
            expectedMonthlyInstalment = request.POST.get('expectedMonthlyInstalment')
            loanTenure = request.POST.get('loanTenure')
            balanceTenure = request.POST.get('balanceTenure')
            myAction = request.POST.get('myAction')
        except ValueError:
            messages.info(request,"Missing Input!")
            return redirect('ApplicationDetails')
        except KeyError:
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth')

        try:
            response = config.CLIENT.service.FnSchoolLiabilities(
                entryNo, applicantNo,nameofborrower,bankName,loanAmount,
                loanBalance,expectedMonthlyInstalment,loanTenure,balanceTenure,myAction)
            messages.success(request, "Successfully Added")
            print(response)
            return redirect('ApplicationDetails')
        except Exception as e:
            print(e)
            messages.info(request, e)
            return redirect('ApplicationDetails')
    return redirect('ApplicationDetails')

def FnSchoolCommitments(request):
    if request.method == 'POST':
        try:
            entryNo = ""
            applicantNo = "000001"
            # applicantNo = request.session['CustomerNo']
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
            messages.success(request, "Successfully Added")
            print(response)
            return redirect('ApplicationDetails')
        except Exception as e:
            print(e)
            messages.info(request, e)
            return redirect('ApplicationDetails')
    return redirect('ApplicationDetails')

def FnSchoolSecurityProvided(request):
    if request.method == 'POST':
        try:
            entryNo = ""
            applicantNo = "000001"
            # applicantNo = request.session['CustomerNo']
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
            messages.success(request, "Successfully Added")
            print(response)
            return redirect('ApplicationDetails')
        except Exception as e:
            print(e)
            messages.info(request, e)
            return redirect('ApplicationDetails')
    return redirect('ApplicationDetails')

def FnSchoolVehicleSecurity(request):
    if request.method == 'POST':
        try:
            entryNo = ""
            applicantNo = "000001"
            # applicantNo = request.session['CustomerNo']
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
            messages.success(request, "Successfully Added")
            print(response)
            return redirect('ApplicationDetails')
        except Exception as e:
            print(e)
            messages.info(request, e)
            return redirect('ApplicationDetails')
    return redirect('ApplicationDetails')

def FnSchoolProjectSecurityDetails(request):
    if request.method == 'POST':
        try:
            entryNo = ""
            applicantNo = "000001"
            # applicantNo = request.session['CustomerNo']
            propertySecurityDetails = request.POST.get('propertySecurityDetails')
            description = request.POST.get('description')
            myAction = request.POST.get('myAction')
        except ValueError:
            messages.info(request,"Missing Input!")
            return redirect('ApplicationDetails')
        except KeyError:
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth')

        try:
            response = config.CLIENT.service.FnSchoolProjectSecurityDetails(
                entryNo, applicantNo,propertySecurityDetails,description,myAction)
            messages.success(request, "Successfully Added")
            print(response)
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
