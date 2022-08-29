from django.shortcuts import render, redirect
from datetime import datetime
import requests
import json
from django.conf import settings as config
import datetime as dt
from django.contrib import messages
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

class appointment(UserObjectMixin,View):
    def get(self,request):
        try:
            CustomerName=request.session['CustomerName']
            CustomerNumber=request.session['CustomerNo']
            stage=request.session['stage']

            
            Appointment = config.O_DATA.format(f"/Appointment?$filter=Client_Code%20eq%20%27{CustomerNumber}%27")
            Response = self.get_object(Appointment)
            MyAppointment = [x for x in Response['value']]

        except requests.exceptions.RequestException as e:
            print(e)
            messages.info(request, "Whoops! Something went wrong. Please Login to Continue")
            return redirect('auth')
        except KeyError:
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth') 
        countOpen = len(MyAppointment) 
        ctx = {"today": self.todays_date, "countOpen": countOpen,
                "full": CustomerName,"stage":stage,"appoint":MyAppointment}     
        return render(request, 'appointment.html', ctx)
    def post(self,request):
        if request.method == 'POST':
            try:
                appointmentNo = request.POST.get('appointmentNo')
                clientCode = request.session['CustomerNo']
                description = request.POST.get('description')
                appointmentDate =datetime.strptime( request.POST.get('appointmentDate'), '%Y-%m-%d').date()
                appointmentTime = datetime.strptime(request.POST.get('appointmentTime'), '%H:%M').time()
                myAction = request.POST.get('myAction')

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



    
