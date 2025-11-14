from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
import re


class CustomPasswordValidator:
    """
    Validador personalizado de contraseñas:
    - Al menos una mayúscula
    - Al menos un número
    - Al menos un carácter especial
    """
    
    def validate(self, password, user=None):
        if not re.findall('[A-Z]', password):
            raise ValidationError(
                _("La contraseña debe contener al menos una letra mayúscula."),
                code='password_no_upper',
            )
        
        if not re.findall('[0-9]', password):
            raise ValidationError(
                _("La contraseña debe contener al menos un número."),
                code='password_no_number',
            )
        
        if not re.findall('[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError(
                _("La contraseña debe contener al menos un carácter especial (!@#$%^&*...)."),
                code='password_no_special',
            )
    
    def get_help_text(self):
        return _(
            "Tu contraseña debe contener al menos una mayúscula, un número y un carácter especial."
        )