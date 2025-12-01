from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from decimal import Decimal
from django.utils import timezone

class Usuario(AbstractUser):
    GENERO_CHOICES = [
        ('Masculino', 'Masculino'),
        ('Femenino', 'Femenino'),
        ('Otro', 'Otro'),
        ('Prefiero_no_decir', 'Prefiero no decir'),
    ]
    
    ESTADO_CHOICES = [
        ('Activo', 'Activo'),
        ('Egresado', 'Egresado'),
        ('Retirado', 'Retirado'),
        ('Suspendido', 'Suspendido'),
    ]

    rut = models.CharField(max_length=12, unique=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    genero = models.CharField(max_length=20, choices=GENERO_CHOICES, default='Prefiero_no_decir')
    sede = models.CharField(max_length=100, blank=True)
    carrera = models.CharField(max_length=100, blank=True)
    semestre_actual = models.PositiveIntegerField(default=1)
    promedio_general = models.DecimalField(max_digits=3, decimal_places=2, default=Decimal('4.00'))
    beneficio_gratuidad = models.BooleanField(default=False)
    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='Activo')
    fecha_ingreso = models.DateField(blank=True, null=True)
    es_tutor = models.BooleanField(default=False)

    USERNAME_FIELD = 'rut'
    REQUIRED_FIELDS = ['username', 'email', 'first_name', 'last_name']

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.rut
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.rut})"


class Sede(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    ciudad = models.CharField(max_length=50)
    region = models.CharField(max_length=50)
    direccion = models.TextField(blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} - {self.ciudad}"


class Carrera(models.Model):
    AREAS_CHOICES = [
        ('Tecnologia', 'Tecnología'),
        ('Administracion', 'Administración'),
        ('Construccion', 'Construcción'),
        ('Salud', 'Salud'),
        ('Gastronomia', 'Gastronomía'),
    ]
    
    nombre = models.CharField(max_length=150)
    codigo = models.CharField(max_length=20, unique=True)
    area = models.CharField(max_length=20, choices=AREAS_CHOICES)
    nivel = models.CharField(max_length=15)
    duracion_semestres = models.PositiveIntegerField()
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


class Asignatura(models.Model):
    nombre = models.CharField(max_length=150)
    codigo = models.CharField(max_length=20, unique=True)
    carrera = models.ForeignKey(Carrera, on_delete=models.CASCADE, related_name='asignaturas')
    semestre = models.PositiveIntegerField()
    es_critica = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} - {self.carrera.nombre}"


class Tutor(models.Model):
    NIVEL_CHOICES = [
        ('Novato', 'Novato'),
        ('Principiante', 'Principiante'),
        ('Intermedio', 'Intermedio'),
        ('Avanzado', 'Avanzado'),
        ('Erudito', 'Erudito'),
        ('Iluminado', 'Iluminado'),
    ]
    
    MODALIDAD_CHOICES = [
        ('Presencial', 'Presencial'),
        ('Online', 'Online'),
        ('Ambas', 'Ambas'),
    ]

    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='tutor_profile')
    fecha_certificacion = models.DateField()
    nivel = models.CharField(max_length=20, choices=NIVEL_CHOICES, default='Novato')
    años_experiencia = models.PositiveIntegerField(default=0)
    calificacion_promedio = models.DecimalField(max_digits=3, decimal_places=2, default=Decimal('4.00'))
    total_sesiones = models.PositiveIntegerField(default=0)
    horas_acumuladas = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.00'))
    especialidades = models.TextField(blank=True)
    modalidad_preferida = models.CharField(max_length=15, choices=MODALIDAD_CHOICES, default='Ambas')
    bio_descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"Tutor: {self.usuario.first_name} {self.usuario.last_name}"

    def actualizar_calificacion_promedio(self):
        """Calcula la calificación promedio del tutor"""
        sesiones = self.sesiones_como_tutor.filter(calificacion_tutor__isnull=False)
        if sesiones.exists():
            promedio = sesiones.aggregate(models.Avg('calificacion_tutor'))['calificacion_tutor__avg']
            self.calificacion_promedio = Decimal(str(promedio))
            self.save()


class DisponibilidadTutor(models.Model):
    DIAS_CHOICES = [
        ("Lunes", "Lunes"),
        ("Martes", "Martes"),
        ("Miércoles", "Miércoles"),
        ("Jueves", "Jueves"),
        ("Viernes", "Viernes"),
        ("Sábado", "Sábado"),
        ("Domingo", "Domingo")
    ]
    
    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE)
    dia = models.CharField(max_length=12, choices=DIAS_CHOICES, default='Lunes')
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    activo = models.BooleanField(default=True)

    class Meta:
        unique_together = ('tutor', 'dia', 'hora_inicio')

    def __str__(self):
        return f"{self.tutor.usuario.first_name} - {self.dia} {self.hora_inicio}"


class SesionTutoria(models.Model):
    MODALIDAD_CHOICES = [
        ('Presencial', 'Presencial'),
        ('Online', 'Online'),
    ]
    
    ESTADO_CHOICES = [
        ('Pendiente', 'Pendiente'),
        ('Aceptada', 'Aceptada'),
        ('Denegada', 'Denegada'),
        ('Completada', 'Completada'),
        ('Cancelada', 'Cancelada'),
        ('No_Show', 'No Show'),
    ]

    tutor = models.ForeignKey('Tutor', on_delete=models.PROTECT, related_name='sesiones_como_tutor')
    tutorado = models.ForeignKey('Usuario', on_delete=models.PROTECT, related_name='sesiones_como_estudiante')
    asignatura = models.ForeignKey('Asignatura', on_delete=models.PROTECT, related_name='sesiones')
    modalidad = models.CharField(max_length=15, choices=MODALIDAD_CHOICES)
    fecha_programada = models.DateTimeField()
    duracion_minutos = models.PositiveIntegerField(default=60)
    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='Pendiente')
    tema_solicitud = models.TextField()
    notas_tutor = models.TextField(blank=True)
    calificacion_tutor = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        blank=True, null=True
    )
    calificacion_tutorado = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        blank=True, null=True
    )
    fecha_inicio = models.DateTimeField(blank=True, null=True)
    fecha_fin = models.DateTimeField(blank=True, null=True)
    razon_rechazo = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        ordering = ['-fecha_programada']

    def __str__(self):
        return f"Sesión: {self.tutor.usuario.first_name} -> {self.tutorado.first_name} ({self.estado})"

    def esta_pasada(self):
        """Verifica si la sesión ya pasó"""
        return timezone.now() > self.fecha_programada

    def puede_ser_calificada(self):
        """Verifica si la sesión puede ser calificada"""
        return self.estado == 'Completada' and self.esta_pasada()


class Mensaje(models.Model):
    sesion = models.ForeignKey(SesionTutoria, on_delete=models.CASCADE, related_name='mensajes')
    remitente = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    mensaje = models.TextField()
    fecha_envio = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['fecha_envio']

    def __str__(self):
        return f"Mensaje de {self.remitente} en sesión {self.sesion.id}"


class RecursoEducativo(models.Model):
    TIPO_CHOICES = [
        ('Guia', 'Guía'),
        ('Ejercicios', 'Ejercicios'),
        ('Video', 'Video'),
        ('Presentacion', 'Presentación'),
        ('Documento', 'Documento'),
        ('Otro', 'Otro'),
    ]

    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE, related_name='recursos')
    asignatura = models.ForeignKey(Asignatura, on_delete=models.CASCADE, related_name='recursos')
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    tipo = models.CharField(max_length=15, choices=TIPO_CHOICES)
    archivo = models.FileField(upload_to='recursos/', blank=True, null=True)
    contenido = models.TextField(blank=True)
    descargas = models.PositiveIntegerField(default=0)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.titulo} - {self.asignatura.nombre}"


class Logro(models.Model):
    CATEGORIA_CHOICES = [
        ('Sesiones', 'Sesiones'),
        ('Calidad', 'Calidad'),
        ('Tiempo', 'Tiempo'),
        ('Especialidad', 'Especialidad'),
        ('Comunidad', 'Comunidad'),
    ]

    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField()
    categoria = models.CharField(max_length=15, choices=CATEGORIA_CHOICES)
    puntos = models.PositiveIntegerField(default=10)
    icono = models.CharField(max_length=10, default='🏆')
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


class UsuarioLogro(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='logros')
    logro = models.ForeignKey(Logro, on_delete=models.CASCADE, related_name='usuarios')
    fecha_obtencion = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('usuario', 'logro')]

    def __str__(self):
        return f"{self.usuario.first_name} - {self.logro.nombre}"


class Notificacion(models.Model):
    TIPO_CHOICES = [
        ('Sesion_Agendada', 'Sesión Agendada'),
        ('Sesion_Aceptada', 'Sesión Aceptada'),
        ('Sesion_Rechazada', 'Sesión Rechazada'),
        ('Recordatorio', 'Recordatorio'),
        ('Cancelacion', 'Cancelación'),
        ('Evaluacion', 'Evaluación'),
        ('Logro', 'Logro'),
        ('Sistema', 'Sistema'),
    ]

    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='notificaciones')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    titulo = models.CharField(max_length=200)
    mensaje = models.TextField()
    leida = models.BooleanField(default=False)
    sesion = models.ForeignKey(SesionTutoria, null=True, blank=True, on_delete=models.CASCADE)
    fecha_envio = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha_envio']

    def __str__(self):
        return f"{self.titulo} - {self.usuario.first_name}"