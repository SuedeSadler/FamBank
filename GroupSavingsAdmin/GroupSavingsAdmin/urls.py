"""
URL configuration for GroupSavingsAdmin project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from savings.views import homepage
from savings.views import dashboard
from savings.views import register
from savings.views import create_group
from savings.views import group_detail

urlpatterns = [
    path('register/', register, name='register'),
    path('admin/', admin.site.urls),
    path('', homepage, name='homepage'),
    path('group/create/', create_group, name='create_group'),  # Add this line for group creation,
    path('group/<int:group_id>/', group_detail, name='group_detail'),
    path('login/', auth_views.LoginView.as_view(template_name='savings/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('dashboard/', dashboard, name='dashboard'),
]
