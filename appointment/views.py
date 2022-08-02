from django.shortcuts import render, redirect
from datetime import date, datetime
import requests
from requests import Session
from requests_ntlm import HttpNtlmAuth
import json
from django.conf import settings as config
import datetime as dt
from django.contrib import messages
import io as BytesIO
import base64
from django.http import HttpResponse

# Create your views here.


def appointment(request):
    try:
        CustomerName=request.session['CustomerName']
        CustomerNumber=request.session['CustomerNo']
        MemberNo=request.session['MemberNo']
        CustomerEmail=request.session['CustomerEmail']
        stage=request.session['stage']
        session = requests.Session()
        session.auth = config.AUTHS
        todays_date = dt.datetime.now().strftime("%b. %d, %Y %A")
        
        Appointment = config.O_DATA.format("/Appointment")
        try:
            Response = session.get(Appointment, timeout=10).json()
            MyAppointment = [] 
            for appointment in Response['value']:
                if appointment['Client_Code'] == request.session['CustomerNo']:
                    output_json = json.dumps(appointment)
                    MyAppointment.append(json.loads(output_json))
        except requests.exceptions.RequestException as e:
            print(e)
            messages.info(request, "Whoops! Something went wrong. Please Login to Continue")
            return redirect('auth')
    except KeyError:
        messages.info(request, "Session Expired. Please Login")
        return redirect('auth') 
    countOpen = len(MyAppointment) 
    ctx = {"today": todays_date, "countOpen": countOpen,
             "full": CustomerName,"stage":stage,"appoint":MyAppointment}     
    return render(request, 'appointment.html', ctx)

def FnBookAppointment(request):
    if request.method == 'POST':
        try:
            appointmentNo = request.POST.get('appointmentNo')
            clientCode = request.session['CustomerNo']
            description = request.POST.get('description')
            appointmentDate =datetime.strptime( request.POST.get('appointmentDate'), '%Y-%m-%d').date()
            appointmentTime = datetime.strptime(request.POST.get('appointmentTime'), '%H:%M').time()
            myAction = request.POST.get('myAction')
        except ValueError:
            messages.info(request,"Missing Input!")
            return redirect('appointments')
        except KeyError:
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth')
        try:
            response = config.CLIENT.service.FnBookAppointment(
                appointmentNo, clientCode,description,appointmentDate,appointmentTime,myAction)
            print(response)
            messages.success(request, "Request Successfully Sent")
            return redirect('appointments')
        except Exception as e:
            print(e)
            messages.info(request, e)
            return redirect('appointments')
    return redirect('appointments')

def All_Approved(request, pk):
    entryNo = ''
    approvalComments = ""
   
    if request.method == 'POST':
        try:
            entryNo = int(request.POST.get('entryNo'))
            myUserID = request.session['User_ID']
            myAction = 'approve'
            documentNo = pk
        except KeyError:
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth')
        try:
            response = config.CLIENT.service.FnDocumentApproval(
                entryNo, documentNo, myUserID, approvalComments, myAction)
            messages.success(request, "Document Approval successful")
            print(response)
            return redirect('approve')
        except Exception as e:
            print(e)
            messages.info(request, e)
            return redirect('ApproveData', pk=pk)
    return redirect('ApproveData', pk=pk)


def Rejected(request, pk):
    entryNo = ''
    approvalComments = ""
    
    if request.method == 'POST':
        try:
            entryNo = int(request.POST.get('entryNo'))
            approvalComments = request.POST.get('approvalComments')
            myAction = 'reject'
            documentNo = pk
            userID = request.session['User_ID']
        except ValueError:
            messages.error(request, "Missing Input")
            return redirect('ApproveData', pk=pk)
        except KeyError:
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth')
        try:
            response = config.CLIENT.service.FnDocumentApproval(
                entryNo, documentNo, userID, approvalComments, myAction)
            messages.success(request, "Reject Document Approval successful")
            print(response)
            return redirect('approve')
        except Exception as e:
            messages.info(request, e)
            return redirect('ApproveData', pk=pk)
    return redirect('ApproveData', pk=pk)

def viewDocs(request,pk,id):
    if request.method == 'POST':
        docNo = pk
        attachmentID = int(request.POST.get('attachmentID'))
        File_Name = request.POST.get('File_Name')
        File_Extension = request.POST.get('File_Extension')
        tableID = int(id)
         
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
            return redirect('ApproveData', pk=pk)
    return redirect('ApproveData', pk=pk)