from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from django.views.generic import TemplateView, ListView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.db.models import Q
from .decorators import solo_administrador, odontologo_o_admin,admin_o_odontologo_gestor, staff_medico
from .mixins import SoloAdministradorMixin, OdontologoOAdminMixin
from .models import Usuario
from .forms import UsuarioCreacionForm, UsuarioEdicionForm, CambiarPasswordForm
from django.shortcuts import redirect

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

# ========== GESTIÓN DE USUARIOS (Administrador o Odontólogo) ==========

@admin_o_odontologo_gestor
def lista_usuarios(request):
    """Lista de todos los usuarios del sistema con búsqueda y filtros"""
    
    # Si es odontólogo, solo puede ver recepcionistas y auditores
    if request.user.es_odontologo():
        usuarios = Usuario.objects.filter(rol__in=['recepcionista', 'auditor']).order_by('-fecha_creacion')
    else:
        # Administradores ven todos
        usuarios = Usuario.objects.all().order_by('-fecha_creacion')
    
    # Búsqueda
    busqueda = request.GET.get('buscar', '')
    if busqueda:
        usuarios = usuarios.filter(
            Q(username__icontains=busqueda) |
            Q(first_name__icontains=busqueda) |
            Q(last_name__icontains=busqueda) |
            Q(email__icontains=busqueda) |
            Q(matricula_profesional__icontains=busqueda)
        )
    
    # Filtro por rol
    rol_filtro = request.GET.get('rol', '')
    if rol_filtro:
        usuarios = usuarios.filter(rol=rol_filtro)
    
    # Filtro por estado
    estado_filtro = request.GET.get('estado', '')
    if estado_filtro == 'activos':
        usuarios = usuarios.filter(activo=True)
    elif estado_filtro == 'inactivos':
        usuarios = usuarios.filter(activo=False)
    
    # Filtrar roles disponibles según el usuario
    if request.user.es_odontologo():
        roles_disponibles = [('recepcionista', 'Recepcionista'), ('auditor', 'Auditor')]
    else:
        roles_disponibles = Usuario.ROLES
    
    context = {
        'usuarios': usuarios,
        'busqueda': busqueda,
        'rol_filtro': rol_filtro,
        'estado_filtro': estado_filtro,
        'roles': roles_disponibles,
    }
    
    return render(request, 'UsuarioApp/lista_usuarios.html', context)


@admin_o_odontologo_gestor
def crear_usuario(request):
    """Crear un nuevo usuario"""
    
    if request.method == 'POST':
        form = UsuarioCreacionForm(request.POST, request.FILES)
        
        # Si es odontólogo, validar que solo cree recepcionistas o auditores
        if request.user.es_odontologo():
            rol_seleccionado = request.POST.get('rol')
            if rol_seleccionado not in ['recepcionista', 'auditor']:
                messages.error(request, 'Solo podés crear usuarios con rol Recepcionista o Auditor.')
                return render(request, 'UsuarioApp/form_usuario.html', {
                    'form': form,
                    'titulo': 'Crear Nuevo Usuario',
                    'boton': 'Crear Usuario'
                })
        
        if form.is_valid():
            usuario = form.save()
            messages.success(request, f'Usuario {usuario.username} creado exitosamente.')
            return redirect('UsuarioApp:lista_usuarios')
    else:
        form = UsuarioCreacionForm()
        
        # Si es odontólogo, limitar las opciones de rol
        if request.user.es_odontologo():
            form.fields['rol'].choices = [
                ('recepcionista', 'Recepcionista'),
                ('auditor', 'Auditor')
            ]
    
    context = {
        'form': form,
        'titulo': 'Crear Nuevo Usuario',
        'boton': 'Crear Usuario'
    }
    
    return render(request, 'UsuarioApp/form_usuario.html', context)


@admin_o_odontologo_gestor
def editar_usuario(request, pk):
    """Editar un usuario existente"""
    usuario = get_object_or_404(Usuario, pk=pk)
    
    # Verificar permisos: odontólogo solo puede editar recepcionistas y auditores
    if request.user.es_odontologo():
        if usuario.rol not in ['recepcionista', 'auditor']:
            messages.error(request, 'No tenés permisos para editar este usuario.')
            return redirect('UsuarioApp:lista_usuarios')
    
    if request.method == 'POST':
        form = UsuarioEdicionForm(request.POST, request.FILES, instance=usuario)
        
        # Si es odontólogo, validar que no cambie el rol a admin u odontólogo
        if request.user.es_odontologo():
            rol_seleccionado = request.POST.get('rol')
            if rol_seleccionado not in ['recepcionista', 'auditor']:
                messages.error(request, 'Solo podés asignar los roles Recepcionista o Auditor.')
                return render(request, 'UsuarioApp/form_usuario.html', {
                    'form': form,
                    'usuario_editado': usuario,
                    'titulo': f'Editar Usuario: {usuario.username}',
                    'boton': 'Guardar Cambios'
                })
        
        if form.is_valid():
            form.save()
            messages.success(request, f'Usuario {usuario.username} actualizado exitosamente.')
            return redirect('UsuarioApp:lista_usuarios')
    else:
        form = UsuarioEdicionForm(instance=usuario)
        
        # Si es odontólogo, limitar las opciones de rol
        if request.user.es_odontologo():
            form.fields['rol'].choices = [
                ('recepcionista', 'Recepcionista'),
                ('auditor', 'Auditor')
            ]
    
    context = {
        'form': form,
        'usuario_editado': usuario,
        'titulo': f'Editar Usuario: {usuario.username}',
        'boton': 'Guardar Cambios'
    }
    
    return render(request, 'UsuarioApp/form_usuario.html', context)


@admin_o_odontologo_gestor
def cambiar_password_usuario(request, pk):
    """Cambiar la contraseña de un usuario"""
    usuario = get_object_or_404(Usuario, pk=pk)
    
    # Verificar permisos: odontólogo solo puede cambiar password de recepcionistas y auditores
    if request.user.es_odontologo():
        if usuario.rol not in ['recepcionista', 'auditor']:
            messages.error(request, 'No tenés permisos para cambiar la contraseña de este usuario.')
            return redirect('UsuarioApp:lista_usuarios')
    
    if request.method == 'POST':
        form = CambiarPasswordForm(request.POST)
        if form.is_valid():
            nueva_password = form.cleaned_data['nueva_password']
            usuario.set_password(nueva_password)
            usuario.save()
            messages.success(request, f'Contraseña de {usuario.username} actualizada exitosamente.')
            return redirect('UsuarioApp:lista_usuarios')
    else:
        form = CambiarPasswordForm()
    
    context = {
        'form': form,
        'usuario_editado': usuario,
    }
    
    return render(request, 'UsuarioApp/cambiar_password.html', context)


@admin_o_odontologo_gestor
def toggle_usuario_activo(request, pk):
    """Activar o desactivar un usuario"""
    usuario = get_object_or_404(Usuario, pk=pk)
    
    # Verificar permisos: odontólogo solo puede activar/desactivar recepcionistas y auditores
    if request.user.es_odontologo():
        if usuario.rol not in ['recepcionista', 'auditor']:
            messages.error(request, 'No tenés permisos para activar/desactivar este usuario.')
            return redirect('UsuarioApp:lista_usuarios')
    
    # No permitir desactivar al superusuario
    if usuario.is_superuser:
        messages.error(request, 'No se puede desactivar al superusuario.')
        return redirect('UsuarioApp:lista_usuarios')
    
    # No permitir desactivarse a sí mismo
    if usuario == request.user:
        messages.error(request, 'No podés desactivar tu propio usuario.')
        return redirect('UsuarioApp:lista_usuarios')
    
    usuario.activo = not usuario.activo
    usuario.is_active = usuario.activo  # También actualizar el is_active de Django
    usuario.save()
    
    estado = "activado" if usuario.activo else "desactivado"
    messages.success(request, f'Usuario {usuario.username} {estado} exitosamente.')
    
    return redirect('UsuarioApp:lista_usuarios')


@admin_o_odontologo_gestor
def ver_usuario(request, pk):
    """Ver detalles de un usuario"""
    usuario = get_object_or_404(Usuario, pk=pk)
    
    # Verificar permisos: odontólogo solo puede ver recepcionistas y auditores
    if request.user.es_odontologo():
        if usuario.rol not in ['recepcionista', 'auditor']:
            messages.error(request, 'No tenés permisos para ver este usuario.')
            return redirect('UsuarioApp:lista_usuarios')
    
    context = {
        'usuario_detalle': usuario,
    }
    
    return render(request, 'UsuarioApp/ver_usuario.html', context)

def sesion_expirada(request):
    """Vista que se muestra cuando la sesión expira por inactividad"""
    return render(request, 'UsuarioApp/sesion_expirada.html')

def logout_view(request):
    """Cerrar sesión del usuario"""
    logout(request)
    messages.info(request, 'Has cerrado sesión exitosamente.')
    return redirect('UsuarioApp:login')

