from logging import exception
from django.http import response
from django.shortcuts import render, HttpResponse, redirect
from django.conf import settings as config
import json
import requests
from requests import Session
from requests_ntlm import HttpNtlmAuth
from datetime import date,datetime
from zeep import Client
from zeep.transports import Transport
from django.contrib import messages
from requests.auth import HTTPBasicAuth
from django.http import JsonResponse
import secrets
import string
from cryptography.fernet import Fernet
import base64
from django.contrib.sites.shortcuts import get_current_site
from  django.template.loader import render_to_string
from django.core.mail import EmailMessage
import threading
# Create your views here.

class EmailThread(threading.Thread):

    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()

def send_mail(emailAddress,verificationToken,request):
    current_site = get_current_site(request)
    email_subject = 'Activate Your Account'
    email_body = render_to_string('activate.html',{
        'domain': current_site,
        'Secret': verificationToken,
    })

    email = EmailMessage(subject=email_subject,body=email_body,
    from_email=config.EMAIL_HOST_USER,to=[emailAddress])

    EmailThread(email).start()

def login_request(request):
    session = requests.Session()
    session.auth = config.AUTHS
    if request.method == 'POST':
        try:
            email = request.POST.get('email')
            password = request.POST.get('password')
        except ValueError:
            messages.error(request,"Missing Input!")
            print("Missing Input!")
            return redirect('auth')
        print(email,password)
        Leads = config.O_DATA.format("/LeadsList")
        try:
        #     Customer = config.O_DATA.format("/CustomersList")
        #     CustomerResponse = session.get(Customer, timeout=10).json()
        #     for applicant in CustomerResponse['value']:
        #         if applicant['Email_Address'] == email and applicant['Verified']==True:
        #             Portal_Password = base64.urlsafe_b64decode(
        #                 applicant['Password'])
        #             cipher_suite = Fernet(config.ENCRYPT_KEY)
        #             try:
        #                 decoded_text = cipher_suite.decrypt(
        #                     Portal_Password).decode("ascii")
        #             except Exception as e:
        #                 print(e)
        #             if decoded_text == password:
        #                 request.session['CustomerName'] = applicant['Full_Name']
        #                 request.session['CustomerNo'] = applicant['No']
        #                 request.session['MemberNo'] = applicant['Member_Number']
        #                 request.session['CustomerEmail'] = applicant['Email_Address']
        #                 request.session['stage'] = 'Customer'
        #                 return redirect('dashboard')
        #             else:
        #                 messages.error(
        #                     request, "Invalid Credentials. Please reset your password else create a new account")
        #                 return redirect('auth')
        #     Applicant = config.O_DATA.format("/ApplicantsList")
        #     ApplicantResponse = session.get(Applicant, timeout=10).json()
        #     for applicant in ApplicantResponse['value']:
        #         if applicant['Email_Address'] == email and applicant['Verified']==True:
        #             Portal_Password = base64.urlsafe_b64decode(
        #                 applicant['Password'])
        #             cipher_suite = Fernet(config.ENCRYPT_KEY)
        #             try:
        #                 decoded_text = cipher_suite.decrypt(
        #                     Portal_Password).decode("ascii")
        #             except Exception as e:
        #                 print(e)
        #             if decoded_text == password:
        #                 request.session['CustomerName'] = applicant['Full_Name']
        #                 request.session['CustomerNo'] = applicant['No']
        #                 request.session['MemberNo'] = applicant['Business_Company_Reg_No']
        #                 request.session['CustomerEmail'] = applicant['Email_Address']
        #                 request.session['stage'] = 'Applicant'
        #                 return redirect('dashboard')
        #             else:
        #                 messages.error(
        #                     request, "Invalid Credentials. Please reset your password else create a new account")
        #                 return redirect('auth')

        #     Potential = config.O_DATA.format("/PotentialsList")
        #     PotentialResponse = session.get(Potential, timeout=10).json()
        #     for applicant in PotentialResponse['value']:
        #         if applicant['Email_Address'] == email and applicant['Verified']==True:
        #             Portal_Password = base64.urlsafe_b64decode(
        #                 applicant['Password'])
        #             cipher_suite = Fernet(config.ENCRYPT_KEY)
        #             try:
        #                 decoded_text = cipher_suite.decrypt(
        #                     Portal_Password).decode("ascii")
        #             except Exception as e:
        #                 print(e)
        #             if decoded_text == password:
        #                 request.session['CustomerName'] = applicant['Name']
        #                 request.session['CustomerNo'] = applicant['No']
        #                 request.session['MemberNo'] = applicant['Business_Company_Reg_No']
        #                 request.session['CustomerEmail'] = applicant['Email_Address']
        #                 request.session['stage'] = 'Potential'
        #                 return redirect('dashboard')
        #             else:
        #                 messages.error(
        #                     request, "Invalid Credentials. Please reset your password else create a new account")
        #                 return redirect('auth')
            
            LeadResponse = session.get(Leads, timeout=10).json()
            for lead in LeadResponse['value']:
                if lead['Email_Address'] == email:
                    Portal_Password = base64.urlsafe_b64decode(
                        lead['Password'])
                    cipher_suite = Fernet(config.ENCRYPT_KEY)
                    try:
                        decoded_text = cipher_suite.decrypt(
                            Portal_Password).decode("ascii")
                    except Exception as e:
                        print(e)
                    if decoded_text == password:
                        request.session['CustomerName'] = lead['Name_of_the_School']
                        request.session['CustomerNo'] = lead['No']
                        request.session['MemberNo'] = lead['Business_Company_Reg_No']
                        request.session['CustomerEmail'] = lead['Email_Address']
                        request.session['stage'] = 'Lead'
                        return redirect('dashboard')
                    else:
                        messages.error(
                            request, "Invalid Credentials. Please reset your password else create a new account")
                        return redirect('auth')
        except requests.exceptions.ConnectionError as e:
            messages.error(request,e)
            print(e)
    return render(request, 'auth.html')

def register_request(request):
    session = requests.Session()
    session.auth = config.AUTHS
    Access_Point = config.O_DATA.format("/LeadSources")
    EDPBranch = config.O_DATA.format("/DimensionValues")
    try:
        response = session.get(Access_Point, timeout=10).json()
        lead_source = response['value']
        BranchResponse = session.get(EDPBranch, timeout=10).json()
        
        Branch = []
        for branch in BranchResponse['value']:
            if branch['Dimension_Code'] == 'BRANCH':
                output_json = json.dumps(branch)
                Branch.append(json.loads(output_json))

    except requests.exceptions.ConnectionError as e:
        print(e)
        return redirect('register')

    ctx = {"lead_source":lead_source,"branch":Branch}
    return render(request,'register.html',ctx)

def RegisterLead(request):
    if request.method == 'POST':
        try:
            leadNo = 'CRM00423'
            schoolName = request.POST.get('schoolName')            
            leadSource = request.POST.get('leadSource')
            branchName = request.POST.get('branchName')  
            subBranch = request.POST.get('subBranch')
            typeOfOwnership = int(request.POST.get('typeOfOwnership'))
            yearSchoolStarted = datetime.strptime(request.POST.get('yearSchoolStarted'), '%Y-%m-%d').date()
            localAuthortyLicense = int(request.POST.get('localAuthortyLicense'))
            formOfRegistration = int(request.POST.get('formOfRegistration'))
            leaseAgreement = int(request.POST.get('leaseAgreement'))
            postalAddress = request.POST.get('postalAddress')
            emailAddress = request.POST.get('emailAddress')
            phoneNumber = request.POST.get('phoneNumber')
            businessNo = request.POST.get('businessNo')
            moestNo = request.POST.get('moestNo')
            premisses = int(request.POST.get('premisses'))
            coord = request.POST.get('coordinates')
            password = request.POST.get('password')
            password2 = request.POST.get('password2')
            myAction = 'modify'

            if len(password) < 6:
                messages.error(request, "Password should be at least 6 characters")
                return redirect('register')
            if password != password2:
                messages.error(request, "Password mismatch")
                return redirect('register')
            nameChars = ''.join(secrets.choice(string.ascii_uppercase + string.digits)
                        for i in range(5))
            verificationToken = str(nameChars)

            print("Token:",verificationToken)
            
            cipher_suite = Fernet(config.ENCRYPT_KEY)
            
            encrypted_text = cipher_suite.encrypt(password.encode('ascii'))
            myPassword = base64.urlsafe_b64encode(encrypted_text).decode("ascii")

            print("Password:", myPassword)

            if not coord:
                coordinates = 'None'
            
            if coord == 'True':
                url = 'https://ipinfo.io/json'
                Coo_Response = requests.get(url, timeout=10).json()
                coordinates = Coo_Response['loc']
            
            print("Coordinates:", coordinates)

            response = config.CLIENT.service.FnCreateSignUp(leadNo, schoolName, leadSource,branchName,
            subBranch,typeOfOwnership,yearSchoolStarted,localAuthortyLicense,formOfRegistration,
            leaseAgreement,postalAddress,emailAddress,phoneNumber,businessNo,moestNo,premisses,
            coordinates,myPassword,verificationToken, myAction)
            print("response:",response)
            if response:
                send_mail(emailAddress,verificationToken,request)
                messages.success(request, 'We sent you an email to verify your account')
                return redirect('auth')
        except Exception as e:
            messages.info(request,e)
            print(e)
            return redirect('register')

def verifyRequest(request):
    if request.method == 'POST':
        try:
            email = request.POST.get('email')
            secret = request.POST.get('secret')
            verified = True
        except ValueError:
            messages.error(request,'Wrong Input')
            return redirect('verify')
        session = requests.Session()
        session.auth = config.AUTHS
        Access_Point = config.O_DATA.format("/LeadsList")
        try:
            response = session.get(Access_Point, timeout=10).json()
            for res in response['value']:
                if res['Email_Address'] == email and res['Verification_Token'] == secret:
                    try:
                        response = config.CLIENT.service.FnVerifyEmailAddress(email,verified)
                        print("response:",response)
                        messages.success(request,"Verification Successful")
                        return redirect('auth')
                    except requests.exceptions.RequestException as e:
                        messages.error(request,e)
                        print(e)
                        return redirect('verify')
        except requests.exceptions.RequestException as e:
            print(e)
            messages.error(request,e)
            return redirect('verify')
    return render(request,"verify.html")

def Spoke(request):
    session = requests.Session()
    session.auth = config.AUTHS
    Item = config.O_DATA.format("/DimensionValues")
    BranchCode = request.GET.get('BranchCode')
    try:
        Item_res = session.get(Item, timeout=10).json()
        return JsonResponse(Item_res)

    except  Exception as e:
        pass
    return redirect('register')

def logout(request):
    try:
        del request.session['CustomerName']
        del request.session['CustomerNo']
        del request.session['MemberNo']
        del request.session['CustomerEmail']
        del request.session['stage']
        messages.success(request,"Logged out successfully")
    except KeyError:
        print(False)
    return redirect('auth')

def profile(request):
    return render(request,"profile.html")