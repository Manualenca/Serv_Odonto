from django import forms
from .models import Paciente, CategoriaAntecedente, AntecedentePaciente
from datetime import date


class PacienteForm(forms.ModelForm):
    """Formulario para crear y editar pacientes"""
    
    # Campos para antecedentes médicos (se generan dinámicamente)
    antecedentes_enfermedades = forms.ModelMultipleChoiceField(
        queryset=CategoriaAntecedente.objects.filter(categoria='enfermedad_cronica', activo=True),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Enfermedades Crónicas'
    )
    
    antecedentes_its = forms.ModelMultipleChoiceField(
        queryset=CategoriaAntecedente.objects.filter(categoria='its', activo=True),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Infecciones de Transmisión Sexual (ITS)'
    )
    
    antecedentes_alergias = forms.ModelMultipleChoiceField(
        queryset=CategoriaAntecedente.objects.filter(categoria='alergia', activo=True),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Alergias'
    )
    
    antecedentes_medicacion = forms.ModelMultipleChoiceField(
        queryset=CategoriaAntecedente.objects.filter(categoria='medicacion', activo=True),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Medicación Actual'
    )
    
    class Meta:
        model = Paciente
        fields = ['nombre', 'apellido', 'dni', 'fecha_nacimiento', 'sexo',
                  'telefono', 'email', 'direccion', 'numero_afiliado', 
                  'obra_social', 'observaciones_generales', 'activo']
        
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
            'obra_social': forms.Select(attrs={
                'class': 'form-select'
            }),
            'observaciones_generales': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Otras observaciones no categorizadas...'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Si estamos editando, cargar los antecedentes actuales
        if self.instance.pk:
            antecedentes_actuales = self.instance.antecedentes_medicos.filter(activo=True)
            
            self.fields['antecedentes_enfermedades'].initial = antecedentes_actuales.filter(
                antecedente__categoria='enfermedad_cronica'
            ).values_list('antecedente', flat=True)
            
            self.fields['antecedentes_its'].initial = antecedentes_actuales.filter(
                antecedente__categoria='its'
            ).values_list('antecedente', flat=True)
            
            self.fields['antecedentes_alergias'].initial = antecedentes_actuales.filter(
                antecedente__categoria='alergia'
            ).values_list('antecedente', flat=True)
            
            self.fields['antecedentes_medicacion'].initial = antecedentes_actuales.filter(
                antecedente__categoria='medicacion'
            ).values_list('antecedente', flat=True)
    
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
        obra_social = cleaned_data.get('obra_social')
        
        # Si tiene número de afiliado, debe tener obra social y viceversa
        if numero_afiliado and not obra_social:
            self.add_error('obra_social', 'Debe seleccionar la obra social.')
        
        if obra_social and not numero_afiliado:
            self.add_error('numero_afiliado', 'Debe especificar el número de afiliado.')
        
        return cleaned_data
    
    def save(self, commit=True, usuario=None):
        """Guardar el paciente y sus antecedentes"""
        paciente = super().save(commit=commit)
        
        if commit:
            # Desactivar todos los antecedentes actuales
            AntecedentePaciente.objects.filter(paciente=paciente).update(activo=False)
            
            # Guardar antecedentes seleccionados
            todos_antecedentes = []
            todos_antecedentes.extend(self.cleaned_data.get('antecedentes_enfermedades', []))
            todos_antecedentes.extend(self.cleaned_data.get('antecedentes_its', []))
            todos_antecedentes.extend(self.cleaned_data.get('antecedentes_alergias', []))
            todos_antecedentes.extend(self.cleaned_data.get('antecedentes_medicacion', []))
            
            for antecedente in todos_antecedentes:
                AntecedentePaciente.objects.update_or_create(
                    paciente=paciente,
                    antecedente=antecedente,
                    defaults={
                        'activo': True,
                        'usuario_registro': usuario
                    }
                )
        
        return paciente
    