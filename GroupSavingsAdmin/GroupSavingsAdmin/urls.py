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
    send_invitation,
    respond_invitation,
)

urlpatterns = [
       path('register/', register, name='register'),
    path('admin/', admin.site.urls),
    path('', homepage, name='homepage'),
    path('group/create/', create_group, name='create_group'),
    path('group/<int:group_id>/', group_detail, name='group_detail'),
    path('group/<int:group_id>/add_member/', add_member, name='add_member'),
    path('group/<int:group_id>/send_invitation/', send_invitation, name='send_invitation'),
    path('invitations/respond/<int:invitation_id>/', respond_invitation, name='respond_invitation'),
    path('login/', auth_views.LoginView.as_view(template_name='savings/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('dashboard/', dashboard, name='dashboard'),
]
