from django.contrib import admin
from django.contrib.auth.models import Group, Permission
from django.utils.html import format_html
from django.db.models import Q, Count
from .models import *

# ===========================================
# CONFIGURACIÓN DE GRUPOS Y PERMISOS
# ===========================================
def setup_groups():
    """Crear grupos con permisos predefinidos"""
    # Grupo Tutores
    tutores_group, created = Group.objects.get_or_create(name='Tutores')
    if created:
        permisos_tutores = Permission.objects.filter(
            codename__in=[
                'add_recurso_educativo',
                'change_recurso_educativo',
                'delete_recurso_educativo',
                'view_sesiontutoria',
                'change_sesiontutoria',
                'view_disponibilidadtutor',
                'add_disponibilidadtutor',
                'change_disponibilidadtutor',
                'delete_disponibilidadtutor',
                'view_notificacion',
            ]
        )
        tutores_group.permissions.set(permisos_tutores)

    # Grupo Estudiantes
    estudiantes_group, created = Group.objects.get_or_create(name='Estudiantes')
    if created:
        permisos_estudiantes = Permission.objects.filter(
            codename__in=[
                'view_tutor',
                'view_sesiontutoria',
                'add_sesiontutoria',
                'change_sesiontutoria',
                'view_recurso_educativo',
                'view_notificacion',
            ]
        )
        estudiantes_group.permissions.set(permisos_estudiantes)

# Ejecutar al iniciar Django
try:
    setup_groups()
except:
    pass


# ===========================================
# FILTROS PERSONALIZADOS
# ===========================================
class RolFilter(admin.SimpleListFilter):
    """Filtro por rol (Tutor/Estudiante)"""
    title = 'Rol'
    parameter_name = 'rol'

    def lookups(self, request, model_admin):
        return (
            ('tutor', 'Tutores'),
            ('estudiante', 'Estudiantes'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'tutor':
            return queryset.filter(es_tutor=True)
        elif self.value() == 'estudiante':
            return queryset.filter(es_tutor=False)


class SedeFilter(admin.SimpleListFilter):
    """Filtro por sede"""
    title = 'Sede'
    parameter_name = 'sede'

    def lookups(self, request, model_admin):
        sedes = Usuario.objects.values_list('sede', 'sede').distinct().exclude(sede='')
        return sedes

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(sede=self.value())


class CarreraFilter(admin.SimpleListFilter):
    """Filtro por carrera"""
    title = 'Carrera'
    parameter_name = 'carrera'

    def lookups(self, request, model_admin):
        carreras = Usuario.objects.values_list('carrera', 'carrera').distinct().exclude(carrera='')
        return carreras

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(carrera=self.value())


class EstadoSesionFilter(admin.SimpleListFilter):
    """Filtro por estado de sesión"""
    title = 'Estado de Sesión'
    parameter_name = 'estado_sesion'

    def lookups(self, request, model_admin):
        return [
            ('Pendiente', 'Pendiente'),
            ('Aceptada', 'Aceptada'),
            ('Denegada', 'Denegada'),
            ('Completada', 'Completada'),
            ('Cancelada', 'Cancelada'),
            ('No_Show', 'No Show'),
        ]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(estado=self.value())


class FechaProximaFilter(admin.SimpleListFilter):
    """Filtro por jerarquía de fechas"""
    title = 'Período de Sesión'
    parameter_name = 'fecha_sesion'

    def lookups(self, request, model_admin):
        from django.utils import timezone
        return (
            ('hoy', 'Hoy'),
            ('proxima_semana', 'Próxima Semana'),
            ('proximo_mes', 'Próximo Mes'),
            ('pasadas', 'Sesiones Pasadas'),
        )

    def queryset(self, request, queryset):
        from django.utils import timezone
        from datetime import timedelta

        ahora = timezone.now()
        
        if self.value() == 'hoy':
            inicio = ahora.replace(hour=0, minute=0, second=0)
            fin = ahora.replace(hour=23, minute=59, second=59)
            return queryset.filter(fecha_programada__range=[inicio, fin])
        
        elif self.value() == 'proxima_semana':
            inicio = ahora + timedelta(days=1)
            fin = ahora + timedelta(days=7)
            return queryset.filter(fecha_programada__range=[inicio, fin])
        
        elif self.value() == 'proximo_mes':
            inicio = ahora + timedelta(days=1)
            fin = ahora + timedelta(days=30)
            return queryset.filter(fecha_programada__range=[inicio, fin])
        
        elif self.value() == 'pasadas':
            return queryset.filter(fecha_programada__lt=ahora)


class CalificacionFilter(admin.SimpleListFilter):
    """Filtro por rango de calificación"""
    title = 'Rango de Calificación'
    parameter_name = 'calificacion_rango'

    def lookups(self, request, model_admin):
        return (
            ('4.5+', '4.5 - 5.0 ⭐⭐⭐⭐⭐'),
            ('4.0', '4.0 - 4.4 ⭐⭐⭐⭐'),
            ('3.5', '3.5 - 3.9 ⭐⭐⭐'),
            ('3.0', '3.0 - 3.4 ⭐⭐'),
            ('-3.0', 'Menor a 3.0 ⭐'),
        )

    def queryset(self, request, queryset):
        if self.value() == '4.5+':
            return queryset.filter(calificacion_promedio__gte=4.5)
        elif self.value() == '4.0':
            return queryset.filter(calificacion_promedio__gte=4.0, calificacion_promedio__lt=4.5)
        elif self.value() == '3.5':
            return queryset.filter(calificacion_promedio__gte=3.5, calificacion_promedio__lt=4.0)
        elif self.value() == '3.0':
            return queryset.filter(calificacion_promedio__gte=3.0, calificacion_promedio__lt=3.5)
        elif self.value() == '-3.0':
            return queryset.filter(calificacion_promedio__lt=3.0)


# ===========================================
# ADMIN USUARIO
# ===========================================
@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = (
        'rut', 'get_full_name', 'email', 'sede', 'carrera', 
        'get_rol_badge', 'estado', 'date_joined'
    )
    list_filter = (
        RolFilter,
        SedeFilter,
        CarreraFilter,
        'estado',
        'date_joined',
        'es_tutor'
    )
    search_fields = ('rut', 'first_name', 'last_name', 'email', 'sede', 'carrera')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Información Personal', {
            'fields': ('first_name', 'last_name', 'email')
        }),
        ('Información INACAP', {
            'fields': (
                'rut', 'telefono', 'genero', 'fecha_nacimiento',
                'sede', 'carrera', 'semestre_actual', 
                'promedio_general', 'beneficio_gratuidad', 
                'es_tutor', 'estado', 'fecha_ingreso'
            ),
        }),
        ('Permisos', {
            'fields': ('is_active', 'is_staff', 'is_superuser'),
        }),
        ('Grupos y Permisos Avanzados', {
            'fields': ('groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        ('Fechas Importantes', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        }),
    )

    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = 'Nombre Completo'

    def get_rol_badge(self, obj):
        """Mostrar rol con color"""
        if obj.es_tutor:
            return format_html(
                '<span style="background-color: #4CAF50; color: white; '
                'padding: 3px 10px; border-radius: 3px;">Tutor</span>'
            )
        else:
            return format_html(
                '<span style="background-color: #2196F3; color: white; '
                'padding: 3px 10px; border-radius: 3px;">Estudiante</span>'
            )
    get_rol_badge.short_description = 'Rol'

    def get_queryset(self, request):
        """Optimizar queryset"""
        qs = super().get_queryset(request)
        return qs.select_related('tutor_profile')

    actions = ['marcar_como_tutor', 'marcar_como_estudiante', 'cambiar_estado_activo']

    def marcar_como_tutor(self, request, queryset):
        updated = queryset.update(es_tutor=True)
        tutores_group = Group.objects.get(name='Tutores')
        for usuario in queryset:
            usuario.groups.add(tutores_group)
        self.message_user(request, f'{updated} usuarios marcados como tutores')
    marcar_como_tutor.short_description = 'Marcar seleccionados como Tutores'

    def marcar_como_estudiante(self, request, queryset):
        updated = queryset.update(es_tutor=False)
        tutores_group = Group.objects.get(name='Tutores')
        for usuario in queryset:
            usuario.groups.remove(tutores_group)
        self.message_user(request, f'{updated} usuarios marcados como estudiantes')
    marcar_como_estudiante.short_description = 'Marcar seleccionados como Estudiantes'

    def cambiar_estado_activo(self, request, queryset):
        updated = queryset.update(estado='Activo')
        self.message_user(request, f'{updated} usuarios marcados como Activos')
    cambiar_estado_activo.short_description = 'Marcar como Activos'


# ===========================================
# ADMIN TUTOR
# ===========================================
@admin.register(Tutor)
class TutorAdmin(admin.ModelAdmin):
    list_display = (
        'get_nombre_completo', 'get_rut', 'nivel', 
        'get_calificacion_badge', 'total_sesiones', 
        'horas_acumuladas', 'activo'
    )
    list_filter = (
        'nivel',
        'modalidad_preferida',
        'activo',
        CalificacionFilter,
    )
    search_fields = (
        'usuario__first_name',
        'usuario__last_name',
        'usuario__rut',
        'especialidades'
    )
    readonly_fields = (
        'calificacion_promedio',
        'total_sesiones',
        'horas_acumuladas',
        'get_sesiones_stats'
    )
    ordering = ('-calificacion_promedio',)

    fieldsets = (
        ('Información del Tutor', {
            'fields': ('usuario', 'fecha_certificacion', 'nivel', 'años_experiencia')
        }),
        ('Especialidades y Modalidad', {
            'fields': ('especialidades', 'modalidad_preferida', 'bio_descripcion')
        }),
        ('Estadísticas', {
            'fields': (
                'calificacion_promedio',
                'total_sesiones',
                'horas_acumuladas',
                'get_sesiones_stats'
            ),
            'classes': ('collapse',)
        }),
        ('Estado', {
            'fields': ('activo',)
        }),
    )

    def get_nombre_completo(self, obj):
        return obj.usuario.get_full_name()
    get_nombre_completo.short_description = 'Nombre'

    def get_rut(self, obj):
        return obj.usuario.rut
    get_rut.short_description = 'RUT'

    def get_calificacion_badge(self, obj):
        """Mostrar calificación con color según puntuación"""
        calificacion = float(obj.calificacion_promedio)
        if calificacion >= 4.5:
            color = '#4CAF50'
        elif calificacion >= 4.0:
            color = '#8BC34A'
        elif calificacion >= 3.5:
            color = '#FFC107'
        else:
            color = '#FF5722'
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-weight: bold;">★ {}</span>',
            color, obj.calificacion_promedio
        )
    get_calificacion_badge.short_description = 'Calificación'

    def get_sesiones_stats(self, obj):
        """Estadísticas de sesiones del tutor"""
        stats = obj.sesiones_como_tutor.aggregate(
            pendientes=Count('id', filter=Q(estado='Pendiente')),
            aceptadas=Count('id', filter=Q(estado='Aceptada')),
            completadas=Count('id', filter=Q(estado='Completada')),
        )
        
        return format_html(
            '<div style="font-family: monospace; line-height: 1.8;">'
            '<span style="color: #ff9800;">⏳ Pendientes: {}</span><br>'
            '<span style="color: #4caf50;">✓ Aceptadas: {}</span><br>'
            '<span style="color: #2196f3;">✔ Completadas: {}</span>'
            '</div>',
            stats['pendientes'],
            stats['aceptadas'],
            stats['completadas']
        )
    get_sesiones_stats.short_description = 'Estadísticas de Sesiones'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('usuario').prefetch_related('sesiones_como_tutor')


# ===========================================
# ADMIN SESIÓN TUTORÍA
# ===========================================
@admin.register(SesionTutoria)
class SesionTutoriaAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'get_tutor_nombre',
        'get_tutorado_nombre',
        'asignatura',
        'modalidad',
        'fecha_programada',
        'get_estado_badge',
        'get_calificaciones'
    )
    list_filter = (
        EstadoSesionFilter,
        FechaProximaFilter,
        'modalidad',
        ('fecha_programada', admin.DateFieldListFilter),
    )
    search_fields = (
        'tutor__usuario__first_name',
        'tutor__usuario__last_name',
        'tutor__usuario__rut',
        'tutorado__first_name',
        'tutorado__last_name',
        'tutorado__rut',
        'asignatura__nombre',
        'tema_solicitud'
    )
    readonly_fields = (
        'fecha_creacion',
        'fecha_inicio',
        'fecha_fin',
        'get_detalles_sesion'
    )
    date_hierarchy = 'fecha_programada'

    fieldsets = (
        ('Participantes', {
            'fields': ('tutor', 'tutorado')
        }),
        ('Información de la Sesión', {
            'fields': (
                'asignatura',
                'modalidad',
                'fecha_programada',
                'duracion_minutos',
                'tema_solicitud'
            )
        }),
        ('Estado y Resultado', {
            'fields': (
                'estado',
                'razon_rechazo',
                'notas_tutor',
                'calificacion_tutor',
                'calificacion_tutorado'
            )
        }),
        ('Fechas', {
            'fields': (
                'fecha_inicio',
                'fecha_fin',
                'fecha_creacion'
            ),
            'classes': ('collapse',)
        }),
        ('Detalles Completos', {
            'fields': ('get_detalles_sesion',),
            'classes': ('collapse',)
        }),
    )

    def get_tutor_nombre(self, obj):
        return obj.tutor.usuario.get_full_name()
    get_tutor_nombre.short_description = 'Tutor'

    def get_tutorado_nombre(self, obj):
        return obj.tutorado.get_full_name()
    get_tutorado_nombre.short_description = 'Tutorado'

    def get_estado_badge(self, obj):
        """Mostrar estado con color"""
        colores = {
            'Pendiente': '#ff9800',
            'Aceptada': '#4caf50',
            'Denegada': '#f44336',
            'Completada': '#2196f3',
            'Cancelada': '#9c27b0',
            'No_Show': '#607d8b',
        }
        color = colores.get(obj.estado, '#999')
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-weight: bold;">{}</span>',
            color, obj.get_estado_display()
        )
    get_estado_badge.short_description = 'Estado'

    def get_calificaciones(self, obj):
        """Mostrar calificaciones de ambas partes"""
        html = ''
        if obj.calificacion_tutor:
            html += f'<span title="Calificación del Tutor">Tutor: ★{obj.calificacion_tutor}</span><br>'
        if obj.calificacion_tutorado:
            html += f'<span title="Calificación del Tutorado">Estudiante: ★{obj.calificacion_tutorado}</span>'
        
        return format_html(html) if html else '—'
    get_calificaciones.short_description = 'Calificaciones'

    def get_detalles_sesion(self, obj):
        """Mostrar detalles completos de la sesión"""
        from django.utils import timezone
        
        hora_inicio = obj.fecha_inicio.strftime('%d/%m/%Y %H:%M') if obj.fecha_inicio else '—'
        hora_fin = obj.fecha_fin.strftime('%d/%m/%Y %H:%M') if obj.fecha_fin else '—'
        
        html = (
            f'<div style="font-family: monospace; line-height: 2;">'
            f'<strong>Tema:</strong> {obj.tema_solicitud}<br>'
            f'<strong>Duración:</strong> {obj.duracion_minutos} minutos<br>'
            f'<strong>Inicio Real:</strong> {hora_inicio}<br>'
            f'<strong>Fin Real:</strong> {hora_fin}<br>'
            f'<strong>Notas del Tutor:</strong> {obj.notas_tutor or "—"}<br>'
            f'<strong>Creada:</strong> {obj.fecha_creacion.strftime("%d/%m/%Y %H:%M") if obj.fecha_creacion else "—"}'
            f'</div>'
        )
        return format_html(html)
    get_detalles_sesion.short_description = 'Detalles de la Sesión'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related(
            'tutor__usuario',
            'tutorado',
            'asignatura'
        )

    actions = ['marcar_como_completada', 'marcar_como_cancelada']

    def marcar_como_completada(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(estado='Completada', fecha_fin=timezone.now())
        self.message_user(request, f'{updated} sesiones marcadas como completadas')
    marcar_como_completada.short_description = 'Marcar como Completadas'

    def marcar_como_cancelada(self, request, queryset):
        updated = queryset.update(estado='Cancelada')
        self.message_user(request, f'{updated} sesiones canceladas')
    marcar_como_cancelada.short_description = 'Marcar como Canceladas'


# ===========================================
# ADMIN NOTIFICACIÓN
# ===========================================
@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = (
        'get_titulo_corto',
        'get_usuario',
        'tipo',
        'get_leida_badge',
        'fecha_envio'
    )
    list_filter = (
        'tipo',
        'leida',
        ('fecha_envio', admin.DateFieldListFilter),
    )
    search_fields = (
        'titulo',
        'mensaje',
        'usuario__first_name',
        'usuario__last_name',
        'usuario__rut'
    )
    readonly_fields = (
        'fecha_envio',
        'get_mensaje_completo'
    )
    
    fieldsets = (
        ('Información', {
            'fields': ('usuario', 'tipo', 'titulo', 'leida', 'fecha_envio')
        }),
        ('Mensaje', {
            'fields': ('get_mensaje_completo',)
        }),
        ('Sesión Relacionada', {
            'fields': ('sesion',),
            'classes': ('collapse',)
        }),
    )

    def get_titulo_corto(self, obj):
        titulo = obj.titulo[:50]
        return titulo + '...' if len(obj.titulo) > 50 else titulo
    get_titulo_corto.short_description = 'Título'

    def get_usuario(self, obj):
        return obj.usuario.get_full_name()
    get_usuario.short_description = 'Usuario'

    def get_leida_badge(self, obj):
        if obj.leida:
            return format_html(
                '<span style="background-color: #4CAF50; color: white; '
                'padding: 3px 8px; border-radius: 3px;">✓ Leída</span>'
            )
        else:
            return format_html(
                '<span style="background-color: #ff9800; color: white; '
                'padding: 3px 8px; border-radius: 3px;">○ No leída</span>'
            )
    get_leida_badge.short_description = 'Estado'

    def get_mensaje_completo(self, obj):
        return format_html('<p>{}</p>', obj.mensaje)
    get_mensaje_completo.short_description = 'Mensaje Completo'


# ===========================================
# ADMIN DISPONIBILIDAD TUTOR
# ===========================================
@admin.register(DisponibilidadTutor)
class DisponibilidadTutorAdmin(admin.ModelAdmin):
    list_display = (
        'get_tutor_nombre',
        'dia',
        'hora_inicio',
        'hora_fin',
        'activo'
    )
    list_filter = (
        'dia',
        'activo',
        'tutor__usuario__es_tutor',
    )
    search_fields = (
        'tutor__usuario__first_name',
        'tutor__usuario__last_name',
        'tutor__usuario__rut'
    )
    
    fieldsets = (
        ('Tutor', {
            'fields': ('tutor',)
        }),
        ('Horario', {
            'fields': ('dia', 'hora_inicio', 'hora_fin')
        }),
        ('Estado', {
            'fields': ('activo',)
        }),
    )

    def get_tutor_nombre(self, obj):
        return obj.tutor.usuario.get_full_name()
    get_tutor_nombre.short_description = 'Tutor'


# ===========================================
# DESREGISTRAR Y REGISTRAR GROUP
# ===========================================
admin.site.unregister(Group)

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_permisos_count')
    
    def get_permisos_count(self, obj):
        count = obj.permissions.count()
        return format_html(
            '<span style="background-color: #2196F3; color: white; '
            'padding: 3px 8px; border-radius: 3px;">{} permisos</span>',
            count
        )
    get_permisos_count.short_description = 'Cantidad de Permisos'


# ===========================================
# REGISTRAR OTROS MODELOS
# ===========================================
admin.site.register(Sede)
admin.site.register(Carrera)
admin.site.register(Asignatura)
admin.site.register(RecursoEducativo)
admin.site.register(Logro)
admin.site.register(Mensaje)