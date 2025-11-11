from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'UsuarioApp'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Login/Logout
    path('login/', auth_views.LoginView.as_view(template_name='usuarios/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='usuarios:login'), name='logout'),
    
    # Ejemplos de vistas protegidas
    path('admin/panel/', views.panel_administracion, name='panel_admin'),
    path('historias-clinicas/', views.historias_clinicas, name='historias_clinicas'),
]