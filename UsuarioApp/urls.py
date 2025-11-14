from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'UsuarioApp'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Login/Logout
    path('login/', auth_views.LoginView.as_view(template_name='UsuarioApp/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='UsuarioApp:login'), name='logout'),
    
    # Ejemplos de vistas protegidas
    path('admin/panel/', views.panel_administracion, name='panel_admin'),
    path('historias-clinicas/', views.historias_clinicas, name='historias_clinicas'),
    
    # Gestión de usuarios (Solo Administrador)
    path('usuarios/', views.lista_usuarios, name='lista_usuarios'),
    path('usuarios/crear/', views.crear_usuario, name='crear_usuario'),
    path('usuarios/<int:pk>/editar/', views.editar_usuario, name='editar_usuario'),
    path('usuarios/<int:pk>/ver/', views.ver_usuario, name='ver_usuario'),
    path('usuarios/<int:pk>/password/', views.cambiar_password_usuario, name='cambiar_password'),
    path('usuarios/<int:pk>/toggle/', views.toggle_usuario_activo, name='toggle_usuario'),

    # Sesión expirada
    path('sesion-expirada/', views.sesion_expirada, name='sesion_expirada'),
]
