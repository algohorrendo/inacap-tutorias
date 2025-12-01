from rest_framework import serializers
from .models import *

class MensajeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mensaje
        fields = '__all__'

class RecursoEducativoSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecursoEducativo
        fields = '__all__'

class SesionTutoriaSerializer(serializers.ModelSerializer):
    mensajes = MensajeSerializer(many=True, read_only=True)
    class Meta:
        model = SesionTutoria
        fields = '__all__'

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = '__all__'

class TutorSerializer(serializers.ModelSerializer):
    usuario = UsuarioSerializer(read_only=True)
    sesiones = SesionTutoriaSerializer(many=True, read_only=True)
    class Meta:
        model = Tutor
        fields = '__all__'