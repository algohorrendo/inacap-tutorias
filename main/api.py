from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .serializers import *
from .models import *

class TutorViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Tutor.objects.all()
    serializer_class = TutorSerializer

    def get_queryset(self):
        queryset = Tutor.objects.all()
        nombre = self.request.query_params.get('nombre', None)
        especialidad = self.request.query_params.get('especialidad', None)
        
        if nombre:
            queryset = queryset.filter(usuario__first_name__icontains=nombre)
        if especialidad:
            queryset = queryset.filter(especialidades__icontains=especialidad)
        
        return queryset
    
class MensajeViewSet(viewsets.ModelViewSet):
    queryset = Mensaje.objects.all()
    serializer_class = MensajeSerializer

class RecursoEducativoViewSet(viewsets.ModelViewSet):
    queryset = RecursoEducativo.objects.all()
    serializer_class = RecursoEducativoSerializer

class SesionTutoriaViewSet(viewsets.ModelViewSet):
    queryset = SesionTutoria.objects.all()
    serializer_class = SesionTutoriaSerializer

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer