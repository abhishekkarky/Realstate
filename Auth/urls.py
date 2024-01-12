from django.urls import path
from Auth import views


urlpatterns = [
    path('login', views.user_login, name='login'),
    path('signup', views.register, name='register'),
    path('', views.dashboard, name='dashboard'),
    path('contact', views.contact, name='contact'),
    path('singleproperty', views.singleProperty, name='singleproperty'),
    path('services', views.services, name='services'),
    path('about', views.about, name='about'),
    path('properties', views.properties, name='properties')
]