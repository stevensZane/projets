# main/urls.py - COPIEZ-CETTE VERSION :
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Pages principales
    path('', views.home, name='home'),
    path('projets/', views.project_list, name='project_list'),
    path('projets/<slug:slug>/', views.project_detail, name='project_detail'),
    path('a-propos/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    
    # APIs
    path('api/track-click/', views.track_click, name='track_click'),
    path('api/filter-data/', views.get_filter_data, name='filter_data'),
]