from django import forms
from .models import Turno, ConfiguracionAgenda, BloqueoHorario
from PacientesApp.models import Paciente
from UsuarioApp.models import Usuario
from datetime import datetime, timedelta, time


class TurnoForm(forms.ModelForm):
    """Formulario para crear y editar turnos"""
    
    class Meta:
        model = Turno
        fields = ['paciente', 'odontologo', 'fecha', 'hora', 'duracion', 
                  'motivo_consulta', 'observaciones'] #Se sacó estado
        
        widgets = {
            'paciente': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'odontologo': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'fecha': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'required': True
            }),
            'hora': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time',
                'required': True
            }),
            'duracion': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 15,
                'max': 120,
                'step': 15,
                'value': 30
            }),
            'motivo_consulta': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Control, Limpieza, Extracción, etc.',
                'required': True
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observaciones adicionales (opcional)'
            }),
#            'estado': forms.Select(attrs={
#               'class': 'form-select'
#            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filtrar solo odontólogos activos
        self.fields['odontologo'].queryset = Usuario.objects.filter(
            rol='odontologo',
            is_active=True
        )
        
        # Filtrar solo pacientes activos
        self.fields['paciente'].queryset = Paciente.objects.filter(activo=True)
        
        # Si es un turno nuevo, establecer estado por defecto
#        if not self.instance.pk:
#            self.fields['estado'].widget = forms.HiddenInput()
#            self.fields['estado'].initial = 'pendiente'
    
    def clean(self):
        cleaned_data = super().clean()
        fecha = cleaned_data.get('fecha')
        hora = cleaned_data.get('hora')
        
        # Validar que no sea en el pasado
        if fecha and hora:
            turno_datetime = datetime.combine(fecha, hora)
            if turno_datetime < datetime.now():
                raise forms.ValidationError('No se pueden crear turnos en fechas/horas pasadas.')
        
        return cleaned_data


class ConfiguracionAgendaForm(forms.ModelForm):
    """Formulario para configurar horarios de atención"""
    
    class Meta:
        model = ConfiguracionAgenda
        fields = ['odontologo', 'dia_semana', 'hora_inicio', 'hora_fin', 
                  'duracion_turno', 'turnos_simultaneos', 'activo']
        
        widgets = {
            'odontologo': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'dia_semana': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'hora_inicio': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time',
                'required': True
            }),
            'hora_fin': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time',
                'required': True
            }),
            'duracion_turno': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 15,
                'max': 120,
                'step': 15,
                'value': 30
            }),
            'turnos_simultaneos': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 5,
                'value': 1
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filtrar solo odontólogos
        self.fields['odontologo'].queryset = Usuario.objects.filter(
            rol='odontologo',
            is_active=True
        )


class BloqueoHorarioForm(forms.ModelForm):
    """Formulario para bloquear horarios"""
    
    class Meta:
        model = BloqueoHorario
        fields = ['odontologo', 'fecha_inicio', 'fecha_fin', 'hora_inicio', 
                  'hora_fin', 'tipo', 'motivo', 'activo']
        
        widgets = {
            'odontologo': forms.Select(attrs={
                'class': 'form-select'
            }),
            'fecha_inicio': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'required': True
            }),
            'fecha_fin': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'required': True
            }),
            'hora_inicio': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'hora_fin': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'tipo': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'motivo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Feriado Nacional, Vacaciones, Capacitación',
                'required': True
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filtrar solo odontólogos
        self.fields['odontologo'].queryset = Usuario.objects.filter(
            rol='odontologo',
            is_active=True
        )
        
        # Hacer odontologo opcional (para bloqueos generales)
        self.fields['odontologo'].required = False


class FiltroTurnosForm(forms.Form):
    """Formulario para filtrar turnos"""
    
    fecha_desde = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='Desde'
    )
    
    fecha_hasta = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='Hasta'
    )
    
    odontologo = forms.ModelChoiceField(
        queryset=Usuario.objects.filter(rol='odontologo', is_active=True),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='Odontólogo',
        empty_label='Todos'
    )
    
    paciente = forms.ModelChoiceField(
        queryset=Paciente.objects.filter(activo=True),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='Paciente',
        empty_label='Todos'
    )
    
    estado = forms.ChoiceField(
        choices=[('', 'Todos')] + Turno.ESTADO_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='Estado'
    )
class TurnoEditarForm(TurnoForm):
    """Formulario para editar turnos (incluye estado)"""
    
    class Meta(TurnoForm.Meta):
        fields = TurnoForm.Meta.fields + ['estado']  # Agregar estado
        widgets = {
            **TurnoForm.Meta.widgets,
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }