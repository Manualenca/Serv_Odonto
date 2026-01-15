import csv
from django.core.management.base import BaseCommand
from PacientesApp.models import ObraSocial


class Command(BaseCommand):
    help = 'Carga las obras sociales desde un archivo CSV'

    def add_arguments(self, parser):
        parser.add_argument(
            'csv_file',
            type=str,
            help='Ruta al archivo CSV con las obras sociales'
        )

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        
        self.stdout.write(self.style.WARNING(f'Cargando obras sociales desde: {csv_file}'))
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file, delimiter='\t')
                
                creadas = 0
                actualizadas = 0
                errores = 0
                
                for row in reader:
                    try:
                        descripcion = row['descripcion'].strip()
                        rnos = row['rnos'].strip()
                        sigla = row['sigla'].strip() if row['sigla'].strip() else None
                        
                        # Buscar si ya existe por RNOS
                        obra_social, created = ObraSocial.objects.update_or_create(
                            codigo=rnos,
                            defaults={
                                'nombre': descripcion,
                                'activa': True
                            }
                        )
                        
                        if created:
                            creadas += 1
                            self.stdout.write(
                                self.style.SUCCESS(f'✓ Creada: {descripcion} (RNOS: {rnos})')
                            )
                        else:
                            actualizadas += 1
                            self.stdout.write(
                                self.style.WARNING(f'↻ Actualizada: {descripcion} (RNOS: {rnos})')
                            )
                    
                    except Exception as e:
                        errores += 1
                        self.stdout.write(
                            self.style.ERROR(f'✗ Error en fila: {row} - {str(e)}')
                        )
                
                # Resumen
                self.stdout.write('\n' + '='*50)
                self.stdout.write(self.style.SUCCESS(f'Obras sociales creadas: {creadas}'))
                self.stdout.write(self.style.WARNING(f'Obras sociales actualizadas: {actualizadas}'))
                if errores > 0:
                    self.stdout.write(self.style.ERROR(f'Errores: {errores}'))
                self.stdout.write(self.style.SUCCESS(f'\nTotal procesado: {creadas + actualizadas}'))
                self.stdout.write('='*50)
        
        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(f'Error: No se encontró el archivo {csv_file}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error al procesar el archivo: {str(e)}')
            )
            