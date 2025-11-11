from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied

class RolRequeridoMixin(LoginRequiredMixin):
    """
    Mixin para restringir acceso a vistas basadas en clases según el rol.
    Uso: class MiVista(RolRequeridoMixin, View):
             roles_permitidos = ['administrador', 'odontologo']
    """
    roles_permitidos = []
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        if request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)
        
        if request.user.rol not in self.roles_permitidos:
            raise PermissionDenied("No tenés permisos para acceder a esta página.")
        
        return super().dispatch(request, *args, **kwargs)


class SoloAdministradorMixin(RolRequeridoMixin):
    """Solo administradores"""
    roles_permitidos = ['administrador']


class SoloOdontologoMixin(RolRequeridoMixin):
    """Solo odontólogos"""
    roles_permitidos = ['odontologo']


class SoloRecepcionistaMixin(RolRequeridoMixin):
    """Solo recepcionistas"""
    roles_permitidos = ['recepcionista']


class OdontologoOAdminMixin(RolRequeridoMixin):
    """Odontólogos o administradores"""
    roles_permitidos = ['administrador', 'odontologo']


class StaffMedicoMixin(RolRequeridoMixin):
    """Odontólogos, recepcionistas o administradores"""
    roles_permitidos = ['administrador', 'odontologo', 'recepcionista']