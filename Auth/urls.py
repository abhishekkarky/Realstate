from django.urls import path

from Auth import views

handler404 = 'Auth.views.error_view'
handler500 = 'Auth.views.error_view'

urlpatterns = [
    path('login', views.user_login, name='login'),
    path('signup', views.register, name='register'),
    path('', views.dashboard, name='dashboard'),
    path('agent-dashboard', views.agentDash, name='agent-dashboard'),
    path('contact', views.contact, name='contact'),
    path('singleproperty/<str:id>', views.singleProperty, name='singleproperty'),
    path('agentsingle/<str:id>', views.properties_booked, name='agentsingle'),
    path('services', views.services, name='services'),
    path('bookinglist', views.bookinglist, name='bookinglist'),
    path('about', views.about, name='about'),
    path('properties', views.properties, name='properties'),
    path('admin-page', views.adminPage, name='admin-page'),
    path('admin-property-management', views.adminProperty, name='admin-property-management'),
    path('admin-enquiry-management', views.enquiryProperty, name='admin-enquiry-management'),
    path('admin-agent-management', views.agentManagement, name='admin-agent-management'), 
    path('assigned-properties', views.assignedToagent, name='assigned-properties'), 
    path('admin-booking-management', views.teamsManagement, name='admin-booking-management') ,
    path('edit_agents/<int:id>/', views.edit_agents, name='edit_agents'),
    path('admin-teams-management', views.teamsManagement, name='admin-teams-management'),
    path('admin-edit-property/<int:property_id>', views.editProperty, name='edit-property'),
    path('admin-property-management/<int:property_id>', views.deleteProperty, name='delete-property'),
    path('delete-agent<int:id>', views.delete_agent, name='delete-agent'),
    path('delete-booking<int:id>', views.user_delete_booking, name='delete-booking'),
    path('admin_delete-booking<int:id>', views.admin_delete_booking, name='admin-delete-booking'),
    path('booking', views.booking, name='booking'),
    path('logout', views.user_logout, name='logout'),
    path('profile_page', views.profile, name='profile_page'),
    path('calculate_land_area', views.calculate_land_area, name='calculate_land_area'),
    path('changepassword', views.changepassword, name='changepassword'),
    path('review_agent<int:property_id>', views.review_agent, name='review_agent'),
    path('update-is-archived/<int:property_id>/', views.update_is_archived, name='update_is_archived'),

]