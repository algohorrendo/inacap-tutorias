#!/usr/bin/env bash
# Script de build para Render

set -o errexit

# Instalar dependencias
pip install -r requirements.txt

# Recolectar archivos estáticos
python manage.py collectstatic --no-input

# Ejecutar migraciones
python manage.py migrate

# Crear superusuario admin si no existe
python manage.py shell << EOF
from main.models import Usuario
if not Usuario.objects.filter(rut='22072118-3').exists():
    admin = Usuario.objects.create_superuser(
        rut='22072118-3',
        username='22072118-3',
        email='basti@inacap.cl',
        password='gato1234',
        first_name='admin',
        last_name='sistema'
    )
    admin.is_staff = True
    admin.is_superuser = True
    admin.save()
    print('✅ Superusuario admin creado exitosamente')
else:
    print('ℹ️ Superusuario admin ya existe')
EOF

