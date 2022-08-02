from django.urls import path

from . import views

urlpatterns = [
    path('Loan/Top/Up',views.LoanTopUp,name='LoanTopUp'),
    path('Loan/Top/Up/Details/<str:pk>',views.LoanTopUp,name='LoanTopUp'),
]