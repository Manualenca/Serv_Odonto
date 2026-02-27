from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
from datetime import datetime, timedelta


def enviar_confirmacion_turno(turno):
    """
    Envía email de confirmación cuando se crea un turno nuevo
    """
    paciente = turno.paciente
    
    # Si el paciente no tiene email, no enviar
    if not paciente.email:
        return False
    
    asunto = f'Turno Confirmado - {turno.fecha.strftime("%d/%m/%Y")} {turno.hora.strftime("%H:%M")}'
    
    # Contexto para el template
    contexto = {
        'paciente': paciente,
        'turno': turno,
        'odontologo': turno.odontologo,
    }
    
    # Renderizar el template HTML
    mensaje_html = render_to_string('TurnosApp/emails/confirmacion_turno.html', contexto)
    mensaje_texto = strip_tags(mensaje_html)
    
    try:
        send_mail(
            subject=asunto,
            message=mensaje_texto,
            from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@clinica.com',
            recipient_list=[paciente.email],
            html_message=mensaje_html,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error al enviar email: {e}")
        return False


def enviar_recordatorio_turno(turno):
    """
    Envía recordatorio de turno (se ejecuta automáticamente 24hs antes)
    """
    paciente = turno.paciente
    
    if not paciente.email:
        return False
    
    asunto = f'Recordatorio: Turno mañana {turno.hora.strftime("%H:%M")}'
    
    contexto = {
        'paciente': paciente,
        'turno': turno,
        'odontologo': turno.odontologo,
    }
    
    mensaje_html = render_to_string('TurnosApp/emails/recordatorio_turno.html', contexto)
    mensaje_texto = strip_tags(mensaje_html)
    
    try:
        send_mail(
            subject=asunto,
            message=mensaje_texto,
            from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@clinica.com',
            recipient_list=[paciente.email],
            html_message=mensaje_html,
            fail_silently=False,
        )
        
        # Marcar como enviado
        turno.recordatorio_enviado = True
        turno.save()
        
        return True
    except Exception as e:
        print(f"Error al enviar recordatorio: {e}")
        return False


def enviar_cancelacion_turno(turno, motivo=None):
    """
    Envía email cuando se cancela un turno
    """
    paciente = turno.paciente
    
    if not paciente.email:
        return False
    
    asunto = f'Turno Cancelado - {turno.fecha.strftime("%d/%m/%Y")} {turno.hora.strftime("%H:%M")}'
    
    contexto = {
        'paciente': paciente,
        'turno': turno,
        'odontologo': turno.odontologo,
        'motivo': motivo,
    }
    
    mensaje_html = render_to_string('TurnosApp/emails/cancelacion_turno.html', contexto)
    mensaje_texto = strip_tags(mensaje_html)
    
    try:
        send_mail(
            subject=asunto,
            message=mensaje_texto,
            from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@clinica.com',
            recipient_list=[paciente.email],
            html_message=mensaje_html,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error al enviar cancelación: {e}")
        return False


def enviar_recordatorio_whatsapp(turno):
    """
    Placeholder para implementación futura de WhatsApp
    Se implementará con Twilio o WhatsApp Business API
    """
    # TODO: Implementar cuando se configure WhatsApp
    paciente = turno.paciente
    
    if not paciente.telefono:
        return False
    
    mensaje = f"""
    Hola {paciente.nombre}!
    
    Te recordamos tu turno:
    📅 {turno.fecha.strftime('%d/%m/%Y')}
    🕐 {turno.hora.strftime('%H:%M')}
    👨‍⚕️ Dr/a. {turno.odontologo.get_full_name()}
    
    Clínica Odontológica
    """
    
    # Aquí irá la integración con Twilio o WhatsApp Business API
    # from twilio.rest import Client
    # client = Client(account_sid, auth_token)
    # message = client.messages.create(...)
    
    print(f"[WhatsApp - No implementado aún] Mensaje para {paciente.telefono}: {mensaje}")
    return False