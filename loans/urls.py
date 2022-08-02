from django.urls import path

from . import views

urlpatterns = [
    path('loan/calculator', views.Loan_Calculator, name="Loan_Calculator"),


    path('loan/request', views.Loan_Request, name="loan"),
    path('loan/detail/<str:pk>', views.LoanDetail, name='LoanDetail'),
    path('FnSchoolLoanRevenue/<str:pk>',views.FnSchoolLoanRevenue,name='FnSchoolLoanRevenue'),
    path('FnSchoolLoanExpenses/<str:pk>',views.FnSchoolLoanExpenses,name='FnSchoolLoanExpenses'),
    path('FnSchoolLoanEnrolment/<str:pk>',views.FnSchoolLoanEnrolment,name='FnSchoolLoanEnrolment'),
    path('FnSchoolLoanPassRate/<str:pk>',views.FnSchoolLoanPassRate,name='FnSchoolLoanPassRate'),
    path('FnSchoolLoanProjectDetails/<str:pk>',views.FnSchoolLoanProjectDetails,name='FnSchoolLoanProjectDetails'),
    path('FnSchoolLoanTransportDetails/<str:pk>',views.FnSchoolLoanTransportDetails,name='FnSchoolLoanTransportDetails'),
    path('FnCustomerAssets/<str:pk>',views.FnCustomerAssets,name='FnCustomerAssets'),
    path('FnCustomerLiabilities/<str:pk>',views.FnCustomerLiabilities,name='FnCustomerLiabilities'),
    path('FnCustomerCommitments/<str:pk>',views.FnCustomerCommitments,name='FnCustomerCommitments'),
    path('FnCustomerSecurityProvided/<str:pk>',views.FnCustomerSecurityProvided,name='FnCustomerSecurityProvided'),
    path('FnCustomerVehicleSecurity/<str:pk>',views.FnCustomerVehicleSecurity,name='FnCustomerVehicleSecurity'),
    path('FnCustomerProjectSecurityDetails/<str:pk>',views.FnCustomerProjectSecurityDetails,name='FnCustomerProjectSecurityDetails'),
    path('ApplyLoan',views.ApplyLoan,name='ApplyLoan'),
    path('SubBranch',views.SubBranch,name='SubBranch'),
    path('subProductCode',views.subProductCode,name='subProductCode'),



    path('loan/topUp', views.TopUpsRequest, name='TopUpsRequest'),
    path('topUp/detail', views.TopUpDetail, name='TopUpDetail'),
    path('TrainApprove/<str:pk>', views.TrainingApproval, name='TrainApprove'),
    path('TrainCancel/<str:pk>', views.TrainingCancelApproval, name='TrainCancel'),
    path('FnLoanTopUp/<str:pk>', views.FnLoanTopUp,
         name='FnLoanTopUp'),
    path('FnGenerateTraining/<str:pk>', views.FnGenerateTrainingReport,
         name='FnGenerateTrainingReport'),
    path('UploadTrainingAttachment/<str:pk>', views.UploadTrainingAttachment,
         name='UploadTrainingAttachment'),

    path('FnAdhocTraining/<str:pk>', views.FnAdhocTrainingNeedRequest,
         name='FnAdhocTraining'),
    path('FnAdhocEdit/<str:pk>/<str:no>',
         views.FnAdhocTrainingEdit, name='FnAdhocEdit'),
    path('FnAdhocLineDelete/<str:pk>',
         views.FnAdhocLineDelete, name='FnAdhocLineDelete'),
    path('p9', views.PNineRequest, name='pNine'),
    path('payslip', views.PayslipRequest, name='payslip'),
    
    path('disciplinary',views.Disciplinary,name="disciplinary"),
    path('DisciplineDetails/<str:pk>', views.DisciplineDetail,
         name='DisciplineDetail'),
    path('DisciplineResponse/<str:pk>', views.DisciplinaryResponse,
         name='DisciplineResponse'),
]
