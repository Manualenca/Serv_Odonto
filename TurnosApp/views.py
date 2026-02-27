from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, timedelta, date
from UsuarioApp.decorators import staff_medico, solo_administrador, admin_o_odontologo_gestor
from .models import Turno, ConfiguracionAgenda, BloqueoHorario
from .forms import TurnoForm, ConfiguracionAgendaForm, BloqueoHorarioForm, FiltroTurnosForm
from .notificaciones import enviar_confirmacion_turno, enviar_cancelacion_turno


# ========== GESTIÓN DE TURNOS ==========

@staff_medico
def lista_turnos(request):
    """Lista de turnos con filtros"""
    
    # Fecha por defecto: semana actual
    hoy = date.today()
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    fin_semana = inicio_semana + timedelta(days=6)
    
    # Obtener turnos
    turnos = Turno.objects.all().select_related('paciente', 'odontologo').order_by('fecha', 'hora')
    
    # Aplicar filtros
    form = FiltroTurnosForm(request.GET)
    if form.is_valid():
        fecha_desde = form.cleaned_data.get('fecha_desde') or inicio_semana
        fecha_hasta = form.cleaned_data.get('fecha_hasta') or fin_semana
        odontologo = form.cleaned_data.get('odontologo')
        paciente = form.cleaned_data.get('paciente')
        estado = form.cleaned_data.get('estado')
        
        turnos = turnos.filter(fecha__range=[fecha_desde, fecha_hasta])
        
        if odontologo:
            turnos = turnos.filter(odontologo=odontologo)
        
        if paciente:
            turnos = turnos.filter(paciente=paciente)
        
        if estado:
            turnos = turnos.filter(estado=estado)
    else:
        turnos = turnos.filter(fecha__range=[inicio_semana, fin_semana])
    
    # Si es odontólogo, solo ver sus turnos
    if request.user.es_odontologo():
        turnos = turnos.filter(odontologo=request.user)
    
    context = {
        'turnos': turnos,
        'form': form,
        'total_turnos': turnos.count(),
    }
    
    return render(request, 'TurnosApp/lista_turnos.html', context)


@staff_medico
def crear_turno(request):
    """Crear un nuevo turno"""
    
    if request.method == 'POST':
        form = TurnoForm(request.POST)
        if form.is_valid():
            turno = form.save(commit=False)
            turno.usuario_registro = request.user
            turno.save()
            
            # Enviar email de confirmación
            enviar_confirmacion_turno(turno)
            
            messages.success(request, f'Turno creado exitosamente para {turno.paciente.get_nombre_completo()}.')
            return redirect('TurnosApp:lista_turnos')
    else:
        form = TurnoForm()
    
    context = {
        'form': form,
        'titulo': 'Nuevo Turno',
        'boton': 'Crear Turno'
    }
    
    return render(request, 'TurnosApp/form_turno.html', context)


@staff_medico
def editar_turno(request, pk):
    """Editar un turno existente"""
    
    turno = get_object_or_404(Turno, pk=pk)
    
    # Si es odontólogo, solo puede editar sus turnos
    if request.user.es_odontologo() and turno.odontologo != request.user:
        messages.error(request, 'No tenés permisos para editar este turno.')
        return redirect('TurnosApp:lista_turnos')
    
    if request.method == 'POST':
        form = TurnoForm(request.POST, instance=turno)
        if form.is_valid():
            form.save()
            messages.success(request, f'Turno actualizado exitosamente.')
            return redirect('TurnosApp:lista_turnos')
    else:
        form = TurnoForm(instance=turno)
    
    context = {
        'form': form,
        'turno': turno,
        'titulo': f'Editar Turno - {turno.paciente.get_nombre_completo()}',
        'boton': 'Guardar Cambios'
    }
    
    return render(request, 'TurnosApp/form_turno.html', context)


@staff_medico
def ver_turno(request, pk):
    """Ver detalles de un turno"""
    
    turno = get_object_or_404(Turno, pk=pk)
    
    # Si es odontólogo, solo puede ver sus turnos
    if request.user.es_odontologo() and turno.odontologo != request.user:
        messages.error(request, 'No tenés permisos para ver este turno.')
        return redirect('TurnosApp:lista_turnos')
    
    context = {
        'turno': turno,
    }
    
    return render(request, 'TurnosApp/ver_turno.html', context)


@staff_medico
def confirmar_turno(request, pk):
    """Confirmar un turno"""
    
    turno = get_object_or_404(Turno, pk=pk)
    
    if turno.puede_confirmar():
        turno.confirmar()
        messages.success(request, f'Turno confirmado para {turno.paciente.get_nombre_completo()}.')
    else:
        messages.warning(request, 'El turno no puede ser confirmado en su estado actual.')
    
    return redirect('TurnosApp:lista_turnos')


@staff_medico
def cancelar_turno(request, pk):
    """Cancelar un turno"""
    
    turno = get_object_or_404(Turno, pk=pk)
    
    if request.method == 'POST':
        motivo = request.POST.get('motivo', '')
        
        if turno.puede_cancelar():
            turno.cancelar(motivo)
            enviar_cancelacion_turno(turno, motivo)
            messages.success(request, f'Turno cancelado.')
        else:
            messages.warning(request, 'El turno no puede ser cancelado en su estado actual.')
        
        return redirect('TurnosApp:lista_turnos')
    
    context = {
        'turno': turno,
    }
    
    return render(request, 'TurnosApp/cancelar_turno.html', context)


@staff_medico
def iniciar_atencion(request, pk):
    """Marcar turno como en atención"""
    
    turno = get_object_or_404(Turno, pk=pk)
    
    # Solo el odontólogo asignado puede iniciar la atención
    if request.user.es_odontologo() and turno.odontologo != request.user:
        messages.error(request, 'Solo el odontólogo asignado puede iniciar la atención.')
        return redirect('TurnosApp:lista_turnos')
    
    turno.iniciar_atencion()
    messages.success(request, f'Atención iniciada para {turno.paciente.get_nombre_completo()}.')
    
    return redirect('TurnosApp:lista_turnos')


@staff_medico
def finalizar_atencion(request, pk):
    """Marcar turno como atendido"""
    
    turno = get_object_or_404(Turno, pk=pk)
    
    # Solo el odontólogo asignado puede finalizar la atención
    if request.user.es_odontologo() and turno.odontologo != request.user:
        messages.error(request, 'Solo el odontólogo asignado puede finalizar la atención.')
        return redirect('TurnosApp:lista_turnos')
    
    turno.finalizar_atencion()
    messages.success(request, f'Atención finalizada para {turno.paciente.get_nombre_completo()}.')
    
    return redirect('TurnosApp:lista_turnos')


@staff_medico
def marcar_ausente(request, pk):
    """Marcar paciente como ausente"""
    
    turno = get_object_or_404(Turno, pk=pk)
    
    turno.marcar_ausente()
    messages.warning(request, f'Paciente {turno.paciente.get_nombre_completo()} marcado como ausente.')
    
    return redirect('TurnosApp:lista_turnos')


# ========== CONFIGURACIÓN DE AGENDA (Solo Administrador) ==========

@solo_administrador
def configuracion_agenda(request):
    """Lista de configuraciones de agenda"""
    
    configuraciones = ConfiguracionAgenda.objects.all().select_related('odontologo').order_by('odontologo', 'dia_semana', 'hora_inicio')
    
    context = {
        'configuraciones': configuraciones,
    }
    
    return render(request, 'TurnosApp/configuracion_agenda.html', context)


@solo_administrador
def crear_configuracion(request):
    """Crear configuración de agenda"""
    
    if request.method == 'POST':
        form = ConfiguracionAgendaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Configuración de agenda creada exitosamente.')
            return redirect('TurnosApp:configuracion_agenda')
    else:
        form = ConfiguracionAgendaForm()
    
    context = {
        'form': form,
        'titulo': 'Nueva Configuración de Agenda',
        'boton': 'Crear Configuración'
    }
    
    return render(request, 'TurnosApp/form_configuracion.html', context)


@solo_administrador
def editar_configuracion(request, pk):
    """Editar configuración de agenda"""
    
    configuracion = get_object_or_404(ConfiguracionAgenda, pk=pk)
    
    if request.method == 'POST':
        form = ConfiguracionAgendaForm(request.POST, instance=configuracion)
        if form.is_valid():
            form.save()
            messages.success(request, 'Configuración actualizada exitosamente.')
            return redirect('TurnosApp:configuracion_agenda')
    else:
        form = ConfiguracionAgendaForm(instance=configuracion)
    
    context = {
        'form': form,
        'configuracion': configuracion,
        'titulo': 'Editar Configuración de Agenda',
        'boton': 'Guardar Cambios'
    }
    
    return render(request, 'TurnosApp/form_configuracion.html', context)


@solo_administrador
def eliminar_configuracion(request, pk):
    """Eliminar configuración de agenda"""
    
    configuracion = get_object_or_404(ConfiguracionAgenda, pk=pk)
    configuracion.delete()
    messages.success(request, 'Configuración eliminada exitosamente.')
    
    return redirect('TurnosApp:configuracion_agenda')
