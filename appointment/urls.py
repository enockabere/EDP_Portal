from django.urls import path
from . import views

urlpatterns = [
    path('appointments', views.appointment, name="appointments"),
    path('FnBookAppointment', views.FnBookAppointment, name="FnBookAppointment"),
]
