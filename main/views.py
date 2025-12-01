from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.conf import settings
from django.views.decorators.http import require_http_methods
from .models import (Usuario, Tutor, SesionTutoria, RecursoEducativo, 
                     Notificacion, DisponibilidadTutor, Mensaje, Asignatura,
                     Logro, UsuarioLogro)
from .forms import (RegistroForm, LoginForm, AgendarForm, MensajeForm, 
                    RecursoEducativoForm)
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from datetime import datetime, timedelta
import json
import requests
from django.db.models import Q, Count

# Verificar si es administrador
def is_admin(user):
    return user.is_staff or user.is_superuser

def index(request):
    """Vista principal para visitantes"""
    tutores = Tutor.objects.filter(activo=True).order_by('-calificacion_promedio')[:6]
    return render(request, 'main/index.html', {
        'tutores': tutores,
        'total_tutores': Tutor.objects.filter(activo=True).count(),
        'total_sesiones': SesionTutoria.objects.filter(estado='Completada').count()
    })

@login_required
@user_passes_test(is_admin)
def api_client(request):
    """Vista del cliente API - Solo para administradores"""
    return render(request, 'main/api_client.html')


# ============================================
# PROXY PARA APIs EXTERNAS (evitar CORS)
# ============================================
@login_required
@user_passes_test(is_admin)
def proxy_countries(request):
    """Proxy para API de países de Sudamérica"""
    try:
        response = requests.get(
            'https://restcountries.com/v3.1/region/south%20america',
            timeout=10
        )
        return JsonResponse(response.json(), safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@user_passes_test(is_admin)
def proxy_jsonplaceholder(request, endpoint):
    """Proxy para JSONPlaceholder API"""
    allowed_endpoints = ['posts', 'users', 'comments', 'todos']
    if endpoint not in allowed_endpoints:
        return JsonResponse({'error': 'Endpoint no permitido'}, status=400)
    
    try:
        response = requests.get(
            f'https://jsonplaceholder.typicode.com/{endpoint}?_limit=10',
            timeout=10
        )
        return JsonResponse(response.json(), safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def registro_view(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            usuario = form.save(commit=False)
            usuario.es_tutor = form.cleaned_data.get('es_tutor', False)
            usuario.save()

            if usuario.es_tutor:
                Tutor.objects.update_or_create(
                    usuario=usuario,
                    defaults={
                        'fecha_certificacion': timezone.now().date(),
                        'especialidades': form.cleaned_data.get('especialidades', ''),
                        'años_experiencia': form.cleaned_data.get('años_experiencia', 0),
                        'activo': True,
                        'nivel': 'Novato'
                    }
                )

            login(request, usuario)
            return redirect('dashboard')
    else:
        form = RegistroForm()

    return render(request, 'main/registro.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = LoginForm(request.POST or None)
    error = None
    if request.method == 'POST' and form.is_valid():
        rut = form.cleaned_data['rut']
        password = form.cleaned_data['password']
        user = authenticate(request, username=rut, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            error = 'Credenciales inválidas'
    return render(request, 'main/login.html', {'form': form, 'error': error})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    user = request.user
    ahora = timezone.now()

    sesiones_terminadas_count = SesionTutoria.objects.filter(
        tutor=user.tutor_profile,
        estado='Completada',
        fecha_programada__lt=ahora
    ).count() if hasattr(user, 'tutor_profile') else 0

    # Rango basado en sesiones terminadas (orden correcto de mayor a menor)
    rango = 'Novato'
    if sesiones_terminadas_count >= 200:
        rango = 'Iluminado'
    elif sesiones_terminadas_count >= 100:
        rango = 'Erudito'
    elif sesiones_terminadas_count >= 50:
        rango = 'Avanzado'
    elif sesiones_terminadas_count >= 25:
        rango = 'Intermedio'
    elif sesiones_terminadas_count >= 10:
        rango = 'Principiante'

    sesiones_tutor = SesionTutoria.objects.filter(
        tutor=user.tutor_profile,
        estado='Aceptada',
        fecha_programada__gte=ahora
    ).order_by('fecha_programada')[:5] if hasattr(user, 'tutor_profile') else []

    tutores = Tutor.objects.filter(activo=True).order_by('-calificacion_promedio')[:5]


    sesiones_pendientes = SesionTutoria.objects.filter(
        tutor=user.tutor_profile,
        estado='Pendiente'
    ).count() if hasattr(user, 'tutor_profile') else 0


    sesiones_terminadas = SesionTutoria.objects.filter(
        tutor=user.tutor_profile,
        estado='Completada'
    ).count() if hasattr(user, 'tutor_profile') else 0



    sesiones_proximas_tutorado = SesionTutoria.objects.filter(
        tutorado=user,
        estado__in=['Pendiente', 'Aceptada'],
        fecha_programada__gte=ahora
    ).order_by('fecha_programada')[:5]


    # Enviar contexto
    return render(request, 'main/dashboard.html', {
        'sesiones_pendientes': sesiones_pendientes,
        'sesiones_terminadas': sesiones_terminadas,
        'sesiones_terminadas_count': sesiones_terminadas_count,
        'rango': rango,
        'sesiones_tutor': sesiones_tutor,
        'tutores': tutores,
        'sesiones_proximas_tutorado': sesiones_proximas_tutorado,
    })


def buscar_tutor(request):
    tutores = Tutor.objects.filter(activo=True).order_by('-calificacion_promedio')
    
    nombre = request.GET.get('nombre', '')
    especialidad = request.GET.get('especialidad', '')

    if nombre:
        tutores = tutores.filter(Q(usuario__first_name__icontains=nombre) | 
                                Q(usuario__last_name__icontains=nombre))
    if especialidad:
        tutores = tutores.filter(especialidades__icontains=especialidad)

    return render(request, 'main/buscar_tutor.html', {
        'tutores': tutores,
        'user_authenticated': request.user.is_authenticated
    })


def perfil_tutor(request, tutor_id):
    tutor = get_object_or_404(Tutor, pk=tutor_id)
    sesiones_completadas = tutor.sesiones_como_tutor.filter(estado='Completada').count()
    return render(request, 'main/perfil_tutor.html', {
        'tutor': tutor,
        'sesiones_completadas': sesiones_completadas,
        'user_authenticated': request.user.is_authenticated
    })

@login_required
def mis_sesiones(request):
    user = request.user
    ahora = timezone.now()
    
    # Distinguir entre tutor y tutorado
    if hasattr(user, 'tutor_profile'):
        # Es tutor: ver sesiones donde es tutor
        sesiones_pendientes = SesionTutoria.objects.filter(
            tutor=user.tutor_profile,
            estado='Pendiente'
        ).order_by('fecha_programada')
        
        sesiones_futuras = SesionTutoria.objects.filter(
            tutor=user.tutor_profile,
            estado__in=['Aceptada'],
            fecha_programada__gte=ahora
        ).order_by('fecha_programada')
        
        sesiones_pasadas = SesionTutoria.objects.filter(
        tutorado=user,
        estado='Completada',
        calificacion_tutorado__isnull=True
        ).order_by('-fecha_programada')

        
        return render(request, 'main/mis_sesiones_tutor.html', {
            'sesiones_pendientes': sesiones_pendientes,
            'sesiones_futuras': sesiones_futuras,
            'sesiones_pasadas': sesiones_pasadas,
            'es_tutor': True,
        })
    else:
        # Es tutorado: ver sesiones donde es tutorado
        sesiones_futuras = SesionTutoria.objects.filter(
            tutorado=user,
            estado='Aceptada',
            fecha_programada__gte=ahora
        ).order_by('fecha_programada')
        
        sesiones_pendientes = SesionTutoria.objects.filter(
            tutorado=user,
            estado='Pendiente'
        ).order_by('fecha_programada')
        
        sesiones_pasadas = SesionTutoria.objects.filter(
            tutorado=user,
            estado__in=['Completada', 'No_Show'],
            fecha_programada__lt=ahora
        ).order_by('-fecha_programada')
        
        return render(request, 'main/mis_sesiones_tutorado.html', {
            'sesiones_futuras': sesiones_futuras,
            'sesiones_pendientes': sesiones_pendientes,
            'sesiones_pasadas': sesiones_pasadas,
            'es_tutor': False,
        })

@login_required
@require_http_methods(["POST"])
def aceptar_sesion(request, sesion_id):
    sesion = get_object_or_404(SesionTutoria, id=sesion_id)

    # Cambiado user a usuario para coincidir con modelo Tutor
    if sesion.tutor.usuario != request.user:
        return HttpResponseForbidden("No tienes permiso para aceptar esta sesión.")

    sesion.estado = 'Aceptada'
    sesion.save()



    Notificacion.objects.create(
        usuario=sesion.tutorado,
        tipo='Sesion_Aceptada',
        titulo='Sesión aceptada',
        mensaje=f'Tu tutor {sesion.tutor.usuario.first_name} ha aceptado tu solicitud para el {sesion.fecha_programada.strftime("%d-%m-%Y %H:%M")}.'
    )

    return JsonResponse({'mensaje': 'Sesión aceptada correctamente'})



@login_required
@require_http_methods(["POST"])
def denegar_sesion(request, sesion_id):
    sesion = get_object_or_404(SesionTutoria, pk=sesion_id)

    # Verificar que el usuario sea el tutor
    if not hasattr(request.user, 'tutor_profile') or sesion.tutor.usuario != request.user:
        return HttpResponseForbidden()

    if sesion.estado != 'Pendiente':
        return JsonResponse({'error': 'Solo puedes rechazar sesiones pendientes'}, status=400)

    # No intentes cargar JSON si no hay body
    razon = 'Sin especificar'  # default si no envían

    if request.body:
        import json
        data = json.loads(request.body)
        razon = data.get('razon', razon)

    sesion.estado = 'Denegada'
    sesion.razon_rechazo = razon
    sesion.save()

    # Notificar al tutorado
    Notificacion.objects.create(
        usuario=sesion.tutorado,
        tipo='Sesion_Rechazada',
        titulo='Sesión rechazada',
        mensaje=f'Lamentablemente, tu tutor ha rechazado tu solicitud de tutoría. Motivo: {razon}'
    )

    return JsonResponse({'success': True, 'mensaje': 'Sesión rechazada correctamente'})


@login_required
def agendar_sesion(request, tutor_id):
    tutor = get_object_or_404(Tutor, pk=tutor_id)
    
    if request.method == 'POST':
        form = AgendarForm(request.POST, tutor=tutor)
        if form.is_valid():
            hora_disp = form.cleaned_data['hora_disponible']
            asignatura_obj = form.cleaned_data['asignatura']
            modalidad = form.cleaned_data['modalidad']
            tema_solicitud = form.cleaned_data['tema_solicitud']

            dia, hora = hora_disp.split(" ", 1)
            hora_dt = datetime.strptime(hora, "%H:%M")
            
            fecha_base = timezone.now().date()
            dias_mapa = {
                'Lunes': 0, 'Martes': 1, 'Miércoles': 2, 'Jueves': 3,
                'Viernes': 4, 'Sábado': 5, 'Domingo': 6
            }
            dia_num = dias_mapa.get(dia, 0)
            dias_adelante = (dia_num - fecha_base.weekday()) % 7
            if dias_adelante == 0:
                dias_adelante = 7
            fecha_programada = datetime.combine(
                fecha_base + timedelta(days=dias_adelante),
                hora_dt.time()
            )
            fecha_programada = timezone.make_aware(fecha_programada)

            sesion = SesionTutoria.objects.create(
                tutorado=request.user,
                tutor=tutor,
                asignatura=asignatura_obj,
                modalidad=modalidad,
                fecha_programada=fecha_programada,
                duracion_minutos=60,
                estado='Pendiente',
                tema_solicitud=tema_solicitud,
            )

            # Otorgar logro si es Nostradamus
            if tutor.usuario.first_name == "Como un Gran Pensador" and tutor.usuario.last_name == "Nostradamus":
                logro, created = Logro.objects.get_or_create(
                    nombre='En busca de habilidades proféticas',
                    defaults={
                        'descripcion': 'Has iniciado una sesión con el tutor Nostradamus, ¡comienza tu viaje hacia la iluminación!',
                        'categoria': 'Especialidad',
                        'puntos': 20,
                        'icono': '🔮',
                        'activo': True,
                    }
                )
                UsuarioLogro.objects.get_or_create(usuario=request.user, logro=logro)

            Notificacion.objects.create(
                usuario=tutor.usuario,
                tipo='Sesion_Agendada',
                titulo='Nueva solicitud de tutoría',
                mensaje=f'{request.user.first_name} ha solicitado una sesión de tutoría para {fecha_programada.strftime("%d-%m-%Y %H:%M")}.'
            )
            Notificacion.objects.create(
                usuario=request.user,
                tipo='Sesion_Agendada',
                titulo='Solicitud enviada',
                mensaje=f'Tu solicitud de tutoría con {tutor.usuario.first_name} ha sido enviada. En breve te notificaremos si es aceptada.'
            )

            return redirect('mis_sesiones')
    else:
        form = AgendarForm(tutor=tutor)
    
    return render(request, 'main/agendar_sesion.html', {'form': form, 'tutor': tutor})
    
@login_required
def detalle_sesion(request, sesion_id):
    sesion = get_object_or_404(SesionTutoria, pk=sesion_id)
    
    # Verificar permisos
    if sesion.tutorado != request.user and sesion.tutor.usuario != request.user:
        return HttpResponseForbidden()
    
    mensajes = sesion.mensajes.all()
    puede_calificar_tutor = (sesion.tutorado == request.user and 
                             sesion.estado == 'Completada' and 
                             sesion.calificacion_tutorado is None)
    puede_calificar_tutor_al = (sesion.tutor.usuario == request.user and 
                                sesion.estado == 'Completada' and 
                                sesion.calificacion_tutor is None)
    
    if request.method == 'POST':
        if 'calificacion' in request.POST:
            calificacion = int(request.POST.get('calificacion'))
            if sesion.tutorado == request.user:
                sesion.calificacion_tutorado = calificacion
            else:
                sesion.calificacion_tutor = calificacion
                sesion.tutor.actualizar_calificacion_promedio()
            sesion.save()
            return redirect('detalle_sesion', sesion_id=sesion_id)
    
    return render(request, 'main/detalle_sesion.html', {
        'sesion': sesion,
        'mensajes': mensajes,
        'puede_calificar_tutor': puede_calificar_tutor,
        'puede_calificar_tutor_al': puede_calificar_tutor_al,
        'es_tutor': sesion.tutor.usuario == request.user,
    })

@login_required
def chat(request, sesion_id):
    sesion = get_object_or_404(SesionTutoria, id=sesion_id)
    # Verificar que el usuario sea tutor o tutorado de la sesión
    if request.user != sesion.tutorado and (not hasattr(request.user, 'tutor_profile') or request.user.tutor_profile != sesion.tutor):
        return redirect('dashboard')

    mensajes = sesion.mensajes.order_by('fecha_envio')

    if request.method == 'POST':
        form = MensajeForm(request.POST)
        if form.is_valid():
            mensaje = form.save(commit=False)
            mensaje.sesion = sesion
            mensaje.remitente = request.user
            mensaje.save()
            return redirect('chat', sesion_id=sesion.id)
    else:
        form = MensajeForm()

    return render(request, 'main/chat.html', {
        'sesion': sesion,
        'mensajes': mensajes,
        'form': form,
    })

@login_required
@require_http_methods(["POST"])
def enviar_mensaje(request, sesion_id):
    sesion = get_object_or_404(SesionTutoria, pk=sesion_id)
    
    # Verificar permisos
    if sesion.tutorado != request.user and sesion.tutor.usuario != request.user:
        return HttpResponseForbidden()
    
    contenido = request.POST.get('contenido', '').strip()
    if not contenido:
        return JsonResponse({'error': 'El mensaje no puede estar vacío'}, status=400)
    
    mensaje = Mensaje.objects.create(
        sesion=sesion,
        remitente=request.user,
        mensaje=contenido
    )
    
    return JsonResponse({
        'success': True,
        'mensaje': {
            'id': mensaje.id,
            'remitente': mensaje.remitente.get_full_name(),
            'contenido': mensaje.mensaje,
            'fecha': mensaje.fecha_envio.strftime('%H:%M'),
        }
    })

@login_required
def lista_recursos(request):
    recursos = RecursoEducativo.objects.filter(activo=True).order_by('-fecha_creacion')
    return render(request, 'main/lista_recursos.html', {'recursos': recursos})

@login_required
def crear_recurso(request):
    # Solo tutores pueden crear recursos
    if not hasattr(request.user, 'tutor_profile'):
        return redirect('dashboard')
    
    tutor = request.user.tutor_profile
    
    if request.method == 'POST':
        form = RecursoEducativoForm(request.POST, request.FILES)
        if form.is_valid():
            recurso = form.save(commit=False)
            recurso.tutor = tutor
            recurso.save()
            return redirect('lista_recursos')
    else:
        form = RecursoEducativoForm()
    
    return render(request, 'main/crear_recurso.html', {'form': form})

@login_required
def notificaciones(request):
    notis = Notificacion.objects.filter(usuario=request.user).order_by('-fecha_envio')
    
    if request.method == 'POST':
        # Marcar como leída
        noti_id = request.POST.get('noti_id')
        noti = get_object_or_404(Notificacion, pk=noti_id, usuario=request.user)
        noti.leida = True
        noti.save()
        return redirect('notificaciones')
    
    return render(request, 'main/notificaciones.html', {'notificaciones': notis})

@login_required
def perfil_usuario(request):
    return render(request, 'main/perfil_usuario.html', {'usuario': request.user})

@login_required
def mi_disponibilidad(request):
    if not hasattr(request.user, 'tutor_profile'):
        return redirect('dashboard')
    
    tutor = request.user.tutor_profile
    
    if request.method == 'GET':
        horas = [f"{h:02d}:00" for h in range(8, 21)]
        dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

        # Obtener disponibilidades guardadas
        disponibilidades = tutor.disponibilidadtutor_set.filter(activo=True)
        horarios_guardados = [
            {'dia': disp.dia, 'hora': disp.hora_inicio.strftime("%H:%M")}
            for disp in disponibilidades
        ]

        return render(request, 'main/mi_disponibilidad.html', {
            'horas': horas,
            'dias': dias,
            'horarios_guardados': horarios_guardados,
        })

    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Eliminar disponibilidades anteriores
            tutor.disponibilidadtutor_set.all().delete()
            
            # Crear nuevas disponibilidades
            for item in data:
                dia = item.get('dia')
                hora = item.get('hora')
                
                if not dia or not hora:
                    continue
                
                try:
                    hora_dt = datetime.strptime(hora, "%H:%M")
                    hora_inicio = hora_dt.time()
                    hora_fin = (hora_dt + timedelta(hours=1)).time()
                    
                    DisponibilidadTutor.objects.create(
                        tutor=tutor,
                        dia=dia,
                        hora_inicio=hora_inicio,
                        hora_fin=hora_fin,
                        activo=True
                    )
                except ValueError:
                    continue
            
            return JsonResponse({"status": "ok", "message": "Disponibilidad actualizada con éxito"})
        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Datos inválidos"}, status=400)
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
        
def generar_estrellas(calificacion, max_estrellas=5):
    estrellas_html = ''
    for i in range(max_estrellas):
        if i < calificacion:
            estrellas_html += '⭐'
        else:
            estrellas_html += '☆'
    return estrellas_html

@login_required
def finalizar_sesion(request, sesion_id):
    if request.method == "POST":
        sesion = get_object_or_404(SesionTutoria, pk=sesion_id, tutor__usuario=request.user)
        sesion.estado = "Completada"
        sesion.fecha_fin = timezone.now()
        sesion.save()

        Notificacion.objects.create(
            usuario=sesion.tutorado,
            tipo='Sesion_Completada',
            titulo='Sesión finalizada',
            sesion=sesion,
            mensaje=f"Tu tutor {sesion.tutor.usuario.first_name} ha finalizado la sesión del {sesion.fecha_programada.strftime('%d-%m-%Y %H:%M')}."
        )

        return redirect('mis_sesiones')

@login_required
@require_http_methods(["POST"])
def calificar_desde_notificacion(request, sesion_id):
    sesion = get_object_or_404(SesionTutoria, pk=sesion_id, tutorado=request.user)

    if sesion.estado != 'Completada':
        return JsonResponse({'error': 'La sesión no está finalizada'}, status=400)

    try:
        calificacion = int(request.POST.get('calificacion'))
        if calificacion < 1 or calificacion > 5:
            raise ValueError
    except Exception:
        return JsonResponse({'error': 'Calificación inválida'}, status=400)

    sesion.calificacion_tutorado = calificacion
    sesion.save()

    return JsonResponse({'mensaje': 'Calificación registrada correctamente'})

# ===========================================
# PANEL DE ADMINISTRACIÓN PERSONALIZADO
# ===========================================
@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    """Dashboard principal del admin"""
    context = {
        'total_usuarios': Usuario.objects.count(),
        'total_tutores': Usuario.objects.filter(es_tutor=True).count(),
        'total_estudiantes': Usuario.objects.filter(es_tutor=False).count(),
        'total_sesiones': SesionTutoria.objects.count(),
        'sesiones_pendientes': SesionTutoria.objects.filter(estado='Pendiente').count(),
        'sesiones_completadas': SesionTutoria.objects.filter(estado='Completada').count(),
        'notificaciones_no_leidas': Notificacion.objects.filter(leida=False).count(),
    }
    return render(request, 'admin/dashboard.html', context)


@login_required
@user_passes_test(is_admin)
def admin_usuarios(request):
    """Gestión de usuarios con filtros avanzados"""
    usuarios = Usuario.objects.all()
    
    # Filtro por rol
    rol = request.GET.get('rol')
    if rol == 'tutor':
        usuarios = usuarios.filter(es_tutor=True)
    elif rol == 'estudiante':
        usuarios = usuarios.filter(es_tutor=False)
    
    # Filtro por sede
    sede = request.GET.get('sede')
    if sede:
        usuarios = usuarios.filter(sede=sede)
    
    # Filtro por carrera
    carrera = request.GET.get('carrera')
    if carrera:
        usuarios = usuarios.filter(carrera=carrera)
    
    # Búsqueda por RUT o nombre
    buscar = request.GET.get('buscar')
    if buscar:
        usuarios = usuarios.filter(
            Q(rut__icontains=buscar) |
            Q(first_name__icontains=buscar) |
            Q(last_name__icontains=buscar) |
            Q(email__icontains=buscar)
        )
    
    # Filtro por estado
    estado = request.GET.get('estado')
    if estado:
        usuarios = usuarios.filter(estado=estado)
    
    # Obtener opciones para los filtros
    sedes = Usuario.objects.values_list('sede', flat=True).distinct().exclude(sede='')
    carreras = Usuario.objects.values_list('carrera', flat=True).distinct().exclude(carrera='')
    
    context = {
        'usuarios': usuarios.order_by('-date_joined'),
        'sedes': sedes,
        'carreras': carreras,
        'rol_filtro': rol,
        'sede_filtro': sede,
        'carrera_filtro': carrera,
        'estado_filtro': estado,
        'buscar': buscar,
    }
    return render(request, 'admin/usuarios.html', context)


@login_required
@user_passes_test(is_admin)
def admin_editar_usuario(request, usuario_id):
    """Editar perfil de usuario"""
    usuario = get_object_or_404(Usuario, id=usuario_id)
    
    if request.method == 'POST':
        usuario.first_name = request.POST.get('first_name')
        usuario.last_name = request.POST.get('last_name')
        usuario.email = request.POST.get('email')
        usuario.rut = request.POST.get('rut')
        usuario.telefono = request.POST.get('telefono')
        usuario.sede = request.POST.get('sede')
        usuario.carrera = request.POST.get('carrera')
        usuario.es_tutor = request.POST.get('es_tutor') == 'on'
        usuario.estado = request.POST.get('estado')
        usuario.save()
        messages.success(request, 'Usuario actualizado correctamente')
        return redirect('admin_usuarios')
    
    context = {'usuario': usuario}
    return render(request, 'admin/editar_usuario.html', context)


@login_required
@user_passes_test(is_admin)
def admin_sesiones(request):
    """Gestión de sesiones de tutoría"""
    sesiones = SesionTutoria.objects.all()
    
    # Filtro por estado
    estado = request.GET.get('estado')
    if estado:
        sesiones = sesiones.filter(estado=estado)
    
    # Filtro por período
    periodo = request.GET.get('periodo')
    ahora = timezone.now()
    
    if periodo == 'hoy':
        inicio = ahora.replace(hour=0, minute=0, second=0)
        fin = ahora.replace(hour=23, minute=59, second=59)
        sesiones = sesiones.filter(fecha_programada__range=[inicio, fin])
    elif periodo == 'proxima_semana':
        inicio = ahora + timedelta(days=1)
        fin = ahora + timedelta(days=7)
        sesiones = sesiones.filter(fecha_programada__range=[inicio, fin])
    elif periodo == 'proximo_mes':
        inicio = ahora + timedelta(days=1)
        fin = ahora + timedelta(days=30)
        sesiones = sesiones.filter(fecha_programada__range=[inicio, fin])
    elif periodo == 'pasadas':
        sesiones = sesiones.filter(fecha_programada__lt=ahora)
    
    # Búsqueda
    buscar = request.GET.get('buscar')
    if buscar:
        sesiones = sesiones.filter(
            Q(tutor__usuario__rut__icontains=buscar) |
            Q(tutor__usuario__first_name__icontains=buscar) |
            Q(tutorado__rut__icontains=buscar) |
            Q(tutorado__first_name__icontains=buscar) |
            Q(asignatura__nombre__icontains=buscar)
        )
    
    context = {
        'sesiones': sesiones.select_related('tutor__usuario', 'tutorado').order_by('-fecha_programada'),
        'estado_filtro': estado,
        'periodo_filtro': periodo,
        'buscar': buscar,
        'estados': ['Pendiente', 'Aceptada', 'Denegada', 'Completada', 'Cancelada'],
    }
    return render(request, 'admin/sesiones.html', context)


@login_required
@user_passes_test(is_admin)
def admin_tutores(request):
    """Gestión de tutores"""
    tutores = Tutor.objects.select_related('usuario').all()
    
    # Filtro por nivel
    nivel = request.GET.get('nivel')
    if nivel:
        tutores = tutores.filter(nivel=nivel)
    
    # Filtro por calificación
    calificacion = request.GET.get('calificacion')
    if calificacion == '4.5+':
        tutores = tutores.filter(calificacion_promedio__gte=4.5)
    elif calificacion == '4.0':
        tutores = tutores.filter(calificacion_promedio__gte=4.0, calificacion_promedio__lt=4.5)
    elif calificacion == '3.5':
        tutores = tutores.filter(calificacion_promedio__gte=3.5, calificacion_promedio__lt=4.0)
    
    # Búsqueda
    buscar = request.GET.get('buscar')
    if buscar:
        tutores = tutores.filter(
            Q(usuario__rut__icontains=buscar) |
            Q(usuario__first_name__icontains=buscar) |
            Q(usuario__last_name__icontains=buscar)
        )
    
    context = {
        'tutores': tutores.order_by('-calificacion_promedio'),
        'nivel_filtro': nivel,
        'calificacion_filtro': calificacion,
        'buscar': buscar,
    }
    return render(request, 'admin/tutores.html', context)


@login_required
@user_passes_test(is_admin)
def admin_grupos_permisos(request):
    """Gestión de grupos y permisos"""
    from django.contrib.auth.models import Group
    
    grupos = Group.objects.all()
    
    context = {
        'grupos': grupos,
    }
    return render(request, 'admin/grupos_permisos.html', context)
