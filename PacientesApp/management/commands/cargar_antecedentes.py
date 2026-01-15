from django.core.management.base import BaseCommand
from PacientesApp.models import CategoriaAntecedente


class Command(BaseCommand):
    help = 'Carga los antecedentes médicos predefinidos'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Cargando antecedentes médicos...'))
        
        antecedentes = [
            # ENFERMEDADES CRÓNICAS
            {'nombre': 'Diabetes tipo 1', 'categoria': 'enfermedad_cronica', 'requiere_precaucion': True, 'orden': 1},
            {'nombre': 'Diabetes tipo 2', 'categoria': 'enfermedad_cronica', 'requiere_precaucion': True, 'orden': 2},
            {'nombre': 'Hipertensión arterial', 'categoria': 'enfermedad_cronica', 'requiere_precaucion': True, 'orden': 3},
            {'nombre': 'Cardiopatía', 'categoria': 'enfermedad_cronica', 'requiere_precaucion': True, 'orden': 4},
            {'nombre': 'Insuficiencia cardíaca', 'categoria': 'enfermedad_cronica', 'requiere_precaucion': True, 'orden': 5},
            {'nombre': 'Arritmias', 'categoria': 'enfermedad_cronica', 'requiere_precaucion': True, 'orden': 6},
            {'nombre': 'Asma', 'categoria': 'enfermedad_cronica', 'requiere_precaucion': True, 'orden': 7},
            {'nombre': 'EPOC (Enfermedad Pulmonar Obstructiva Crónica)', 'categoria': 'enfermedad_cronica', 'requiere_precaucion': True, 'orden': 8},
            {'nombre': 'Insuficiencia renal', 'categoria': 'enfermedad_cronica', 'requiere_precaucion': True, 'orden': 9},
            {'nombre': 'Insuficiencia hepática', 'categoria': 'enfermedad_cronica', 'requiere_precaucion': True, 'orden': 10},
            {'nombre': 'Epilepsia', 'categoria': 'enfermedad_cronica', 'requiere_precaucion': True, 'orden': 11},
            {'nombre': 'Hemofilia', 'categoria': 'enfermedad_cronica', 'requiere_precaucion': True, 'orden': 12},
            {'nombre': 'Trastornos de coagulación', 'categoria': 'enfermedad_cronica', 'requiere_precaucion': True, 'orden': 13},
            {'nombre': 'Osteoporosis', 'categoria': 'enfermedad_cronica', 'requiere_precaucion': True, 'orden': 14},
            {'nombre': 'Artritis reumatoidea', 'categoria': 'enfermedad_cronica', 'requiere_precaucion': False, 'orden': 15},
            {'nombre': 'Lupus', 'categoria': 'enfermedad_cronica', 'requiere_precaucion': True, 'orden': 16},
            {'nombre': 'Enfermedad de Crohn', 'categoria': 'enfermedad_cronica', 'requiere_precaucion': False, 'orden': 17},
            {'nombre': 'Cáncer (especificar en observaciones)', 'categoria': 'enfermedad_cronica', 'requiere_precaucion': True, 'orden': 18},
            {'nombre': 'Tiroides (hipo/hipertiroidismo)', 'categoria': 'enfermedad_cronica', 'requiere_precaucion': False, 'orden': 19},
            
            # ITS - INFECCIONES DE TRANSMISIÓN SEXUAL
            {'nombre': 'VIH/SIDA', 'categoria': 'its', 'requiere_precaucion': True, 'orden': 1},
            {'nombre': 'Hepatitis B', 'categoria': 'its', 'requiere_precaucion': True, 'orden': 2},
            {'nombre': 'Hepatitis C', 'categoria': 'its', 'requiere_precaucion': True, 'orden': 3},
            {'nombre': 'Sífilis', 'categoria': 'its', 'requiere_precaucion': True, 'orden': 4},
            {'nombre': 'Herpes genital', 'categoria': 'its', 'requiere_precaucion': False, 'orden': 5},
            {'nombre': 'VPH (Virus del Papiloma Humano)', 'categoria': 'its', 'requiere_precaucion': False, 'orden': 6},
            
            # ALERGIAS
            {'nombre': 'Penicilina', 'categoria': 'alergia', 'requiere_precaucion': True, 'orden': 1},
            {'nombre': 'Amoxicilina', 'categoria': 'alergia', 'requiere_precaucion': True, 'orden': 2},
            {'nombre': 'Cefalosporinas', 'categoria': 'alergia', 'requiere_precaucion': True, 'orden': 3},
            {'nombre': 'Macrólidos (eritromicina, azitromicina)', 'categoria': 'alergia', 'requiere_precaucion': True, 'orden': 4},
            {'nombre': 'Anestésicos locales (lidocaína, articaína)', 'categoria': 'alergia', 'requiere_precaucion': True, 'orden': 5},
            {'nombre': 'Látex', 'categoria': 'alergia', 'requiere_precaucion': True, 'orden': 6},
            {'nombre': 'Metales (níquel, cromo)', 'categoria': 'alergia', 'requiere_precaucion': True, 'orden': 7},
            {'nombre': 'Yodo', 'categoria': 'alergia', 'requiere_precaucion': True, 'orden': 8},
            {'nombre': 'AINEs (ibuprofeno, diclofenac)', 'categoria': 'alergia', 'requiere_precaucion': True, 'orden': 9},
            {'nombre': 'Sulfonamidas', 'categoria': 'alergia', 'requiere_precaucion': True, 'orden': 10},
            
            # MEDICACIÓN ACTUAL
            {'nombre': 'Anticoagulantes (warfarina, acenocumarol)', 'categoria': 'medicacion', 'requiere_precaucion': True, 'orden': 1},
            {'nombre': 'Antiagregantes plaquetarios (aspirina, clopidogrel)', 'categoria': 'medicacion', 'requiere_precaucion': True, 'orden': 2},
            {'nombre': 'Corticoides', 'categoria': 'medicacion', 'requiere_precaucion': True, 'orden': 3},
            {'nombre': 'Bifosfonatos', 'categoria': 'medicacion', 'requiere_precaucion': True, 'orden': 4},
            {'nombre': 'Inmunosupresores', 'categoria': 'medicacion', 'requiere_precaucion': True, 'orden': 5},
            {'nombre': 'Antirretrovirales', 'categoria': 'medicacion', 'requiere_precaucion': True, 'orden': 6},
            {'nombre': 'Antihipertensivos', 'categoria': 'medicacion', 'requiere_precaucion': False, 'orden': 7},
            {'nombre': 'Hipoglucemiantes orales', 'categoria': 'medicacion', 'requiere_precaucion': True, 'orden': 8},
            {'nombre': 'Insulina', 'categoria': 'medicacion', 'requiere_precaucion': True, 'orden': 9},
            {'nombre': 'Antiepilépticos', 'categoria': 'medicacion', 'requiere_precaucion': True, 'orden': 10},
        ]
        
        creados = 0
        actualizados = 0
        
        for ant_data in antecedentes:
            antecedente, created = CategoriaAntecedente.objects.update_or_create(
                nombre=ant_data['nombre'],
                categoria=ant_data['categoria'],
                defaults={
                    'requiere_precaucion': ant_data['requiere_precaucion'],
                    'orden': ant_data['orden'],
                    'activo': True
                }
            )
            
            if created:
                creados += 1
                self.stdout.write(self.style.SUCCESS(f'✓ Creado: {ant_data["nombre"]}'))
            else:
                actualizados += 1
                self.stdout.write(self.style.WARNING(f'↻ Actualizado: {ant_data["nombre"]}'))
        
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS(f'Antecedentes creados: {creados}'))
        self.stdout.write(self.style.WARNING(f'Antecedentes actualizados: {actualizados}'))
        self.stdout.write(self.style.SUCCESS(f'Total procesado: {creados + actualizados}'))
        self.stdout.write('='*50)