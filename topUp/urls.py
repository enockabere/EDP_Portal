from django.urls import path

from . import views

urlpatterns = [
    path('Loan/Top/Up',views.LoanTopUp,name='LoanTopUp'),
    path('FnLoanTopUp<str:pk>',views.FnLoanTopUp,name='FnLoanTopUp'),
]