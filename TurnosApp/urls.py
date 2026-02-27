from django.urls import path
from . import views

app_name = 'TurnosApp'

urlpatterns = [
    # Gestión de turnos
    path('', views.lista_turnos, name='lista_turnos'),
    path('crear/', views.crear_turno, name='crear_turno'),
    path('<int:pk>/editar/', views.editar_turno, name='editar_turno'),
    path('<int:pk>/ver/', views.ver_turno, name='ver_turno'),
    path('<int:pk>/confirmar/', views.confirmar_turno, name='confirmar_turno'),
    path('<int:pk>/cancelar/', views.cancelar_turno, name='cancelar_turno'),
    path('<int:pk>/iniciar/', views.iniciar_atencion, name='iniciar_atencion'),
    path('<int:pk>/finalizar/', views.finalizar_atencion, name='finalizar_atencion'),
    path('<int:pk>/ausente/', views.marcar_ausente, name='marcar_ausente'),
    
    # Configuración de agenda
    path('configuracion/', views.configuracion_agenda, name='configuracion_agenda'),
    path('configuracion/crear/', views.crear_configuracion, name='crear_configuracion'),
    path('configuracion/<int:pk>/editar/', views.editar_configuracion, name='editar_configuracion'),
    path('configuracion/<int:pk>/eliminar/', views.eliminar_configuracion, name='eliminar_configuracion'),
]