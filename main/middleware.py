from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib import messages

class OneSessionPerUserMiddleware:
    """
    Middleware que previene múltiples sesiones simultáneas del mismo usuario.
    Si un usuario inicia sesión en otro dispositivo, cierra la sesión anterior.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Obtener la sesión actual del usuario
            current_session_key = request.session.session_key
            
            # Obtener la última sesión registrada para este usuario
            stored_session_key = request.session.get('user_session_key')
            
            # Si no hay sesión registrada, guardarla
            if not stored_session_key:
                request.session['user_session_key'] = current_session_key
            
            # Si la sesión actual no coincide con la registrada, cerrar sesión
            elif stored_session_key != current_session_key:
                messages.warning(
                    request,
                    'Tu sesión ha sido cerrada porque iniciaste sesión en otro dispositivo.'
                )
                logout(request)
                return redirect('login')

        response = self.get_response(request)
        return response


class SessionTimeoutMiddleware:
    """
    Middleware que cierra automáticamente sesiones inactivas después de cierto tiempo.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            from django.utils import timezone
            import datetime
            
            # Obtener última actividad
            last_activity = request.session.get('last_activity')
            
            if last_activity:
                # Convertir a datetime si es string
                if isinstance(last_activity, str):
                    last_activity = datetime.datetime.fromisoformat(last_activity)
                
                # Calcular tiempo de inactividad (en minutos)
                inactive_time = (timezone.now() - last_activity).total_seconds() / 60
                
                # Si han pasado más de 30 minutos de inactividad, cerrar sesión
                if inactive_time > 30:
                    messages.info(
                        request,
                        'Tu sesión ha expirado por inactividad.'
                    )
                    logout(request)
                    return redirect('login')
            
            # Actualizar última actividad
            request.session['last_activity'] = timezone.now().isoformat()

        response = self.get_response(request)
        return response