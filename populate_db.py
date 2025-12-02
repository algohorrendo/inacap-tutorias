#!/usr/bin/env python
"""
Script para poblar la base de datos con datos de ejemplo
Se ejecuta automáticamente durante el build en Railway
"""
import os
import django
import random
from datetime import date, timedelta
from decimal import Decimal

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inacap_tutorias.settings')
django.setup()

from main.models import Usuario, Tutor, Asignatura, DisponibilidadTutor, SesionTutoria, RecursoEducativo, Carrera
from django.utils import timezone

print('=' * 50)
print('📊 POBLANDO BASE DE DATOS...')
print('=' * 50)

# ============================================
# CREAR CARRERA
# ============================================
carrera, _ = Carrera.objects.get_or_create(
    codigo='INFO',
    defaults={
        'nombre': 'Ingeniería en Informática',
        'area': 'Tecnologia',
        'nivel': 'Profesional',
        'duracion_semestres': 8,
        'activo': True
    }
)
print(f'✅ Carrera creada: {carrera.nombre}')

# ============================================
# CREAR ADMIN
# ============================================
admin, created = Usuario.objects.get_or_create(
    rut='22072118-3',
    defaults={
        'username': '22072118-3',
        'email': 'basti@inacap.cl',
        'first_name': 'Admin',
        'last_name': 'Sistema',
        'is_staff': True,
        'is_superuser': True
    }
)
admin.set_password('gato1234')
admin.is_staff = True
admin.is_superuser = True
admin.save()
print('✅ Admin creado/actualizado: 22072118-3 / gato1234')

# ============================================
# CREAR ASIGNATURAS
# ============================================
asignaturas_data = [
    ('Programación I', 'INFO101', 1),
    ('Programación II', 'INFO102', 2),
    ('Base de Datos', 'INFO201', 3),
    ('Cálculo I', 'MAT101', 1),
    ('Cálculo II', 'MAT102', 2),
    ('Física I', 'FIS101', 2),
    ('Álgebra Lineal', 'MAT103', 1),
    ('Estructuras de Datos', 'INFO202', 3),
    ('Redes de Computadores', 'INFO301', 5),
    ('Sistemas Operativos', 'INFO302', 4),
]

for nombre, codigo, semestre in asignaturas_data:
    Asignatura.objects.get_or_create(
        codigo=codigo,
        defaults={
            'nombre': nombre,
            'carrera': carrera,
            'semestre': semestre,
            'es_critica': semestre <= 2,
            'activo': True
        }
    )
print(f'✅ {Asignatura.objects.count()} asignaturas creadas')

# ============================================
# CREAR TUTORES
# ============================================
tutores_data = [
    ('19111222-3', 'tutor1', 'Carlos', 'González', 'carlos.gonzalez@inacap.cl', 'Programación, Python, Java'),
    ('19222333-4', 'tutor2', 'María', 'Fernández', 'maria.fernandez@inacap.cl', 'Cálculo, Álgebra, Matemáticas'),
    ('19333444-5', 'tutor3', 'Diego', 'Muñoz', 'diego.munoz@inacap.cl', 'Base de Datos, SQL, PostgreSQL'),
    ('19444555-6', 'tutor4', 'Valentina', 'López', 'valentina.lopez@inacap.cl', 'Física, Cálculo, Ciencias'),
    ('19555666-7', 'tutor5', 'Sebastián', 'Rojas', 'sebastian.rojas@inacap.cl', 'Sistemas Operativos, Linux, Redes'),
]

niveles = ['Novato', 'Principiante', 'Intermedio', 'Avanzado']
modalidades = ['Presencial', 'Online', 'Ambas']

for rut, pwd, nombre, apellido, email, especialidades in tutores_data:
    user, user_created = Usuario.objects.get_or_create(
        rut=rut,
        defaults={
            'username': rut,
            'email': email,
            'first_name': nombre,
            'last_name': apellido,
            'es_tutor': True
        }
    )
    user.set_password(pwd)
    user.save()
    
    tutor, tutor_created = Tutor.objects.get_or_create(
        usuario=user,
        defaults={
            'fecha_certificacion': date(2024, random.randint(1, 12), random.randint(1, 28)),
            'nivel': random.choice(niveles),
            'años_experiencia': random.randint(1, 5),
            'calificacion_promedio': Decimal(str(round(random.uniform(3.5, 5.0), 2))),
            'total_sesiones': random.randint(5, 50),
            'horas_acumuladas': Decimal(str(random.randint(10, 200))),
            'especialidades': especialidades,
            'modalidad_preferida': random.choice(modalidades),
            'bio_descripcion': f'Tutor especializado en {especialidades.split(",")[0]}',
            'activo': True
        }
    )
    
    # Crear disponibilidad para el tutor
    dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
    for dia in random.sample(dias, 3):
        DisponibilidadTutor.objects.get_or_create(
            tutor=tutor,
            dia=dia,
            defaults={
                'hora_inicio': '09:00',
                'hora_fin': '18:00',
                'activo': True
            }
        )
print(f'✅ {Tutor.objects.count()} tutores creados')

# ============================================
# CREAR ESTUDIANTES
# ============================================
estudiantes_data = [
    ('20111222-3', 'est1', 'Juan', 'Pérez', 'juan.perez@inacap.cl'),
    ('20222333-4', 'est2', 'Ana', 'Silva', 'ana.silva@inacap.cl'),
    ('20333444-5', 'est3', 'Pedro', 'Martínez', 'pedro.martinez@inacap.cl'),
    ('20444555-6', 'est4', 'Camila', 'Vargas', 'camila.vargas@inacap.cl'),
    ('20555666-7', 'est5', 'Felipe', 'Soto', 'felipe.soto@inacap.cl'),
    ('20666777-8', 'est6', 'Javiera', 'Reyes', 'javiera.reyes@inacap.cl'),
    ('20777888-9', 'est7', 'Matías', 'Torres', 'matias.torres@inacap.cl'),
    ('20888999-0', 'est8', 'Francisca', 'Díaz', 'francisca.diaz@inacap.cl'),
]

for rut, pwd, nombre, apellido, email in estudiantes_data:
    user, created = Usuario.objects.get_or_create(
        rut=rut,
        defaults={
            'username': rut,
            'email': email,
            'first_name': nombre,
            'last_name': apellido,
            'es_tutor': False
        }
    )
    user.set_password(pwd)
    user.save()
print(f'✅ {Usuario.objects.filter(es_tutor=False, is_superuser=False).count()} estudiantes creados')

# ============================================
# CREAR SESIONES DE EJEMPLO
# ============================================
tutores = list(Tutor.objects.all())
estudiantes = list(Usuario.objects.filter(es_tutor=False, is_superuser=False))
asignaturas = list(Asignatura.objects.all())
estados = ['Pendiente', 'Aceptada', 'Completada']
modalidades_sesion = ['Presencial', 'Online']

if SesionTutoria.objects.count() < 10 and tutores and estudiantes and asignaturas:
    for i in range(15):
        tutor = random.choice(tutores)
        estudiante = random.choice(estudiantes)
        asignatura = random.choice(asignaturas)
        estado = random.choice(estados)
        
        fecha = timezone.now() + timedelta(days=random.randint(-10, 10))
        
        SesionTutoria.objects.get_or_create(
            tutor=tutor,
            tutorado=estudiante,
            asignatura=asignatura,
            defaults={
                'modalidad': random.choice(modalidades_sesion),
                'fecha_programada': fecha,
                'duracion_minutos': random.choice([30, 45, 60, 90]),
                'estado': estado,
                'tema_solicitud': f'Ayuda con {asignatura.nombre}',
                'notas_tutor': ''
            }
        )
    print(f'✅ {SesionTutoria.objects.count()} sesiones creadas')
else:
    print('ℹ️ No se crearon sesiones (faltan datos base o ya existen)')

# ============================================
# CREAR RECURSOS DE EJEMPLO
# ============================================
recursos_data = [
    ('Guía de Programación Python', 'Guia', 'INFO101'),
    ('Video: Introducción a SQL', 'Video', 'INFO201'),
    ('Ejercicios de Cálculo Resueltos', 'Ejercicios', 'MAT101'),
    ('Tutorial: Git y GitHub', 'Documento', 'INFO102'),
    ('Fórmulas de Física Mecánica', 'Documento', 'FIS101'),
    ('Curso de Estructuras de Datos', 'Video', 'INFO202'),
    ('Ejercicios de Álgebra', 'Ejercicios', 'MAT103'),
    ('Manual de Redes TCP/IP', 'Documento', 'INFO301'),
]

tutores_lista = list(Tutor.objects.all())
if tutores_lista and RecursoEducativo.objects.count() < 10:
    for titulo, tipo, asig_codigo in recursos_data:
        asig = Asignatura.objects.filter(codigo=asig_codigo).first()
        tutor = random.choice(tutores_lista)
        if asig:
            RecursoEducativo.objects.get_or_create(
                titulo=titulo,
                defaults={
                    'tutor': tutor,
                    'asignatura': asig,
                    'tipo': tipo,
                    'descripcion': f'Material de apoyo para {asig.nombre}',
                    'contenido': f'Contenido educativo sobre {asig.nombre}',
                    'descargas': random.randint(5, 50),
                    'activo': True
                }
            )
    print(f'✅ {RecursoEducativo.objects.count()} recursos creados')
else:
    print('ℹ️ No se crearon recursos (faltan tutores o ya existen)')

print('')
print('=' * 50)
print('📋 CREDENCIALES DE ACCESO:')
print('=' * 50)
print('ADMIN:      22072118-3 / gato1234')
print('')
print('TUTORES:')
print('  Carlos:   19111222-3 / tutor1')
print('  María:    19222333-4 / tutor2')
print('  Diego:    19333444-5 / tutor3')
print('  Valentina: 19444555-6 / tutor4')
print('  Sebastián: 19555666-7 / tutor5')
print('')
print('ESTUDIANTES:')
print('  Juan:     20111222-3 / est1')
print('  Ana:      20222333-4 / est2')
print('  Pedro:    20333444-5 / est3')
print('  Camila:   20444555-6 / est4')
print('  Felipe:   20555666-7 / est5')
print('=' * 50)
print('✅ Base de datos poblada exitosamente')

