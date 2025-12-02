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

from main.models import (
    Usuario, Tutor, Asignatura, DisponibilidadTutor, SesionTutoria, 
    RecursoEducativo, Carrera, Sede, Mensaje, Logro, UsuarioLogro, Notificacion
)
from django.utils import timezone

print('=' * 50)
print('📊 POBLANDO BASE DE DATOS...')
print('=' * 50)

# ============================================
# CREAR SEDES
# ============================================
sedes_data = [
    ('INACAP Santiago Centro', 'Santiago', 'Región Metropolitana', 'Av. Ejército 146, Santiago', '+56 2 2345 6789', 'santiago.centro@inacap.cl'),
    ('INACAP Valparaíso', 'Valparaíso', 'Región de Valparaíso', 'Av. Brasil 1160, Valparaíso', '+56 32 234 5678', 'valparaiso@inacap.cl'),
    ('INACAP Concepción', 'Concepción', 'Región del Biobío', 'Av. O\'Higgins 501, Concepción', '+56 41 234 5678', 'concepcion@inacap.cl'),
    ('INACAP Temuco', 'Temuco', 'Región de La Araucanía', 'Av. Alemania 0280, Temuco', '+56 45 234 5678', 'temuco@inacap.cl'),
]

for nombre, ciudad, region, direccion, telefono, email in sedes_data:
    Sede.objects.get_or_create(
        nombre=nombre,
        defaults={
            'ciudad': ciudad,
            'region': region,
            'direccion': direccion,
            'telefono': telefono,
            'email': email,
            'activo': True
        }
    )
print(f'✅ {Sede.objects.count()} sedes creadas')

# ============================================
# CREAR CARRERAS
# ============================================
carreras_data = [
    ('Ingeniería en Informática', 'INFO', 'Tecnologia', 'Profesional', 8),
    ('Ingeniería en Administración', 'ADMIN', 'Administracion', 'Profesional', 8),
    ('Ingeniería en Construcción', 'CONST', 'Construccion', 'Profesional', 10),
    ('Enfermería', 'ENF', 'Salud', 'Profesional', 10),
    ('Gastronomía Internacional', 'GAST', 'Gastronomia', 'Técnico', 6),
    ('Ingeniería Industrial', 'IND', 'Administracion', 'Profesional', 8),
]

carreras_objs = []
for nombre, codigo, area, nivel, duracion in carreras_data:
    carrera, _ = Carrera.objects.get_or_create(
        codigo=codigo,
        defaults={
            'nombre': nombre,
            'area': area,
            'nivel': nivel,
            'duracion_semestres': duracion,
            'activo': True
        }
    )
    carreras_objs.append(carrera)
print(f'✅ {Carrera.objects.count()} carreras creadas')
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
    # Informática
    ('Programación I', 'INFO101', 'INFO', 1),
    ('Programación II', 'INFO102', 'INFO', 2),
    ('Base de Datos', 'INFO201', 'INFO', 3),
    ('Estructuras de Datos', 'INFO202', 'INFO', 3),
    ('Redes de Computadores', 'INFO301', 'INFO', 5),
    ('Sistemas Operativos', 'INFO302', 'INFO', 4),
    ('Ingeniería de Software', 'INFO303', 'INFO', 6),
    # Matemáticas (comunes)
    ('Cálculo I', 'MAT101', 'INFO', 1),
    ('Cálculo II', 'MAT102', 'INFO', 2),
    ('Álgebra Lineal', 'MAT103', 'INFO', 1),
    # Física
    ('Física I', 'FIS101', 'INFO', 2),
    # Administración
    ('Contabilidad General', 'ADMIN101', 'ADMIN', 1),
    ('Gestión de Recursos Humanos', 'ADMIN201', 'ADMIN', 3),
    ('Marketing Digital', 'ADMIN202', 'ADMIN', 4),
    # Construcción
    ('Materiales de Construcción', 'CONST101', 'CONST', 1),
    ('Estructuras', 'CONST201', 'CONST', 3),
    # Salud
    ('Anatomía y Fisiología', 'ENF101', 'ENF', 1),
    ('Fundamentos de Enfermería', 'ENF102', 'ENF', 1),
    # Gastronomía
    ('Técnicas Culinarias Básicas', 'GAST101', 'GAST', 1),
    ('Pastelería y Repostería', 'GAST201', 'GAST', 3),
]

for nombre, codigo, carrera_codigo, semestre in asignaturas_data:
    carrera_obj = next((c for c in carreras_objs if c.codigo == carrera_codigo), carreras_objs[0])
    Asignatura.objects.get_or_create(
        codigo=codigo,
        defaults={
            'nombre': nombre,
            'carrera': carrera_obj,
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
    ('19111222-3', 'tutor1', 'Carlos', 'González', 'carlos.gonzalez@inacap.cl', 'Programación, Python, Java', 'Masculino', 'Santiago Centro'),
    ('19222333-4', 'tutor2', 'María', 'Fernández', 'maria.fernandez@inacap.cl', 'Cálculo, Álgebra, Matemáticas', 'Femenino', 'Santiago Centro'),
    ('19333444-5', 'tutor3', 'Diego', 'Muñoz', 'diego.munoz@inacap.cl', 'Base de Datos, SQL, PostgreSQL', 'Masculino', 'Valparaíso'),
    ('19444555-6', 'tutor4', 'Valentina', 'López', 'valentina.lopez@inacap.cl', 'Física, Cálculo, Ciencias', 'Femenino', 'Concepción'),
    ('19555666-7', 'tutor5', 'Sebastián', 'Rojas', 'sebastian.rojas@inacap.cl', 'Sistemas Operativos, Linux, Redes', 'Masculino', 'Santiago Centro'),
    ('19666777-8', 'tutor6', 'Isabella', 'Morales', 'isabella.morales@inacap.cl', 'Marketing, Administración, Gestión', 'Femenino', 'Temuco'),
    ('19777888-9', 'tutor7', 'Andrés', 'Castro', 'andres.castro@inacap.cl', 'Construcción, Materiales, Estructuras', 'Masculino', 'Santiago Centro'),
]

niveles = ['Novato', 'Principiante', 'Intermedio', 'Avanzado', 'Erudito']
modalidades = ['Presencial', 'Online', 'Ambas']
generos = ['Masculino', 'Femenino']
sedes_list = list(Sede.objects.all())

for rut, pwd, nombre, apellido, email, especialidades, genero, sede_nombre in tutores_data:
    sede_obj = next((s for s in sedes_list if sede_nombre in s.nombre), sedes_list[0] if sedes_list else None)
    carrera_obj = random.choice(carreras_objs)
    
    user, user_created = Usuario.objects.get_or_create(
        rut=rut,
        defaults={
            'username': rut,
            'email': email,
            'first_name': nombre,
            'last_name': apellido,
            'es_tutor': True,
            'telefono': f'+56 9 {random.randint(10000000, 99999999)}',
            'fecha_nacimiento': date(1990 + random.randint(0, 10), random.randint(1, 12), random.randint(1, 28)),
            'genero': genero,
            'sede': sede_obj.nombre if sede_obj else 'Santiago Centro',
            'carrera': carrera_obj.nombre,
            'semestre_actual': random.randint(5, 8),
            'promedio_general': Decimal(str(round(random.uniform(4.5, 6.0), 2))),
            'beneficio_gratuidad': random.choice([True, False]),
            'estado': 'Activo',
            'fecha_ingreso': date(2020 + random.randint(0, 3), 1, 1),
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
            'bio_descripcion': f'Tutor especializado en {especialidades.split(",")[0]} con {random.randint(1, 5)} años de experiencia',
            'activo': True
        }
    )
    
    # Crear disponibilidad para el tutor
    dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
    horas_inicio = ['09:00', '10:00', '14:00', '15:00']
    horas_fin = ['12:00', '13:00', '17:00', '18:00']
    for dia in random.sample(dias, random.randint(2, 4)):
        DisponibilidadTutor.objects.get_or_create(
            tutor=tutor,
            dia=dia,
            hora_inicio=random.choice(horas_inicio),
            defaults={
                'hora_fin': random.choice(horas_fin),
                'activo': True
            }
        )
print(f'✅ {Tutor.objects.count()} tutores creados')
print(f'✅ {DisponibilidadTutor.objects.count()} disponibilidades creadas')

# ============================================
# CREAR ESTUDIANTES
# ============================================
estudiantes_data = [
    ('20111222-3', 'est1', 'Juan', 'Pérez', 'juan.perez@inacap.cl', 'Masculino', 'Santiago Centro', 'INFO'),
    ('20222333-4', 'est2', 'Ana', 'Silva', 'ana.silva@inacap.cl', 'Femenino', 'Santiago Centro', 'INFO'),
    ('20333444-5', 'est3', 'Pedro', 'Martínez', 'pedro.martinez@inacap.cl', 'Masculino', 'Valparaíso', 'ADMIN'),
    ('20444555-6', 'est4', 'Camila', 'Vargas', 'camila.vargas@inacap.cl', 'Femenino', 'Concepción', 'INFO'),
    ('20555666-7', 'est5', 'Felipe', 'Soto', 'felipe.soto@inacap.cl', 'Masculino', 'Santiago Centro', 'CONST'),
    ('20666777-8', 'est6', 'Javiera', 'Reyes', 'javiera.reyes@inacap.cl', 'Femenino', 'Temuco', 'ENF'),
    ('20777888-9', 'est7', 'Matías', 'Torres', 'matias.torres@inacap.cl', 'Masculino', 'Santiago Centro', 'INFO'),
    ('20888999-0', 'est8', 'Francisca', 'Díaz', 'francisca.diaz@inacap.cl', 'Femenino', 'Valparaíso', 'GAST'),
    ('20999000-1', 'est9', 'Tomás', 'Gutiérrez', 'tomas.gutierrez@inacap.cl', 'Masculino', 'Concepción', 'ADMIN'),
    ('21000111-2', 'est10', 'Catalina', 'Moreno', 'catalina.moreno@inacap.cl', 'Femenino', 'Santiago Centro', 'INFO'),
]

for rut, pwd, nombre, apellido, email, genero, sede_nombre, carrera_codigo in estudiantes_data:
    sede_obj = next((s for s in sedes_list if sede_nombre in s.nombre), sedes_list[0] if sedes_list else None)
    carrera_obj = next((c for c in carreras_objs if c.codigo == carrera_codigo), carreras_objs[0])
    
    user, created = Usuario.objects.get_or_create(
        rut=rut,
        defaults={
            'username': rut,
            'email': email,
            'first_name': nombre,
            'last_name': apellido,
            'es_tutor': False,
            'telefono': f'+56 9 {random.randint(10000000, 99999999)}',
            'fecha_nacimiento': date(2000 + random.randint(0, 5), random.randint(1, 12), random.randint(1, 28)),
            'genero': genero,
            'sede': sede_obj.nombre if sede_obj else 'Santiago Centro',
            'carrera': carrera_obj.nombre,
            'semestre_actual': random.randint(1, 6),
            'promedio_general': Decimal(str(round(random.uniform(3.5, 6.0), 2))),
            'beneficio_gratuidad': random.choice([True, False]),
            'estado': 'Activo',
            'fecha_ingreso': date(2022 + random.randint(0, 2), 1, 1),
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
estados = ['Pendiente', 'Aceptada', 'Completada', 'Cancelada']
modalidades_sesion = ['Presencial', 'Online']

if SesionTutoria.objects.count() < 20 and tutores and estudiantes and asignaturas:
    for i in range(25):
        tutor = random.choice(tutores)
        estudiante = random.choice(estudiantes)
        asignatura = random.choice(asignaturas)
        estado = random.choice(estados)
        
        fecha = timezone.now() + timedelta(days=random.randint(-15, 15))
        
        sesion, created = SesionTutoria.objects.get_or_create(
            tutor=tutor,
            tutorado=estudiante,
            asignatura=asignatura,
            fecha_programada=fecha,
            defaults={
                'modalidad': random.choice(modalidades_sesion),
                'duracion_minutos': random.choice([30, 45, 60, 90]),
                'estado': estado,
                'tema_solicitud': f'Ayuda con {asignatura.nombre} - {random.choice(["Conceptos básicos", "Ejercicios prácticos", "Preparación para examen", "Repaso general"])}',
                'notas_tutor': random.choice(['', 'Sesión productiva', 'Estudiante muy participativo', 'Requiere más práctica']) if estado == 'Completada' else '',
                'calificacion_tutor': random.randint(3, 5) if estado == 'Completada' and random.choice([True, False]) else None,
                'calificacion_tutorado': random.randint(4, 5) if estado == 'Completada' and random.choice([True, False]) else None,
                'fecha_inicio': fecha - timedelta(minutes=5) if estado == 'Completada' else None,
                'fecha_fin': fecha + timedelta(minutes=random.choice([30, 45, 60, 90])) if estado == 'Completada' else None,
            }
        )
        
        # Crear mensajes para algunas sesiones
        if created and estado in ['Aceptada', 'Completada'] and random.choice([True, False]):
            Mensaje.objects.get_or_create(
                sesion=sesion,
                remitente=tutor.usuario,
                defaults={
                    'mensaje': f'Hola {estudiante.first_name}, confirmo nuestra sesión de {asignatura.nombre} para el {fecha.strftime("%d/%m/%Y")} a las {fecha.strftime("%H:%M")}.',
                    'fecha_envio': fecha - timedelta(days=1)
                }
            )
            
            if random.choice([True, False]):
                Mensaje.objects.get_or_create(
                    sesion=sesion,
                    remitente=estudiante,
                    defaults={
                        'mensaje': 'Perfecto, estaré ahí. Gracias!',
                        'fecha_envio': fecha - timedelta(hours=12)
                    }
                )
    print(f'✅ {SesionTutoria.objects.count()} sesiones creadas')
    print(f'✅ {Mensaje.objects.count()} mensajes creados')
else:
    print('ℹ️ No se crearon sesiones (faltan datos base o ya existen)')

# ============================================
# CREAR RECURSOS DE EJEMPLO
# ============================================
recursos_data = [
    ('Guía de Programación Python', 'Guia', 'INFO101', 'Guía completa de Python desde cero hasta nivel intermedio'),
    ('Video: Introducción a SQL', 'Video', 'INFO201', 'Tutorial en video sobre consultas SQL básicas y avanzadas'),
    ('Ejercicios de Cálculo Resueltos', 'Ejercicios', 'MAT101', 'Colección de ejercicios de cálculo diferencial con soluciones paso a paso'),
    ('Tutorial: Git y GitHub', 'Documento', 'INFO102', 'Manual completo sobre control de versiones con Git'),
    ('Fórmulas de Física Mecánica', 'Documento', 'FIS101', 'Resumen de fórmulas y conceptos clave de física mecánica'),
    ('Curso de Estructuras de Datos', 'Video', 'INFO202', 'Serie de videos explicando listas, pilas, colas y árboles'),
    ('Ejercicios de Álgebra', 'Ejercicios', 'MAT103', 'Problemas de álgebra lineal con soluciones detalladas'),
    ('Manual de Redes TCP/IP', 'Documento', 'INFO301', 'Documentación completa sobre protocolos de red'),
    ('Presentación: Marketing Digital', 'Presentacion', 'ADMIN202', 'Slides sobre estrategias de marketing digital'),
    ('Guía de Materiales de Construcción', 'Guia', 'CONST101', 'Catálogo y características de materiales de construcción'),
    ('Video: Técnicas Culinarias', 'Video', 'GAST101', 'Tutorial práctico de técnicas básicas de cocina'),
    ('Apuntes de Anatomía', 'Documento', 'ENF101', 'Resumen de conceptos de anatomía humana'),
]

tutores_lista = list(Tutor.objects.all())
if tutores_lista and RecursoEducativo.objects.count() < 15:
    for titulo, tipo, asig_codigo, descripcion in recursos_data:
        asig = Asignatura.objects.filter(codigo=asig_codigo).first()
        tutor = random.choice(tutores_lista)
        if asig:
            RecursoEducativo.objects.get_or_create(
                titulo=titulo,
                defaults={
                    'tutor': tutor,
                    'asignatura': asig,
                    'tipo': tipo,
                    'descripcion': descripcion,
                    'contenido': f'Contenido educativo detallado sobre {asig.nombre}. {descripcion}',
                    'descargas': random.randint(5, 150),
                    'activo': True
                }
            )
    print(f'✅ {RecursoEducativo.objects.count()} recursos creados')
else:
    print('ℹ️ No se crearon recursos (faltan tutores o ya existen)')

# ============================================
# CREAR LOGROS
# ============================================
logros_data = [
    ('Primera Sesión', 'Completa tu primera sesión de tutoría', 'Sesiones', 10, '🎯'),
    ('5 Sesiones', 'Completa 5 sesiones de tutoría', 'Sesiones', 25, '⭐'),
    ('10 Sesiones', 'Completa 10 sesiones de tutoría', 'Sesiones', 50, '🌟'),
    ('Tutor Estrella', 'Obtén una calificación promedio de 4.5 o más', 'Calidad', 75, '⭐'),
    ('Tutor Excepcional', 'Obtén una calificación promedio de 5.0', 'Calidad', 100, '🏆'),
    ('Puntual', 'Completa 10 sesiones sin cancelar', 'Tiempo', 30, '⏰'),
    ('Especialista', 'Tutorea en 3 asignaturas diferentes', 'Especialidad', 40, '📚'),
    ('Comunidad', 'Ayuda a 5 estudiantes diferentes', 'Comunidad', 60, '👥'),
    ('Experto', 'Completa 50 horas de tutoría', 'Tiempo', 100, '💎'),
    ('Mentor', 'Obtén 20 calificaciones positivas', 'Calidad', 80, '🎓'),
]

for nombre, descripcion, categoria, puntos, icono in logros_data:
    Logro.objects.get_or_create(
        nombre=nombre,
        defaults={
            'descripcion': descripcion,
            'categoria': categoria,
            'puntos': puntos,
            'icono': icono,
            'activo': True
        }
    )
print(f'✅ {Logro.objects.count()} logros creados')

# ============================================
# ASIGNAR LOGROS A USUARIOS
# ============================================
logros_lista = list(Logro.objects.all())
tutores_con_sesiones = Tutor.objects.filter(total_sesiones__gte=5)

for tutor in tutores_con_sesiones[:5]:  # Asignar logros a algunos tutores
    logros_para_asignar = random.sample(logros_lista, min(3, len(logros_lista)))
    for logro in logros_para_asignar:
        UsuarioLogro.objects.get_or_create(
            usuario=tutor.usuario,
            logro=logro,
            defaults={
                'fecha_obtencion': timezone.now() - timedelta(days=random.randint(1, 30))
            }
        )
print(f'✅ {UsuarioLogro.objects.count()} logros asignados a usuarios')

# ============================================
# CREAR NOTIFICACIONES
# ============================================
tipos_notificacion = [
    ('Sesion_Agendada', 'Sesión Agendada', 'Tu sesión de tutoría ha sido agendada exitosamente'),
    ('Sesion_Aceptada', 'Sesión Aceptada', 'El tutor ha aceptado tu solicitud de sesión'),
    ('Recordatorio', 'Recordatorio', 'Recuerda que tienes una sesión programada mañana'),
    ('Evaluacion', 'Evaluación', 'Por favor califica tu última sesión de tutoría'),
    ('Logro', 'Logro Desbloqueado', '¡Felicidades! Has obtenido un nuevo logro'),
    ('Sistema', 'Bienvenido', 'Bienvenido a la plataforma de tutorías INACAP'),
]

sesiones_con_notificaciones = SesionTutoria.objects.all()[:10]
usuarios_todos = list(Usuario.objects.all())

# Notificaciones para sesiones
for sesion in sesiones_con_notificaciones:
    if sesion.estado == 'Aceptada':
        Notificacion.objects.get_or_create(
            usuario=sesion.tutorado,
            sesion=sesion,
            tipo='Sesion_Aceptada',
            defaults={
                'titulo': 'Sesión Aceptada',
                'mensaje': f'El tutor {sesion.tutor.usuario.first_name} ha aceptado tu solicitud de sesión para {sesion.asignatura.nombre}',
                'leida': random.choice([True, False]),
                'fecha_envio': sesion.fecha_programada - timedelta(days=2)
            }
        )
    
    if sesion.estado == 'Completada' and random.choice([True, False]):
        Notificacion.objects.get_or_create(
            usuario=sesion.tutorado,
            sesion=sesion,
            tipo='Evaluacion',
            defaults={
                'titulo': 'Evalúa tu Sesión',
                'mensaje': f'Por favor califica tu sesión de {sesion.asignatura.nombre} con {sesion.tutor.usuario.first_name}',
                'leida': False,
                'fecha_envio': sesion.fecha_programada + timedelta(hours=1)
            }
        )

# Notificaciones de recordatorio
for usuario in usuarios_todos[:5]:
    Notificacion.objects.get_or_create(
        usuario=usuario,
        tipo='Recordatorio',
        defaults={
            'titulo': 'Recordatorio de Sesión',
            'mensaje': 'Tienes una sesión programada para mañana. ¡No olvides asistir!',
            'leida': False,
            'fecha_envio': timezone.now() - timedelta(hours=random.randint(1, 12))
        }
    )

# Notificaciones de logros
for usuario_logro in UsuarioLogro.objects.all()[:5]:
    Notificacion.objects.get_or_create(
        usuario=usuario_logro.usuario,
        tipo='Logro',
        defaults={
            'titulo': f'Logro: {usuario_logro.logro.nombre}',
            'mensaje': f'¡Felicidades! Has obtenido el logro "{usuario_logro.logro.nombre}"',
            'leida': False,
            'fecha_envio': usuario_logro.fecha_obtencion
        }
    )

print(f'✅ {Notificacion.objects.count()} notificaciones creadas')

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

