from django.urls import path

from . import views

urlpatterns = [
    path('loan/calculator', views.Loan_Calculator, name="Loan_Calculator"),


    path('loan/request', views.Loan_Request, name="loan"),
    path('loan/detail', views.LoanDetail, name='LoanDetail'),



    path('loan/topUp', views.TopUpsRequest, name='TopUpsRequest'),
    path('topUp/detail', views.TopUpDetail, name='TopUpDetail'),
    path('TrainApprove/<str:pk>', views.TrainingApproval, name='TrainApprove'),
    path('TrainCancel/<str:pk>', views.TrainingCancelApproval, name='TrainCancel'),
    path('TrainingRequest', views.CreateTrainingRequest,
         name='CreateTrainingRequest'),
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
