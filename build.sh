#!/usr/bin/env bash
# Script de build para Render

set -o errexit

# Instalar dependencias
pip install -r requirements.txt

# Recolectar archivos estáticos
python manage.py collectstatic --no-input

# Ejecutar migraciones
python manage.py migrate

# Crear superusuario admin y poblar base de datos
python manage.py shell << EOF
from main.models import Usuario, Tutor, Asignatura, DisponibilidadTutor, SesionTutoria, RecursoEducativo, Carrera
from django.utils import timezone
from datetime import timedelta
import random

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
if not Usuario.objects.filter(rut='22072118-3').exists():
    admin = Usuario.objects.create_superuser(
        rut='22072118-3',
        username='22072118-3',
        email='basti@inacap.cl',
        password='gato1234',
        first_name='Admin',
        last_name='Sistema'
    )
    admin.is_staff = True
    admin.is_superuser = True
    admin.save()
    print('✅ Admin creado: 22072118-3 / gato1234')

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
    ('19111222-3', 'tutor1', 'Carlos', 'González', 'carlos.gonzalez@inacap.cl', ['Programación I', 'Programación II', 'Estructuras de Datos']),
    ('19222333-4', 'tutor2', 'María', 'Fernández', 'maria.fernandez@inacap.cl', ['Cálculo I', 'Cálculo II', 'Álgebra Lineal']),
    ('19333444-5', 'tutor3', 'Diego', 'Muñoz', 'diego.munoz@inacap.cl', ['Base de Datos', 'Redes de Computadores']),
    ('19444555-6', 'tutor4', 'Valentina', 'López', 'valentina.lopez@inacap.cl', ['Física I', 'Cálculo I']),
    ('19555666-7', 'tutor5', 'Sebastián', 'Rojas', 'sebastian.rojas@inacap.cl', ['Sistemas Operativos', 'Programación II']),
]

niveles = ['Novato', 'Principiante', 'Intermedio', 'Avanzado']
for rut, pwd, nombre, apellido, email, asigs in tutores_data:
    if not Usuario.objects.filter(rut=rut).exists():
        user = Usuario.objects.create_user(
            rut=rut,
            username=rut,
            email=email,
            password=pwd,
            first_name=nombre,
            last_name=apellido,
            es_tutor=True
        )
        tutor = Tutor.objects.create(
            usuario=user,
            nivel=random.choice(niveles),
            calificacion_promedio=round(random.uniform(3.5, 5.0), 1),
            horas_acumuladas=random.randint(10, 100),
            años_experiencia=random.randint(1, 5)
        )
        for asig_nombre in asigs:
            asig = Asignatura.objects.filter(nombre=asig_nombre).first()
            if asig:
                tutor.asignaturas.add(asig)
        
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
    Usuario.objects.get_or_create(
        rut=rut,
        defaults={
            'username': rut,
            'email': email,
            'first_name': nombre,
            'last_name': apellido,
            'es_tutor': False
        }
    )
    user = Usuario.objects.get(rut=rut)
    user.set_password(pwd)
    user.save()
print(f'✅ {Usuario.objects.filter(es_tutor=False, is_superuser=False).count()} estudiantes creados')

# ============================================
# CREAR SESIONES DE EJEMPLO
# ============================================
tutores = list(Tutor.objects.all())
estudiantes = list(Usuario.objects.filter(es_tutor=False, is_superuser=False))
asignaturas = list(Asignatura.objects.all())
estados = ['pendiente', 'aceptada', 'completada']

if SesionTutoria.objects.count() < 10:
    for i in range(15):
        tutor = random.choice(tutores)
        estudiante = random.choice(estudiantes)
        asignatura = random.choice(list(tutor.asignaturas.all())) if tutor.asignaturas.exists() else random.choice(asignaturas)
        estado = random.choice(estados)
        
        fecha = timezone.now() + timedelta(days=random.randint(-10, 10))
        
        SesionTutoria.objects.create(
            tutor=tutor,
            estudiante=estudiante,
            asignatura=asignatura,
            fecha_programada=fecha,
            duracion_minutos=random.choice([30, 45, 60, 90]),
            estado=estado,
            tema=f'Ayuda con {asignatura.nombre}',
            descripcion=f'Necesito reforzar conceptos de {asignatura.nombre}'
        )
    print(f'✅ {SesionTutoria.objects.count()} sesiones creadas')

# ============================================
# CREAR RECURSOS DE EJEMPLO
# ============================================
recursos_data = [
    ('Guía de Programación Python', 'documento', 'Programación I'),
    ('Video: Introducción a SQL', 'video', 'Base de Datos'),
    ('Ejercicios de Cálculo Resueltos', 'documento', 'Cálculo I'),
    ('Tutorial: Git y GitHub', 'enlace', 'Programación II'),
    ('Fórmulas de Física Mecánica', 'documento', 'Física I'),
    ('Curso de Estructuras de Datos', 'video', 'Estructuras de Datos'),
    ('Ejercicios de Álgebra', 'documento', 'Álgebra Lineal'),
    ('Manual de Redes TCP/IP', 'documento', 'Redes de Computadores'),
]

for titulo, tipo, asig_nombre in recursos_data:
    asig = Asignatura.objects.filter(nombre=asig_nombre).first()
    tutor = random.choice(tutores)
    RecursoEducativo.objects.get_or_create(
        titulo=titulo,
        defaults={
            'tipo': tipo,
            'descripcion': f'Material de apoyo para {asig_nombre}',
            'asignatura': asig,
            'subido_por': tutor,
            'descargas': random.randint(5, 50)
        }
    )
print(f'✅ {RecursoEducativo.objects.count()} recursos creados')

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
EOF

