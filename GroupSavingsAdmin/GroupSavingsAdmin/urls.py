from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from savings.views import (
    homepage,
    dashboard,
    register,
    create_group,
    group_detail,
    add_member,
)

urlpatterns = [
    path('', homepage, name='homepage'),  # Root URL
    path('admin/', admin.site.urls),  # Admin interface
    path('register/', register, name='register'),  # User registration
    path('login/', auth_views.LoginView.as_view(template_name='savings/login.html'), name='login'),  # Login
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),  # Logout
    path('dashboard/', dashboard, name='dashboard'),  # User dashboard
    path('group/create/', create_group, name='create_group'),  # Group creation
    path('group/<int:group_id>/', group_detail, name='group_detail'),  # Group details
    path('group/<int:group_id>/add_member/', add_member, name='add_member'),  # Add member to group
]
