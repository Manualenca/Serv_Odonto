from django.db import models
from django.core.validators import RegexValidator
from UsuarioApp.models import Usuario

class ObraSocial(models.Model):
    """Modelo para gestionar obras sociales disponibles"""
    
    nombre = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Nombre de la Obra Social'
    )
    
    codigo = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Código',
        help_text='Código identificador de la obra social'
    )
    
    activa = models.BooleanField(
        default=True,
        verbose_name='Activa'
    )
    
    class Meta:
        verbose_name = 'Obra Social'
        verbose_name_plural = 'Obras Sociales'
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


class CategoriaAntecedente(models.Model):
    """Categorías para organizar los antecedentes médicos"""
    
    CATEGORIAS = [
        ('enfermedad_cronica', 'Enfermedad Crónica'),
        ('its', 'Infección de Transmisión Sexual'),
        ('alergia', 'Alergia'),
        ('medicacion', 'Medicación Actual'),
    ]
    
    nombre = models.CharField(
        max_length=100,
        verbose_name='Nombre'
    )
    
    categoria = models.CharField(
        max_length=20,
        choices=CATEGORIAS,
        verbose_name='Categoría'
    )
    
    descripcion = models.TextField(
        blank=True,
        null=True,
        verbose_name='Descripción',
        help_text='Información adicional sobre este antecedente'
    )
    
    requiere_precaucion = models.BooleanField(
        default=False,
        verbose_name='Requiere Precaución Especial',
        help_text='Marca si este antecedente requiere precauciones especiales en el tratamiento'
    )
    
    activo = models.BooleanField(
        default=True,
        verbose_name='Activo'
    )
    
    orden = models.IntegerField(
        default=0,
        verbose_name='Orden de visualización'
    )
    
    class Meta:
        verbose_name = 'Categoría de Antecedente'
        verbose_name_plural = 'Categorías de Antecedentes'
        ordering = ['categoria', 'orden', 'nombre']
    
    def __str__(self):
        return f"{self.nombre} ({self.get_categoria_display()})"


class AntecedentePaciente(models.Model):
    """Relación entre paciente y sus antecedentes médicos"""
    
    paciente = models.ForeignKey(
        'Paciente',
        on_delete=models.CASCADE,
        related_name='antecedentes_medicos',
        verbose_name='Paciente'
    )
    
    antecedente = models.ForeignKey(
        CategoriaAntecedente,
        on_delete=models.CASCADE,
        verbose_name='Antecedente'
    )
    
    observaciones = models.TextField(
        blank=True,
        null=True,
        verbose_name='Observaciones',
        help_text='Detalles específicos sobre este antecedente'
    )
    
    fecha_diagnostico = models.DateField(
        blank=True,
        null=True,
        verbose_name='Fecha de Diagnóstico'
    )
    
    activo = models.BooleanField(
        default=True,
        verbose_name='Activo',
        help_text='Si el antecedente está actualmente presente'
    )
    
    fecha_registro = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Registro'
    )
    
    usuario_registro = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Usuario que Registró'
    )
    
    class Meta:
        verbose_name = 'Antecedente del Paciente'
        verbose_name_plural = 'Antecedentes de los Pacientes'
        ordering = ['-activo', 'antecedente__categoria', 'antecedente__nombre']
        unique_together = ['paciente', 'antecedente']
    
    def __str__(self):
        return f"{self.paciente.get_nombre_completo()} - {self.antecedente.nombre}"


class Paciente(models.Model):
    """Modelo para gestionar información de pacientes"""
    
    SEXO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('O', 'Otro'),
    ]
    
    # Validador para DNI (solo números)
    dni_validator = RegexValidator(
        regex=r'^\d{7,8}$',
        message='El DNI debe contener entre 7 y 8 dígitos numéricos.'
    )
    
    # Validador para teléfono
    telefono_validator = RegexValidator(
        regex=r'^\d{10,15}$',
        message='El teléfono debe contener entre 10 y 15 dígitos.'
    )
    
    # Campos del paciente
    nombre = models.CharField(
        max_length=100,
        verbose_name='Nombre'
    )
    
    apellido = models.CharField(
        max_length=100,
        verbose_name='Apellido'
    )
    
    dni = models.CharField(
        max_length=8,
        unique=True,
        validators=[dni_validator],
        verbose_name='DNI',
        help_text='Documento Nacional de Identidad (7 u 8 dígitos)'
    )
    
    fecha_nacimiento = models.DateField(
        verbose_name='Fecha de Nacimiento'
    )
    
    telefono = models.CharField(
        max_length=15,
        validators=[telefono_validator],
        verbose_name='Teléfono',
        help_text='Número de contacto (10-15 dígitos)'
    )
    
    email = models.EmailField(
        blank=True,
        null=True,
        verbose_name='Email'
    )
    
    direccion = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Dirección'
    )
    
    sexo = models.CharField(
        max_length=1,
        choices=SEXO_CHOICES,
        verbose_name='Sexo'
    )
    
    numero_afiliado = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='Número de Afiliado',
        help_text='Número de obra social o prepaga'
    )
    
    obra_social = models.ForeignKey(
        ObraSocial,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='Obra Social',
        help_text='Seleccione la obra social'
    )
    
    observaciones_generales = models.TextField(
        blank=True,
        null=True,
        verbose_name='Observaciones Generales',
        help_text='Otras observaciones no categorizadas'
    )
    
    activo = models.BooleanField(
        default=True,
        verbose_name='Paciente Activo'
    )
    
    # Campos de auditoría
    fecha_registro = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Registro'
    )
    
    fecha_modificacion = models.DateTimeField(
        auto_now=True,
        verbose_name='Última Modificación'
    )
    
    usuario_registro = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        related_name='pacientes_registrados',
        verbose_name='Usuario que Registró'
    )
    
    class Meta:
        verbose_name = 'Paciente'
        verbose_name_plural = 'Pacientes'
        ordering = ['apellido', 'nombre']
        indexes = [
            models.Index(fields=['dni']),
            models.Index(fields=['apellido', 'nombre']),
        ]
    
    def __str__(self):
        return f"{self.apellido}, {self.nombre} (DNI: {self.dni})"
    
    def get_nombre_completo(self):
        """Retorna el nombre completo del paciente"""
        return f"{self.nombre} {self.apellido}"
    
    def get_edad(self):
        """Calcula la edad del paciente"""
        from datetime import date
        today = date.today()
        edad = today.year - self.fecha_nacimiento.year - (
            (today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day)
        )
        return edad
    
    def tiene_obra_social(self):
        """Verifica si el paciente tiene obra social"""
        return bool(self.numero_afiliado and self.obra_social)