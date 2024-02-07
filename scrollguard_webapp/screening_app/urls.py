from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name='scrollguard-home'),
    path('demo/', views.demo, name='scrollguard-demo'),
    path('contact/', views.contact, name='scrollguard-contact'),
    path('login/', views.login, name='scrollguard-login'),
    path('screening/', views.screening, name='scrollguard-screen'),
]
