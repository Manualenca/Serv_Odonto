from django.contrib import admin
from .models import ConfiguracionAgenda, BloqueoHorario, Turno


@admin.register(ConfiguracionAgenda)
class ConfiguracionAgendaAdmin(admin.ModelAdmin):
    list_display = ['odontologo', 'dia_semana', 'hora_inicio', 'hora_fin', 'duracion_turno', 'turnos_simultaneos', 'activo']
    list_filter = ['activo', 'dia_semana', 'odontologo']
    search_fields = ['odontologo__first_name', 'odontologo__last_name']
    ordering = ['odontologo', 'dia_semana', 'hora_inicio']


@admin.register(BloqueoHorario)
class BloqueoHorarioAdmin(admin.ModelAdmin):
    list_display = ['odontologo', 'tipo', 'fecha_inicio', 'fecha_fin', 'motivo', 'activo']
    list_filter = ['tipo', 'activo', 'fecha_inicio']
    search_fields = ['motivo', 'odontologo__first_name', 'odontologo__last_name']
    readonly_fields = ['usuario_registro', 'fecha_creacion']
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.usuario_registro = request.user
        super().save_model(request, obj, form, change)


@admin.register(Turno)
class TurnoAdmin(admin.ModelAdmin):
    list_display = ['fecha', 'hora', 'paciente', 'odontologo', 'motivo_consulta', 'estado', 'duracion']
    list_filter = ['estado', 'fecha', 'odontologo']
    search_fields = ['paciente__nombre', 'paciente__apellido', 'motivo_consulta', 'odontologo__first_name', 'odontologo__last_name']
    readonly_fields = ['usuario_registro', 'fecha_creacion', 'fecha_modificacion', 'fecha_confirmacion', 'fecha_atencion']
    date_hierarchy = 'fecha'
    
    fieldsets = (
        ('Información del Turno', {
            'fields': ('paciente', 'odontologo', 'fecha', 'hora', 'duracion')
        }),
        ('Detalles de la Consulta', {
            'fields': ('motivo_consulta', 'observaciones')
        }),
        ('Estado', {
            'fields': ('estado', 'recordatorio_enviado', 'fecha_confirmacion', 'fecha_atencion')
        }),
        ('Auditoría', {
            'fields': ('usuario_registro', 'fecha_creacion', 'fecha_modificacion'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.usuario_registro = request.user
        super().save_model(request, obj, form, change)
        