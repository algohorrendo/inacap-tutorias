from django import forms
from .models import *
from django.contrib.auth.forms import UserCreationForm

class RegistroForm(UserCreationForm):
    es_tutor = forms.BooleanField(required=False, label="Soy tutor")
    especialidades = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Describe tus especialidades'}),
        label="Especialidades"
    )
    años_experiencia = forms.IntegerField(
        required=False, min_value=0,
        widget=forms.NumberInput(attrs={'placeholder': '0'}),
        label="Años de experiencia"
    )

    class Meta:
        model = Usuario
        fields = [
            "username", "first_name", "last_name", "email", "genero", "rut",
            "sede", "carrera", "semestre_actual", "promedio_general", "es_tutor",
            "especialidades", "años_experiencia", "password1", "password2"
        ]

    def clean(self):
        cleaned_data = super().clean()
        es_tutor = cleaned_data.get("es_tutor")
        especialidades = cleaned_data.get("especialidades")
        años_experiencia = cleaned_data.get("años_experiencia")
        if es_tutor:
            if not especialidades:
                self.add_error('especialidades', "Este campo es obligatorio si eres tutor.")
            if años_experiencia is None:
                self.add_error('años_experiencia', "Este campo es obligatorio si eres tutor.")
        return cleaned_data

class SesionTutoriaForm(forms.ModelForm):
    class Meta:
        model = SesionTutoria
        fields = ['tutorado', 'tutor', 'asignatura', 'modalidad', 'fecha_programada', 'duracion_minutos', 'estado', 'tema_solicitud', 'notas_tutor', 'calificacion_tutor', 'calificacion_tutorado']

class AgendarForm(forms.Form):
    modalidad = forms.ChoiceField(choices=[('Presencial', 'Presencial'), ('Online', 'Online')], required=True)
    tema_solicitud = forms.CharField(widget=forms.Textarea, required=True)
    asignatura = forms.ModelChoiceField(
        queryset=Asignatura.objects.all(),
        label="Asignatura",
        empty_label="Seleccione una asignatura",
        to_field_name="id"
    )

    def __init__(self, *args, **kwargs):
        tutor = kwargs.pop('tutor')
        super().__init__(*args, **kwargs)
        disponibilidades = DisponibilidadTutor.objects.filter(tutor=tutor, activo=True).order_by('dia', 'hora_inicio')
        choices = []
        for disp in disponibilidades:
            label = f"{disp.dia} {disp.hora_inicio.strftime('%H:%M')} a {disp.hora_fin.strftime('%H:%M')}"
            value = f"{disp.dia} {disp.hora_inicio.strftime('%H:%M')}"
            choices.append((value, label))
        self.fields['hora_disponible'] = forms.ChoiceField(choices=choices, label="Seleccione hora disponible")


class LoginForm(forms.Form):
    rut = forms.CharField(max_length=12, widget=forms.TextInput(attrs={'placeholder': '12.345.678-9'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Contraseña'}))

class MensajeForm(forms.ModelForm):
    class Meta:
        model = Mensaje
        fields = ['mensaje']
        widgets = {
            'mensaje': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Escribe un mensaje...'})
        }

class RecursoEducativoForm(forms.ModelForm):
    class Meta:
        model = RecursoEducativo
        fields = ['asignatura', 'titulo', 'descripcion', 'tipo', 'archivo', 'contenido']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
            'contenido': forms.Textarea(attrs={'rows': 5}),
        }


class DisponibilidadForm(forms.ModelForm):
    class Meta:
        model = DisponibilidadTutor
        fields = ['dia', 'hora_inicio', 'hora_fin']


