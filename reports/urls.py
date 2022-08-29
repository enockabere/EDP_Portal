from django.urls import path

from . import views

urlpatterns = [
    path("Reports",views.Reports.as_view(),name="Reports"),
    path("FnDetailedCustomerReport",views.FnDetailedCustomerReport,name="FnDetailedCustomerReport"),
    path("FnLoanStatementReport",views.FnLoanStatementReport,name="FnLoanStatementReport"),
    path("FnLoanRepaymentScheduleReport",views.FnLoanRepaymentScheduleReport,name="FnLoanRepaymentScheduleReport"),
    path("FnCalculatorScheduleReport",views.FnCalculatorScheduleReport,name="FnCalculatorScheduleReport"),
]