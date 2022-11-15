from django.urls import path

from knox import views as knox_views

from .api import RegisterUser, LoginAPI, GetProfileAPI

urlpatterns = [
    path('registro', RegisterUser.as_view(), name='registro'),
    path('perfil/', GetProfileAPI.as_view(), name='perfil'),
    path('login/', LoginAPI.as_view(), name='login'),
    path('logout/', knox_views.LogoutView.as_view(), name='logout'),
    path('logoutall/', knox_views.LogoutAllView.as_view(), name='logoutall'),
]
