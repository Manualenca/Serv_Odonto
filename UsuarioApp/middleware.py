from django.utils import timezone
from django.contrib.auth import logout
from django.conf import settings
from django.shortcuts import redirect
from django.contrib import messages
from datetime import datetime, timedelta

class SessionIdleTimeout:
    """
    Middleware que cierra la sesión automáticamente después de un período de inactividad.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Obtener el tiempo de la última actividad
            last_activity = request.session.get('last_activity')
            
            if last_activity:
                # Convertir a datetime
                last_activity_time = datetime.fromisoformat(last_activity)
                now = datetime.now()
                
                # Obtener el timeout configurado (por defecto 30 minutos)
                idle_timeout = getattr(settings, 'SESSION_IDLE_TIMEOUT', 1800)
                
                # Verificar si pasó el tiempo de inactividad
                if (now - last_activity_time).seconds > idle_timeout:
                    # Cerrar sesión
                    logout(request)
                    request.session.flush()
                    messages.warning(request, 'Tu sesión ha expirado por inactividad.')
                    return redirect('UsuarioApp:login')
            
            # Actualizar el tiempo de última actividad
            request.session['last_activity'] = datetime.now().isoformat()
        
        response = self.get_response(request)
        return response