from django.urls import path
from . import views

app_name = 'PacientesApp'

urlpatterns = [
    # Lista y gestión de pacientes
    path('', views.lista_pacientes, name='lista_pacientes'),
    path('crear/', views.crear_paciente, name='crear_paciente'),
    path('<int:pk>/editar/', views.editar_paciente, name='editar_paciente'),
    path('<int:pk>/ver/', views.ver_paciente, name='ver_paciente'),
    path('<int:pk>/toggle/', views.toggle_paciente_activo, name='toggle_paciente'),
]