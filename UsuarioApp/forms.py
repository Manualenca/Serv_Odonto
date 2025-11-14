from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Usuario
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError



class UsuarioCreacionForm(UserCreationForm):
    """Formulario para crear nuevos usuarios"""
    
    class Meta:
        model = Usuario
        fields = ('username', 'email', 'first_name', 'last_name', 'rol', 
                  'telefono', 'matricula_profesional', 'especialidad', 'foto_perfil')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de usuario'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@ejemplo.com'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellido'}),
            'rol': forms.Select(attrs={'class': 'form-select'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '3874123456'}),
            'matricula_profesional': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: MP 12345'}),
            'especialidad': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Ortodoncia'}),
            'foto_perfil': forms.FileInput(attrs={'class': 'form-control'}),
        }
    
    password1 = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'})
    )
    password2 = forms.CharField(
        label="Confirmar contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirmar contraseña'})
    )
    
    def clean(self):
        cleaned_data = super().clean()
        rol = cleaned_data.get('rol')
        matricula = cleaned_data.get('matricula_profesional')
        especialidad = cleaned_data.get('especialidad')
        
        # Validar que odontólogos tengan matrícula
        if rol == 'odontologo':
            if not matricula:
                self.add_error('matricula_profesional', 'Los odontólogos deben tener matrícula profesional.')
        
        return cleaned_data

    def clean_password1(self):
        """Validar la contraseña con los validadores de Django"""
        password = self.cleaned_data.get('password1')
        if password:
            try:
                validate_password(password, self.instance)
            except DjangoValidationError as e:
                raise forms.ValidationError(e.messages)
        return password

class UsuarioEdicionForm(UserChangeForm):
    """Formulario para editar usuarios existentes"""
    
    password = None  # Removemos el campo de password del formulario de edición
    
    class Meta:
        model = Usuario
        fields = ('username', 'email', 'first_name', 'last_name', 'rol', 
                  'telefono', 'matricula_profesional', 'especialidad', 
                  'foto_perfil', 'activo')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'rol': forms.Select(attrs={'class': 'form-select'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'matricula_profesional': forms.TextInput(attrs={'class': 'form-control'}),
            'especialidad': forms.TextInput(attrs={'class': 'form-control'}),
            'foto_perfil': forms.FileInput(attrs={'class': 'form-control'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        rol = cleaned_data.get('rol')
        matricula = cleaned_data.get('matricula_profesional')
        
        # Validar que odontólogos tengan matrícula
        if rol == 'odontologo':
            if not matricula:
                self.add_error('matricula_profesional', 'Los odontólogos deben tener matrícula profesional.')
        
        return cleaned_data


class CambiarPasswordForm(forms.Form):
    """Formulario para cambiar la contraseña de un usuario"""
    
    nueva_password = forms.CharField(
        label="Nueva contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Nueva contraseña'})
    )
    confirmar_password = forms.CharField(
        label="Confirmar contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirmar contraseña'})
    )
    
    def clean(self):
        cleaned_data = super().clean()
        nueva = cleaned_data.get('nueva_password')
        confirmar = cleaned_data.get('confirmar_password')
        
        if nueva and confirmar and nueva != confirmar:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        
        return cleaned_data