from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from .decorators import solo_administrador, odontologo_o_admin, staff_medico
from .mixins import SoloAdministradorMixin, OdontologoOAdminMixin


# Vista de inicio/dashboard
@login_required
def dashboard(request):
    """Dashboard principal según el rol del usuario"""
    context = {
        'usuario': request.user
    }
    
    # Redirigir a diferentes dashboards según el rol
    if request.user.es_administrador():
        return render(request, 'UsuarioApp/dashboard_admin.html', context)
    elif request.user.es_odontologo():
        return render(request, 'UsuarioApp/dashboard_odontologo.html', context)
    elif request.user.es_recepcionista():
        return render(request, 'UsuarioApp/dashboard_recepcionista.html', context)
    elif request.user.es_auditor():
        return render(request, 'UsuarioApp/dashboard_auditor.html', context)
    
    return render(request, 'UsuarioApp/dashboard.html', context)


# Ejemplo con decorador
@solo_administrador
def panel_administracion(request):
    """Solo administradores pueden ver esto"""
    return render(request, 'UsuarioApp/panel_admin.html')


@odontologo_o_admin
def historias_clinicas(request):
    """Odontólogos y administradores pueden ver historias clínicas"""
    return render(request, 'UsuarioApp/historias_clinicas.html')


# Ejemplo con Class-Based View
class PanelAdministracionView(SoloAdministradorMixin, TemplateView):
    """Vista basada en clase - solo administradores"""
    template_name = 'UsuarioApp/panel_admin.html'


class HistoriasClinicasView(OdontologoOAdminMixin, TemplateView):
    """Vista basada en clase - odontólogos y administradores"""
    template_name = 'UsuarioApp/historias_clinicas.html'