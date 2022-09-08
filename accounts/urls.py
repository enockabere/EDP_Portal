from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_request, name='auth'),
    path('register', views.register_request, name='register'),
    path('RegisterLead', views.RegisterLead, name='RegisterLead'),
    path('Spoke', views.Spoke, name='Spoke'),
    path('logout', views.logout, name='logout'),
    path('profile', views.profile, name='profile'),
    path("verify", views.verifyRequest,name='verify'),
    path("resetPassword", views.resetPassword,name='resetPassword'),
    path("reset/request", views.reset_request,name='reset_request'),
    path("testing", views.testing,name='testing'),
]
