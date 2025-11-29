from django.contrib import admin
from .models import Paciente, ObraSocial

@admin.register(ObraSocial)
class ObraSocialAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'codigo', 'activa']
    list_filter = ['activa']
    search_fields = ['nombre', 'codigo']
    
@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ['dni', 'apellido', 'nombre', 'telefono', 'fecha_nacimiento', 'activo', 'fecha_registro']
    list_filter = ['activo', 'sexo', 'fecha_registro']
    search_fields = ['dni', 'apellido', 'nombre', 'telefono', 'email']
    readonly_fields = ['fecha_registro', 'fecha_modificacion', 'usuario_registro']
    
    fieldsets = (
        ('Información Personal', {
            'fields': ('nombre', 'apellido', 'dni', 'fecha_nacimiento', 'sexo')
        }),
        ('Contacto', {
            'fields': ('telefono', 'email', 'direccion')
        }),
        ('Obra Social', {
            'fields': ('numero_afiliado', 'obra_social_id')
        }),
        ('Información Adicional', {
            'fields': ('observaciones', 'activo')
        }),
        ('Auditoría', {
            'fields': ('fecha_registro', 'fecha_modificacion', 'usuario_registro'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # Si es un nuevo objeto
            obj.usuario_registro = request.user
        super().save_model(request, obj, form, change)
        