from django import forms
from .models import Paciente
from datetime import date


class PacienteForm(forms.ModelForm):
    """Formulario para crear y editar pacientes"""
    
    class Meta:
        model = Paciente
        fields = ['nombre', 'apellido', 'dni', 'fecha_nacimiento', 'sexo',
                  'telefono', 'email', 'direccion', 'numero_afiliado', 
                  'obra_social_id', 'observaciones', 'activo']
        
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el nombre'
            }),
            'apellido': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el apellido'
            }),
            'dni': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 12345678'
            }),
            'fecha_nacimiento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'sexo': forms.Select(attrs={
                'class': 'form-select'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 3874123456'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'ejemplo@correo.com'
            }),
            'direccion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Calle, número, barrio'
            }),
            'numero_afiliado': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de afiliado'
            }),
            'obra_social_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la obra social'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Alergias, antecedentes médicos, observaciones generales...'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def clean_dni(self):
        """Validar que el DNI sea único (excepto en edición)"""
        dni = self.cleaned_data.get('dni')
        
        # Verificar si existe otro paciente con el mismo DNI
        paciente_existente = Paciente.objects.filter(dni=dni)
        
        # Si estamos editando, excluir el paciente actual
        if self.instance.pk:
            paciente_existente = paciente_existente.exclude(pk=self.instance.pk)
        
        if paciente_existente.exists():
            raise forms.ValidationError('Ya existe un paciente con este DNI.')
        
        return dni
    
    def clean_fecha_nacimiento(self):
        """Validar que la fecha de nacimiento sea lógica"""
        fecha = self.cleaned_data.get('fecha_nacimiento')
        
        if fecha:
            # No puede ser una fecha futura
            if fecha > date.today():
                raise forms.ValidationError('La fecha de nacimiento no puede ser futura.')
            
            # No puede ser mayor a 150 años
            edad = date.today().year - fecha.year
            if edad > 150:
                raise forms.ValidationError('La fecha de nacimiento no es válida.')
        
        return fecha
    
    def clean(self):
        """Validaciones adicionales"""
        cleaned_data = super().clean()
        numero_afiliado = cleaned_data.get('numero_afiliado')
        obra_social = cleaned_data.get('obra_social_id')
        
        # Si tiene número de afiliado, debe tener obra social y viceversa
        if numero_afiliado and not obra_social:
            self.add_error('obra_social_id', 'Debe especificar la obra social.')
        
        if obra_social and not numero_afiliado:
            self.add_error('numero_afiliado', 'Debe especificar el número de afiliado.')
        
        return cleaned_data