from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from TurnosApp.models import Turno
from TurnosApp.notificaciones import enviar_recordatorio_turno
from django.conf import settings


class Command(BaseCommand):
    help = 'Envía recordatorios de turnos programados para mañana'

    def handle(self, *args, **options):
        # Fecha de mañana
        manana = timezone.now().date() + timedelta(days=1)
        
        # Buscar turnos para mañana que no se les haya enviado recordatorio
        turnos_pendientes = Turno.objects.filter(
            fecha=manana,
            estado__in=['pendiente', 'confirmado'],
            recordatorio_enviado=False,
            paciente__email__isnull=False
        ).exclude(paciente__email='')
        
        enviados = 0
        errores = 0
        
        self.stdout.write(self.style.WARNING(f'Buscando turnos para {manana}...'))
        
        for turno in turnos_pendientes:
            self.stdout.write(f'Enviando recordatorio a {turno.paciente.get_nombre_completo()}...')
            
            if enviar_recordatorio_turno(turno):
                enviados += 1
                self.stdout.write(self.style.SUCCESS(f'  ✓ Enviado'))
            else:
                errores += 1
                self.stdout.write(self.style.ERROR(f'  ✗ Error'))
        
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS(f'Recordatorios enviados: {enviados}'))
        if errores > 0:
            self.stdout.write(self.style.ERROR(f'Errores: {errores}'))
        self.stdout.write('='*50)
        