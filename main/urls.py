from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import *
from . import views

router = DefaultRouter()
router.register(r'mensajes', MensajeViewSet)
router.register(r'recursos', RecursoEducativoViewSet)
router.register(r'sesiones', SesionTutoriaViewSet)
router.register(r'usuarios', UsuarioViewSet)
router.register(r'tutores', TutorViewSet)

urlpatterns = [
    # Rutas originales
    path('', views.index, name='index'),  
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('buscar-tutor/', views.buscar_tutor, name='buscar_tutor'),
    path('perfil-tutor/<int:tutor_id>/', views.perfil_tutor, name='perfil_tutor'),
    path('mis-sesiones/', views.mis_sesiones, name='mis_sesiones'),
    path('agendar/<int:tutor_id>/', views.agendar_sesion, name='agendar_sesion'),
    path('recursos/', views.lista_recursos, name='lista_recursos'),
    path('recursos/crear/', views.crear_recurso, name='crear_recurso'),
    path('notificaciones/', views.notificaciones, name='notificaciones'),
    path('perfil/', views.perfil_usuario, name='perfil_usuario'),
    path('registro/', views.registro_view, name='registro'),
    path('mi-disponibilidad/', views.mi_disponibilidad, name='mi_disponibilidad'),
    path('chat/<int:sesion_id>/', views.chat, name='chat'),
    path('chat/<int:sesion_id>/enviar/', views.enviar_mensaje, name='enviar_mensaje'),
    path('sesion/<int:sesion_id>/aceptar/', views.aceptar_sesion, name='aceptar_sesion'),
    path('sesion/<int:sesion_id>/denegar/', views.denegar_sesion, name='denegar_sesion'),
    path('sesion/<int:sesion_id>/finalizar/', views.finalizar_sesion, name='finalizar_sesion'),
    path('calificar_notificacion/<int:sesion_id>/', views.calificar_desde_notificacion, name='calificar_desde_notificacion'),
    path('api/', include(router.urls)),
    path('api-client/', views.api_client, name='api_client'),
    
    # Proxy para APIs externas (evitar CORS)
    path('api/proxy/universidades/', views.proxy_universidades, name='proxy_universidades'),
    path('api/proxy/jsonplaceholder/<str:endpoint>/', views.proxy_jsonplaceholder, name='proxy_jsonplaceholder'),
    
    # Nuevas rutas admin
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-usuarios/', views.admin_usuarios, name='admin_usuarios'),
    path('admin-usuario/<int:usuario_id>/editar/', views.admin_editar_usuario, name='admin_editar_usuario'),
    path('admin-sesiones/', views.admin_sesiones, name='admin_sesiones'),
    path('admin-tutores/', views.admin_tutores, name='admin_tutores'),
    path('admin-grupos-permisos/', views.admin_grupos_permisos, name='admin_grupos_permisos'),
]
