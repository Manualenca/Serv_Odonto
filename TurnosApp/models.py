from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from UsuarioApp.models import Usuario
from PacientesApp.models import Paciente
from datetime import time, datetime, timedelta


class ConfiguracionAgenda(models.Model):
    """Configuración de horarios de atención por odontólogo"""
    
    DIAS_SEMANA = [
        (0, 'Lunes'),
        (1, 'Martes'),
        (2, 'Miércoles'),
        (3, 'Jueves'),
        (4, 'Viernes'),
        (5, 'Sábado'),
        (6, 'Domingo'),
    ]
    
    odontologo = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        limit_choices_to={'rol': 'odontologo'},
        related_name='configuraciones_agenda',
        verbose_name='Odontólogo'
    )
    
    dia_semana = models.IntegerField(
        choices=DIAS_SEMANA,
        verbose_name='Día de la Semana'
    )
    
    hora_inicio = models.TimeField(
        verbose_name='Hora de Inicio'
    )
    
    hora_fin = models.TimeField(
        verbose_name='Hora de Fin'
    )
    
    duracion_turno = models.IntegerField(
        default=30,
        validators=[MinValueValidator(15), MaxValueValidator(120)],
        verbose_name='Duración del Turno (minutos)',
        help_text='Entre 15 y 120 minutos'
    )
    
    turnos_simultaneos = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='Turnos Simultáneos',
        help_text='Cantidad de pacientes que puede atender al mismo tiempo'
    )
    
    activo = models.BooleanField(
        default=True,
        verbose_name='Activo'
    )
    
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )
    
    fecha_modificacion = models.DateTimeField(
        auto_now=True,
        verbose_name='Última Modificación'
    )
    
    class Meta:
        verbose_name = 'Configuración de Agenda'
        verbose_name_plural = 'Configuraciones de Agenda'
        ordering = ['odontologo', 'dia_semana', 'hora_inicio']
        unique_together = ['odontologo', 'dia_semana', 'hora_inicio']
    
    def __str__(self):
        return f"{self.odontologo.get_full_name()} - {self.get_dia_semana_display()} {self.hora_inicio.strftime('%H:%M')} a {self.hora_fin.strftime('%H:%M')}"
    
    def clean(self):
        """Validar que la hora de fin sea posterior a la hora de inicio"""
        if self.hora_fin <= self.hora_inicio:
            raise ValidationError('La hora de fin debe ser posterior a la hora de inicio.')
    
    def get_horarios_disponibles(self):
        """Retorna lista de horarios disponibles según la configuración"""
        horarios = []
        hora_actual = datetime.combine(datetime.today(), self.hora_inicio)
        hora_fin = datetime.combine(datetime.today(), self.hora_fin)
        
        while hora_actual < hora_fin:
            horarios.append(hora_actual.time())
            hora_actual += timedelta(minutes=self.duracion_turno)
        
        return horarios


class BloqueoHorario(models.Model):
    """Bloqueo de horarios por feriados, vacaciones, ausencias, etc."""
    
    TIPO_BLOQUEO = [
        ('feriado', 'Feriado'),
        ('vacaciones', 'Vacaciones'),
        ('ausencia', 'Ausencia'),
        ('otro', 'Otro'),
    ]
    
    odontologo = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        limit_choices_to={'rol': 'odontologo'},
        related_name='bloqueos_horario',
        verbose_name='Odontólogo',
        null=True,
        blank=True,
        help_text='Dejá vacío para bloqueo general (afecta a todos)'
    )
    
    fecha_inicio = models.DateField(
        verbose_name='Fecha de Inicio'
    )
    
    fecha_fin = models.DateField(
        verbose_name='Fecha de Fin'
    )
    
    hora_inicio = models.TimeField(
        null=True,
        blank=True,
        verbose_name='Hora de Inicio',
        help_text='Dejá vacío para bloquear todo el día'
    )
    
    hora_fin = models.TimeField(
        null=True,
        blank=True,
        verbose_name='Hora de Fin',
        help_text='Dejá vacío para bloquear todo el día'
    )
    
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_BLOQUEO,
        default='otro',
        verbose_name='Tipo de Bloqueo'
    )
    
    motivo = models.CharField(
        max_length=200,
        verbose_name='Motivo',
        help_text='Ej: Feriado Nacional, Vacaciones de verano, Capacitación, etc.'
    )
    
    activo = models.BooleanField(
        default=True,
        verbose_name='Activo'
    )
    
    usuario_registro = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        related_name='bloqueos_registrados',
        verbose_name='Usuario que Registró'
    )
    
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )
    
    class Meta:
        verbose_name = 'Bloqueo de Horario'
        verbose_name_plural = 'Bloqueos de Horarios'
        ordering = ['-fecha_inicio']
    
    def __str__(self):
        odontologo = self.odontologo.get_full_name() if self.odontologo else "Todos"
        return f"{odontologo} - {self.get_tipo_display()} ({self.fecha_inicio} al {self.fecha_fin})"
    
    def clean(self):
        """Validaciones"""
        if self.fecha_fin < self.fecha_inicio:
            raise ValidationError('La fecha de fin debe ser posterior o igual a la fecha de inicio.')
        
        if self.hora_inicio and self.hora_fin:
            if self.hora_fin <= self.hora_inicio:
                raise ValidationError('La hora de fin debe ser posterior a la hora de inicio.')


class Turno(models.Model):
    """Modelo para gestionar turnos de pacientes"""
    
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('confirmado', 'Confirmado'),
        ('en_atencion', 'En Atención'),
        ('atendido', 'Atendido'),
        ('cancelado', 'Cancelado'),
        ('ausente', 'Paciente Ausente'),
    ]
    
    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.CASCADE,
        related_name='turnos',
        verbose_name='Paciente'
    )
    
    odontologo = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        limit_choices_to={'rol': 'odontologo'},
        related_name='turnos_asignados',
        verbose_name='Odontólogo'
    )
    
    fecha = models.DateField(
        verbose_name='Fecha del Turno'
    )
    
    hora = models.TimeField(
        verbose_name='Hora del Turno'
    )
    
    duracion = models.IntegerField(
        default=30,
        validators=[MinValueValidator(15), MaxValueValidator(120)],
        verbose_name='Duración (minutos)'
    )
    
    motivo_consulta = models.CharField(
        max_length=255,
        verbose_name='Motivo de Consulta',
        help_text='Descripción breve del motivo de la consulta'
    )
    
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='pendiente',
        verbose_name='Estado del Turno'
    )
    
    observaciones = models.TextField(
        blank=True,
        null=True,
        verbose_name='Observaciones',
        help_text='Notas adicionales sobre el turno'
    )
    
    recordatorio_enviado = models.BooleanField(
        default=False,
        verbose_name='Recordatorio Enviado',
        help_text='Indica si se envió recordatorio al paciente'
    )
    
    fecha_confirmacion = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha de Confirmación'
    )
    
    fecha_atencion = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha de Atención Real'
    )
    
    # Auditoría
    usuario_registro = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        related_name='turnos_registrados',
        verbose_name='Usuario que Registró'
    )
    
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )
    
    fecha_modificacion = models.DateTimeField(
        auto_now=True,
        verbose_name='Última Modificación'
    )
    
    class Meta:
        verbose_name = 'Turno'
        verbose_name_plural = 'Turnos'
        ordering = ['fecha', 'hora']
        indexes = [
            models.Index(fields=['fecha', 'hora']),
            models.Index(fields=['odontologo', 'fecha']),
            models.Index(fields=['paciente', 'fecha']),
        ]
    
    def __str__(self):
        return f"{self.paciente.get_nombre_completo()} - {self.fecha.strftime('%d/%m/%Y')} {self.hora.strftime('%H:%M')} - Dr/a. {self.odontologo.get_full_name()}"
    
    def clean(self):
        """Validaciones del turno"""
        # No permitir turnos en el pasado
        if self.fecha and self.hora:
            turno_datetime = datetime.combine(self.fecha, self.hora)
            if turno_datetime < datetime.now():
                raise ValidationError('No se pueden crear turnos en fechas/horas pasadas.')
        
        # Verificar que no haya solapamiento de turnos
        if self.odontologo and self.fecha and self.hora:
            hora_fin = (datetime.combine(datetime.today(), self.hora) + timedelta(minutes=self.duracion)).time()
            
            turnos_solapados = Turno.objects.filter(
                odontologo=self.odontologo,
                fecha=self.fecha,
                estado__in=['pendiente', 'confirmado', 'en_atencion']
            ).exclude(pk=self.pk if self.pk else None)
            
            for turno in turnos_solapados:
                turno_fin = (datetime.combine(datetime.today(), turno.hora) + timedelta(minutes=turno.duracion)).time()
                
                # Verificar solapamiento
                if not (hora_fin <= turno.hora or self.hora >= turno_fin):
                    raise ValidationError(
                        f'Ya existe un turno para {self.odontologo.get_full_name()} '
                        f'el {self.fecha.strftime("%d/%m/%Y")} de {turno.hora.strftime("%H:%M")} a {turno_fin.strftime("%H:%M")}.'
                    )
    
    def get_hora_fin(self):
        """Retorna la hora de finalización del turno"""
        return (datetime.combine(datetime.today(), self.hora) + timedelta(minutes=self.duracion)).time()
    
    def puede_confirmar(self):
        """Verifica si el turno puede ser confirmado"""
        return self.estado == 'pendiente'
    
    def puede_cancelar(self):
        """Verifica si el turno puede ser cancelado"""
        return self.estado in ['pendiente', 'confirmado']
    
    def puede_atender(self):
        """Verifica si el turno puede ser marcado como atendido"""
        return self.estado in ['confirmado', 'en_atencion']
    
    def confirmar(self):
        """Confirma el turno"""
        if self.puede_confirmar():
            self.estado = 'confirmado'
            self.fecha_confirmacion = datetime.now()
            self.save()
    
    def iniciar_atencion(self):
        """Marca el turno como en atención"""
        if self.estado in ['confirmado', 'pendiente']:
            self.estado = 'en_atencion'
            self.save()
    
    def finalizar_atencion(self):
        """Marca el turno como atendido"""
        if self.puede_atender():
            self.estado = 'atendido'
            self.fecha_atencion = datetime.now()
            self.save()
    
    def cancelar(self, motivo=None):
        """Cancela el turno"""
        if self.puede_cancelar():
            self.estado = 'cancelado'
            if motivo:
                self.observaciones = f"{self.observaciones or ''}\nCancelado: {motivo}".strip()
            self.save()
    
    def marcar_ausente(self):
        """Marca al paciente como ausente"""
        if self.estado in ['confirmado', 'pendiente']:
            self.estado = 'ausente'
            self.save()

