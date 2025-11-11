from django.contrib.auth.models import AbstractUser
from django.db import models

class Usuario(AbstractUser):
    """
    Modelo de Usuario personalizado que extiende AbstractUser
    """
    
    ROLES = [
        ('administrador', 'Administrador'),
        ('odontologo', 'Odontólogo'),
        ('recepcionista', 'Recepcionista'),
        ('auditor', 'Auditor'),
    ]
    
    rol = models.CharField(
        max_length=20,
        choices=ROLES,
        default='recepcionista',
        verbose_name='Rol del usuario'
    )
    
    telefono = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Teléfono'
    )
    
    matricula_profesional = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='Matrícula Profesional',
        help_text='Solo para odontólogos'
    )
    
    especialidad = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Especialidad',
        help_text='Solo para odontólogos'
    )
    
    foto_perfil = models.ImageField(
        upload_to='perfiles/',
        blank=True,
        null=True,
        verbose_name='Foto de perfil'
    )
    
    activo = models.BooleanField(
        default=True,
        verbose_name='Usuario activo'
    )
    
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de creación'
    )
    
    fecha_modificacion = models.DateTimeField(
        auto_now=True,
        verbose_name='Última modificación'
    )
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.get_rol_display()})"
    
    def es_administrador(self):
        return self.rol == 'administrador'
    
    def es_odontologo(self):
        return self.rol == 'odontologo'
    
    def es_recepcionista(self):
        return self.rol == 'recepcionista'
    
    def es_auditor(self):
        return self.rol == 'auditor'