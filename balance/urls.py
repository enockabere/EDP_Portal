from os import name
from django.urls import path

from . import views

urlpatterns = [
    path("Balance/Enquiry",views.BalanceEnquiry.as_view(),name="BalanceEnquiry"),
]