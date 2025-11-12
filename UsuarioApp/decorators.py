from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from functools import wraps

def rol_requerido(*roles_permitidos):
    """
    Decorador para restringir acceso según el rol del usuario.
    Uso: @rol_requerido('administrador', 'odontologo')
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                from django.shortcuts import redirect
                from django.urls import reverse
                return redirect(f"{reverse('login')}?next={request.path}")
            
            if request.user.rol in roles_permitidos or request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            raise PermissionDenied("No tenés permisos para acceder a esta página.")
        
        return _wrapped_view
    return decorator


# Decoradores específicos por rol
def solo_administrador(view_func):
    """Solo administradores pueden acceder"""
    return rol_requerido('administrador')(view_func)


def solo_odontologo(view_func):
    """Solo odontólogos pueden acceder"""
    return rol_requerido('odontologo')(view_func)


def solo_recepcionista(view_func):
    """Solo recepcionistas pueden acceder"""
    return rol_requerido('recepcionista')(view_func)


def odontologo_o_admin(view_func):
    """Odontólogos o administradores pueden acceder"""
    return rol_requerido('administrador', 'odontologo')(view_func)


def staff_medico(view_func):
    """Odontólogos, recepcionistas o administradores pueden acceder"""
    return rol_requerido('administrador', 'odontologo', 'recepcionista')(view_func)

def admin_o_odontologo_gestor(view_func):
    """Administradores o odontólogos pueden gestionar usuarios (con restricciones)"""
    return rol_requerido('administrador', 'odontologo')(view_func)