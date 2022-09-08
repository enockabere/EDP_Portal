from django.urls import path

from . import views

urlpatterns = [
    path('loan/calculator', views.Loan_Calculator.as_view(), name="Loan_Calculator"),


    path('loan/request', views.Loan_Request.as_view(), name="loan"),
    path('loan/detail/<str:pk>', views.LoanDetail.as_view(), name='LoanDetail'),
    path('FnSchoolLoanRevenue',views.FnSchoolLoanRevenue,name='FnSchoolLoanRevenue'),
    path('FnSchoolLoanExpenses',views.FnSchoolLoanExpenses,name='FnSchoolLoanExpenses'),
    path('FnSchoolLoanEnrolment',views.FnSchoolLoanEnrolment,name='FnSchoolLoanEnrolment'),
    path('FnSchoolLoanPassRate',views.FnSchoolLoanPassRate,name='FnSchoolLoanPassRate'),
    path('FnSchoolLoanProjectDetails',views.FnSchoolLoanProjectDetails,name='FnSchoolLoanProjectDetails'),
    path('FnSchoolLoanTransportDetails/<str:pk>',views.FnSchoolLoanTransportDetails,name='FnSchoolLoanTransportDetails'),
    path('FnCustomerAssets/<str:pk>',views.FnCustomerAssets,name='FnCustomerAssets'),
    path('FnCustomerLiabilities/<str:pk>',views.FnCustomerLiabilities,name='FnCustomerLiabilities'),
    path('FnCustomerCommitments/<str:pk>',views.FnCustomerCommitments,name='FnCustomerCommitments'),
    path('FnCustomerSecurityProvided/<str:pk>',views.FnCustomerSecurityProvided,name='FnCustomerSecurityProvided'),
    path('FnCustomerVehicleSecurity/<str:pk>',views.FnCustomerVehicleSecurity,name='FnCustomerVehicleSecurity'),
    path('FnCustomerProjectSecurityDetails/<str:pk>',views.FnCustomerProjectSecurityDetails,name='FnCustomerProjectSecurityDetails'),
    path('SubBranch',views.SubBranch,name='SubBranch'),
    path('subProductCode',views.subProductCode,name='subProductCode'),
    path('FnUploadAttachedDocument',views.FnUploadAttachedDocument,name='FnUploadAttachedDocument'),
    path('Loan/Repayment',views.loanRepayment.as_view(),name='repay'),
    path('loanFilter',views.loanFilter.as_view(),name='loanFilter'),
    path('Payment/Gateway/<str:pk>', views.PaymentGateway.as_view(), name='PaymentGateway'),
]
