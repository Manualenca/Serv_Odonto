from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from UsuarioApp.decorators import staff_medico
from .models import Paciente
from .forms import PacienteForm


# ========== GESTIÓN DE PACIENTES ==========

@staff_medico
def lista_pacientes(request):
    """Lista de todos los pacientes con búsqueda y filtros"""
    pacientes = Paciente.objects.all().order_by('apellido', 'nombre')
    
    # Búsqueda
    busqueda = request.GET.get('buscar', '')
    if busqueda:
        pacientes = pacientes.filter(
            Q(dni__icontains=busqueda) |
            Q(nombre__icontains=busqueda) |
            Q(apellido__icontains=busqueda) |
            Q(telefono__icontains=busqueda) |
            Q(email__icontains=busqueda) |
            Q(numero_afiliado__icontains=busqueda)
        )
    
    # Filtro por sexo
    sexo_filtro = request.GET.get('sexo', '')
    if sexo_filtro:
        pacientes = pacientes.filter(sexo=sexo_filtro)
    
    # Filtro por estado
    estado_filtro = request.GET.get('estado', '')
    if estado_filtro == 'activos':
        pacientes = pacientes.filter(activo=True)
    elif estado_filtro == 'inactivos':
        pacientes = pacientes.filter(activo=False)
    
    # Filtro por obra social
    obra_social_filtro = request.GET.get('obra_social', '')
    if obra_social_filtro == 'con_obra':
        pacientes = pacientes.exclude(numero_afiliado__isnull=True).exclude(numero_afiliado='')
    elif obra_social_filtro == 'sin_obra':
        pacientes = pacientes.filter(Q(numero_afiliado__isnull=True) | Q(numero_afiliado=''))
    
    context = {
        'pacientes': pacientes,
        'busqueda': busqueda,
        'sexo_filtro': sexo_filtro,
        'estado_filtro': estado_filtro,
        'obra_social_filtro': obra_social_filtro,
        'total_pacientes': pacientes.count(),
    }
    
    return render(request, 'PacientesApp/lista_pacientes.html', context)


@staff_medico
def crear_paciente(request):
    """Crear un nuevo paciente"""
    if request.method == 'POST':
        form = PacienteForm(request.POST)
        if form.is_valid():
            paciente = form.save(commit=False)
            paciente.usuario_registro = request.user
            paciente.save()
            form.save_m2m()  # Guardar relaciones many-to-many
            
            # Guardar antecedentes
            form.save(usuario=request.user)
            
            messages.success(request, f'Paciente {paciente.get_nombre_completo()} registrado exitosamente.')
            return redirect('PacientesApp:lista_pacientes')
    else:
        form = PacienteForm()
    
    context = {
        'form': form,
        'titulo': 'Registrar Nuevo Paciente',
        'boton': 'Registrar Paciente'
    }
    
    return render(request, 'PacientesApp/form_paciente.html', context)


@staff_medico
def editar_paciente(request, pk):
    """Editar un paciente existente"""
    paciente = get_object_or_404(Paciente, pk=pk)
    
    if request.method == 'POST':
        form = PacienteForm(request.POST, instance=paciente)
        if form.is_valid():
            paciente = form.save(commit=False)
            paciente.save()
            
            # Guardar antecedentes
            form.save(usuario=request.user)
            
            messages.success(request, f'Paciente {paciente.get_nombre_completo()} actualizado exitosamente.')
            return redirect('PacientesApp:lista_pacientes')
    else:
        form = PacienteForm(instance=paciente)
    
    context = {
        'form': form,
        'paciente_editado': paciente,
        'titulo': f'Editar Paciente: {paciente.get_nombre_completo()}',
        'boton': 'Guardar Cambios'
    }
    
    return render(request, 'PacientesApp/form_paciente.html', context)


@staff_medico
def ver_paciente(request, pk):
    """Ver detalles completos de un paciente"""
    paciente = get_object_or_404(Paciente, pk=pk)
    
    # Obtener antecedentes organizados por categoría
    antecedentes_activos = paciente.antecedentes_medicos.filter(activo=True).select_related('antecedente')
    
    context = {
        'paciente': paciente,
        'enfermedades': antecedentes_activos.filter(antecedente__categoria='enfermedad_cronica'),
        'its': antecedentes_activos.filter(antecedente__categoria='its'),
        'alergias': antecedentes_activos.filter(antecedente__categoria='alergia'),
        'medicacion': antecedentes_activos.filter(antecedente__categoria='medicacion'),
    }
    
    return render(request, 'PacientesApp/ver_paciente.html', context)


@staff_medico
def toggle_paciente_activo(request, pk):
    """Activar o desactivar un paciente"""
    paciente = get_object_or_404(Paciente, pk=pk)
    
    # Solo odontólogos y administradores pueden desactivar
    if request.user.es_recepcionista():
        messages.error(request, 'No tenés permisos para desactivar pacientes. Solicitá autorización a un odontólogo o administrador.')
        return redirect('PacientesApp:lista_pacientes')
    
    paciente.activo = not paciente.activo
    paciente.save()
    
    estado = "activado" if paciente.activo else "desactivado"
    messages.success(request, f'Paciente {paciente.get_nombre_completo()} {estado} exitosamente.')
    
    return redirect('PacientesApp:lista_pacientes')