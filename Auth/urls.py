from django.urls import path

from Auth import views

urlpatterns = [
    path('login', views.user_login, name='login'),
    path('signup', views.register, name='register'),
    path('', views.dashboard, name='dashboard'),
    path('contact', views.contact, name='contact'),
    path('singleproperty/<str:id>', views.singleProperty, name='singleproperty'),
    path('services', views.services, name='services'),
    path('about', views.about, name='about'),
    path('properties', views.properties, name='properties'),
    path('admin-page', views.adminPage, name='admin-page'),
    path('admin-property-management', views.adminProperty, name='admin-property-management'),
    path('admin-enquiry-management', views.enquiryProperty, name='admin-enquiry-management'),
    path('admin-agent-management', views.agentManagement, name='admin-agent-management'), 
    path('admin-teams-management', views.teamsManagement, name='admin-teams-management'),
    



    path('admin-edit-property/<int:property_id>', views.editProperty, name='edit-property'),
    path('admin-property-management/<int:property_id>', views.deleteProperty, name='delete-property'),
]