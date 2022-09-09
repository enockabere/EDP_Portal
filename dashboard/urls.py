from django.urls import path
from django.urls import path
from . import views

from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('dashboard', views.Dashboard.as_view(), name="dashboard"),
    path('canvas', views.Canvas, name="canvas"),
    path('application/details', views.ApplicationDetails.as_view(), name="ApplicationDetails"),
    path('FnSchoolRevenue',views.FnSchoolRevenue,name='FnSchoolRevenue'),
    path('FnSchoolExpenses',views.FnSchoolExpenses,name='FnSchoolExpenses'),
    path('FnSchoolTransportDetails',views.FnSchoolTransportDetails,name='FnSchoolTransportDetails'),
    path('FnSchoolCoapplicantAssets',views.FnSchoolCoapplicantAssets,name='FnSchoolCoapplicantAssets'),
    path('FnSchoolLiabilities',views.FnSchoolLiabilities,name='FnSchoolLiabilities'),
    path('FnSchoolCommitments',views.FnSchoolCommitments,name='FnSchoolCommitments'),
    path('FnSchoolSecurityProvided',views.FnSchoolSecurityProvided,name='FnSchoolSecurityProvided'),
    path('FnSchoolVehicleSecurity',views.FnSchoolVehicleSecurity,name='FnSchoolVehicleSecurity'),
    path('FnSchoolProjectSecurityDetails',views.FnSchoolProjectSecurityDetails,name='FnSchoolProjectSecurityDetails'),
    path('SchoolEnrolment', views.SchoolEnrolment, name="SchoolEnrolment"),
    path('SchoolPassRate', views.SchoolPassRate, name="SchoolPassRate"),
    path('SchoolProjectDetails', views.SchoolProjectDetails, name="SchoolProjectDetails"),
    path('manual', views.Manual.as_view(), name="Manual"),
    path('UploadPotentialAttachment', views.UploadPotentialAttachment, name="UploadPotentialAttachment"),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
