from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('add/', views.add_contact, name='add_contact'),
    path('contacts/', views.list_contacts, name='list_contacts'),
    path('send/', views.send_message, name='send_message'),
    path('login/', auth_views.LoginView.as_view(template_name='messaging/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='messaging/logout.html'), name='logout'),
    path('upload-csv/', views.upload_contacts_csv, name='upload_contacts_csv'),
    path('schedule/', views.schedule_message, name='schedule_message'),
    path('scheduled-messages/', views.list_scheduled_messages, name='list_scheduled_messages'),
    path('statistics/', views.contact_statistics, name='contact_statistics'),
    path('', views.home, name='home'),
]

