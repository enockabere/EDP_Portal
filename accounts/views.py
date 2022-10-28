from django.shortcuts import render, HttpResponse, redirect
from django.conf import settings as config
import requests
from datetime import datetime
from django.contrib import messages
from django.http import JsonResponse
import secrets
import string
from cryptography.fernet import Fernet
import base64
from django.contrib.sites.shortcuts import get_current_site
from  django.template.loader import render_to_string
from django.core.mail import EmailMessage
import threading
import datetime as dt


def get_object(endpoint):
    session = requests.Session()
    session.auth = config.AUTHS
    response = session.get(endpoint, timeout=10).json()
    return response

def passwordCipher(password):
    Portal_Password = base64.urlsafe_b64decode(password)
    cipher_suite = Fernet(config.ENCRYPT_KEY)
    decoded_text = cipher_suite.decrypt(Portal_Password).decode("ascii")
    return decoded_text


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

def send_reset_mail(email,request):
    current_site = get_current_site(request)
    email_subject = 'Password Reset'
    email_body = render_to_string('resetMail.html',{
        'domain': current_site
    })
    reset_email = EmailMessage(subject=email_subject,body=email_body,from_email=config.EMAIL_HOST_USER,to=[email])

    EmailThread(reset_email).start()

def login_request(request):
    if request.method == 'POST':
        try:
            email = request.POST.get('email')
            password = request.POST.get('password')
        
            print(email,password)
            Customer = config.O_DATA.format(f"/CustomersList?$filter=Email_Address%20eq%20%27{email}%27")
            CustomerResponse = get_object(Customer)
            for applicant in CustomerResponse['value']:
                if applicant['Verified']==True:
                    decoded_text = passwordCipher(applicant['Password'])
                    if decoded_text == password:
                        request.session['CustomerName'] = applicant['Full_Name']
                        request.session['CustomerNo'] = applicant['No']
                        request.session['MemberNo'] = applicant['Member_Number']
                        request.session['CustomerEmail'] = applicant['Email_Address']
                        request.session['KRA_Pin'] = applicant['KRA_Pin']
                        request.session['Branch_Code'] = applicant['Branch_Code']
                        request.session['Membership_Status'] = applicant['Membership_Status']
                        request.session['MOEST_Registration_No'] = applicant['MOEST_Registration_No']
                        request.session['Mobile_Number'] = applicant['Mobile_Number']
                        request.session['stage'] = 'Customer'
                        return redirect('dashboard')
                    messages.error(request,"Incorrect Password/Username")
                    return redirect('auth')
                messages.error(request,"User not verified.")
                return redirect('auth')

            Applicant = config.O_DATA.format(f"/ApplicantsList?$filter=Email_Address%20eq%20%27{email}%27")
            ApplicantResponse = get_object(Applicant)
            for applicant in ApplicantResponse['value']:
                if applicant['Verified']==True:
                    decoded_text = passwordCipher(applicant['Password'])
                    if decoded_text == password:
                        request.session['CustomerName'] = applicant['Full_Name']
                        request.session['CustomerNo'] = applicant['No']
                        request.session['MemberNo'] = applicant['Business_Company_Reg_No']
                        request.session['CustomerEmail'] = applicant['Email_Address']
                        request.session['stage'] = 'Applicant'
                        return redirect('ApplicationDetails')
                    messages.error(request,"Incorrect Password/Username")
                    return redirect('auth')
                messages.error(request,"User not verified")
                return redirect('auth')

            Potential = config.O_DATA.format(f"/PotentialsList?$filter=Email_Address%20eq%20%27{email}%27")
            PotentialResponse = get_object(Potential)
            for applicant in PotentialResponse['value']:
                if applicant['Verified']==True:
                    decoded_text = passwordCipher(applicant['Password'])
                    if decoded_text == password:
                        request.session['CustomerName'] = applicant['Name']
                        request.session['CustomerNo'] = applicant['No']
                        request.session['MemberNo'] = applicant['Business_Company_Reg_No']
                        request.session['CustomerEmail'] = applicant['Email_Address']
                        request.session['stage'] = 'Potential'
                        return redirect('dashboard')
                    messages.error(request,"Incorrect Password/Username")
                    return redirect('auth')
                messages.error(request,"User not verified.")
                return redirect('auth')
                    
            Leads = config.O_DATA.format(f"/LeadsList?$filter=Email_Address%20eq%20%27{email}%27")
            LeadResponse = get_object(Leads)
            for lead in LeadResponse['value']:
                if lead['Verified']==True:
                    decoded_text = passwordCipher(lead['Password'])
                    if decoded_text == password:
                        request.session['CustomerName'] = lead['Name_of_the_School']
                        request.session['CustomerNo'] = lead['No']
                        request.session['MemberNo'] = lead['Business_Company_Reg_No']
                        request.session['CustomerEmail'] = lead['Email_Address']
                        request.session['stage'] = 'Lead'
                        return redirect('dashboard')
                    messages.error(request,"Incorrect Password/Username")
                    return redirect('auth')
                messages.error(request,"User not verified.")
                return redirect('auth')
            
            messages.error(request, "User not registered")
            return redirect('auth') 
        except ValueError as e:
            messages.error(request,e)
            print("Missing Input!")
            return redirect('auth')
        except requests.exceptions.ConnectionError as e:
            messages.error(request,e)
            print(e)
    return render(request, 'auth.html')

def register_request(request):
    try:
        Access_Point = config.O_DATA.format("/LeadSources")
        response = get_object(Access_Point)
        lead_source = response['value']

        EDPBranch = config.O_DATA.format("/DimensionValues?$filter=Dimension_Code%20eq%20%27BRANCH%27")
        BranchResponse = get_object(EDPBranch)
        Branch = BranchResponse['value']
    except requests.exceptions.ConnectionError as e:
        print(e)
        return redirect('register')

    ctx = {"lead_source":lead_source,"branch":Branch}
    return render(request,'register.html',ctx)

def RegisterLead(request):
    if request.method == 'POST':
        try:
            leadNo = ''
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
            myAction = 'insert'

            if len(password) < 6:
                messages.error(request, "Password should be at least 6 characters")
                return redirect('register')
            if password != password2:
                messages.error(request, "Password mismatch")
                return redirect('register')
            nameChars = ''.join(secrets.choice(string.ascii_uppercase + string.digits)
                        for i in range(5))
            verificationToken = str(nameChars)
            
            cipher_suite = Fernet(config.ENCRYPT_KEY)
            
            encrypted_text = cipher_suite.encrypt(password.encode('ascii'))
            myPassword = base64.urlsafe_b64encode(encrypted_text).decode("ascii")


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
            Access_Point = config.O_DATA.format(f"/LeadsList?$filter=Email_Address%20eq%20%27{email}%27")
            response = get_object(Access_Point)
            for res in response['value']:
                if res['Verification_Token'] == secret:
                    response = config.CLIENT.service.FnVerifyEmailAddress(email,verified)
                    print("response:",response)
                    messages.success(request,"Verification Successful")
                    return redirect('auth')
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
        del request.session['KRA_Pin']
        del request.session['Branch_Code']
        del request.session['Membership_Status']
        del request.session['MOEST_Registration_No']
        del request.session['Mobile_Number']
        messages.success(request,"Logged out successfully")
    except KeyError:
        print(False)
    return redirect('auth')

def profile(request):
    try:
        CustomerName=request.session['CustomerName']
        MOEST_Registration_No=request.session['MOEST_Registration_No']
        MemberNo=request.session['MemberNo']
        CustomerEmail=request.session['CustomerEmail']
        todays_date = dt.datetime.now().strftime("%b. %d, %Y %A")
        stage=request.session['stage']
        KRA_Pin = request.session['KRA_Pin']
        Branch_Code = request.session['Branch_Code']
        Membership_Status = request.session['Membership_Status']
        Mobile_Number = request.session['Mobile_Number']
    except KeyError:
        messages.info(request, "Session Expired. Please Login")
        return redirect('auth')
    ctx = {"today": todays_date,"full": CustomerName,"stage":stage,"MemberNo":MemberNo,
    "KRA_Pin":KRA_Pin,"Branch_Code":Branch_Code,"Membership_Status":Membership_Status,
    "CustomerEmail":CustomerEmail,"MOEST_Registration_No":MOEST_Registration_No,
    "Mobile_Number":Mobile_Number}
    return render(request,"profile.html",ctx)

def resetPassword(request):
    if request.method == 'POST':
        try:
            email = request.POST.get('email')

            Customer =config.O_DATA.format(f"/CustomersList?$filter=Email_Address%20eq%20%27{email}%27")
            CustomerResponse = get_object(Customer)
            for applicant in CustomerResponse['value']:
                if applicant['Verified']==True:
                    request.session['resetMail'] = email
                    send_reset_mail(email,request)
                    messages.success(request, 'We sent you an email to reset your password')
                    return redirect('auth')
            Applicant = config.O_DATA.format(f"/ApplicantsList?$filter=Email_Address%20eq%20%27{email}%27")
            ApplicantResponse = get_object(Applicant)
            for applicant in ApplicantResponse['value']:
                if applicant['Verified']==True:
                    request.session['resetMail'] = email
                    send_reset_mail(email,request)
                    messages.success(request, 'We sent you an email to reset your password')
                    return redirect('auth')
            Potential = config.O_DATA.format(f"/PotentialsList?$filter=Email_Address%20eq%20%27{email}%27")
            PotentialResponse = get_object(Potential)
            for applicant in PotentialResponse['value']:
                if applicant['Verified']==True:
                    request.session['resetMail'] = email
                    send_reset_mail(email,request)
                    messages.success(request, 'We sent you an email to reset your password')
                    return redirect('auth')
            Leads = config.O_DATA.format(f"/LeadsList?$filter=Email_Address%20eq%20%27{email}%27")
            LeadResponse = get_object(Leads)
            for lead in LeadResponse['value']:
                if lead['Verified']==True:
                    request.session['resetMail'] = email
                    send_reset_mail(email,request)
                    messages.success(request, 'We sent you an email to reset your password')
                    return redirect('auth')
            messages.error(request,"Invalid Email")
            return redirect('auth')
        except  ValueError:
            messages.error(request,'Missing Input')
            return redirect('login')
        except Exception as e:
            messages.error(request, e)
            print(e)
            return redirect('login')       
    return redirect("login")

def reset_request(request):
    if request.method == 'POST':
        try:
            email = request.session['resetMail']
            password = request.POST.get('password')
            password2 = request.POST.get('password2')
        
            if len(password) < 6:
                messages.error(request, "Password should be at least 6 characters")
                return redirect('reset_request')
            if password != password2:
                messages.error(request, "Password mismatch")
                return redirect('reset_request')   
            myPassword = passwordCipher(password)
            nameChars = ''.join(secrets.choice(string.ascii_uppercase + string.digits)
                            for i in range(5))

            verificationToken = str(nameChars)

            response = config.CLIENT.service.FnResetPassword(email, myPassword,verificationToken)
            print(response)
            if response == True:
                messages.success(request,"Reset successful")
                del request.session['resetMail']
                return redirect('auth')
            else:
                messages.error(request,"Error Try Again")
                return redirect('reset_request')
        except KeyError:
            messages.info(request,"Session Expired, Raise new password reset request")
            return redirect('auth')
        except  ValueError:
            messages.error(request,'Invalid Input')
            return redirect('reset_request')
        except Exception as e:
            messages.info(request, e)
            print(e)
            return redirect('reset_request')
    return render(request,'reset.html')

def testing(request):
    return render(request,"testing.html")