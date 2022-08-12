from django.urls import path
from django.urls import path
from . import views

from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('dashboard', views.dashboard, name="dashboard"),
    path('canvas', views.Canvas, name="canvas"),
    path('application/details', views.ApplicationDetails, name="ApplicationDetails"),
    path('FnSchoolRevenue',views.FnSchoolRevenue,name='FnSchoolRevenue'),
    path('FnSchoolExpenses',views.FnSchoolExpenses,name='FnSchoolExpenses'),
    path('FnSchoolTransportDetails',views.FnSchoolTransportDetails,name='FnSchoolTransportDetails'),
    path('FnSchoolCoapplicantAssets',views.FnSchoolCoapplicantAssets,name='FnSchoolCoapplicantAssets'),
    path('FnSchoolLiabilities',views.FnSchoolLiabilities,name='FnSchoolLiabilities'),
    path('FnSchoolCommitments',views.FnSchoolCommitments,name='FnSchoolCommitments'),
    path('FnSchoolSecurityProvided',views.FnSchoolSecurityProvided,name='FnSchoolSecurityProvided'),
    path('FnSchoolVehicleSecurity',views.FnSchoolVehicleSecurity,name='FnSchoolVehicleSecurity'),
    path('FnSchoolProjectSecurityDetails',views.FnSchoolProjectSecurityDetails,name='FnSchoolProjectSecurityDetails'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
