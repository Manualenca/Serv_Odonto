from django.contrib import admin
from .models import Paciente, ObraSocial, CategoriaAntecedente, AntecedentePaciente

@admin.register(CategoriaAntecedente)
class CategoriaAntecedenteAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'categoria', 'requiere_precaucion', 'activo', 'orden']
    list_filter = ['categoria', 'requiere_precaucion', 'activo']
    search_fields = ['nombre', 'descripcion']
    ordering = ['categoria', 'orden', 'nombre']

@admin.register(AntecedentePaciente)
class AntecedentePacienteAdmin(admin.ModelAdmin):
    list_display = ['paciente', 'antecedente', 'activo', 'fecha_registro']
    list_filter = ['activo', 'antecedente__categoria', 'fecha_registro']
    search_fields = ['paciente__nombre', 'paciente__apellido', 'antecedente__nombre']
    readonly_fields = ['fecha_registro', 'usuario_registro']
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.usuario_registro = request.user
        super().save_model(request, obj, form, change)

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
            'fields': ('numero_afiliado', 'obra_social')
        }),
        ('Información Adicional', {
            'fields': ('observaciones_generales', 'activo')
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