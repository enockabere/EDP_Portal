from django.urls import path
from . import views

urlpatterns = [
    path('appointments', views.appointment.as_view(), name="appointments"),
]
