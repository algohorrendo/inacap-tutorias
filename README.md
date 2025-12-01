# 🎓 INACAP Tutorías

Sistema de gestión de tutorías académicas desarrollado con Django REST Framework.

![Django](https://img.shields.io/badge/Django-4.2.7-green)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![MySQL](https://img.shields.io/badge/MySQL-8.0-orange)
![REST API](https://img.shields.io/badge/API-REST-red)

## 📋 Descripción

Plataforma web completa para la gestión de tutorías académicas en INACAP. Permite a estudiantes buscar tutores, agendar sesiones de tutoría, y a tutores gestionar su disponibilidad y recursos educativos.

## ✨ Características Principales

### 👥 Control de Usuarios
- Registro y autenticación de usuarios con RUT
- Roles diferenciados: Estudiante, Tutor, Administrador
- Perfil personalizado con información académica
- Sistema de sesión única por usuario
- Timeout de sesión por inactividad

### 📚 CRUD Completo
- **Usuarios**: Crear, leer, actualizar, eliminar usuarios
- **Tutores**: Gestión completa de perfiles de tutor
- **Sesiones**: Agendar, aceptar, rechazar, completar tutorías
- **Recursos**: Subir y gestionar material educativo
- **Notificaciones**: Sistema de alertas para usuarios
- **Disponibilidad**: Gestión de horarios de tutores

### 🔌 API REST
- API REST completa con Django REST Framework
- Endpoints para todos los modelos principales
- Autenticación por sesión
- Paginación automática
- Filtros y búsquedas

### 🌐 Conexión API Externa
- Cliente de API integrado
- Conexión a JSONPlaceholder (API de pruebas)
- Conexión a API de Universidades
- Visualización de respuestas JSON

### 🎨 Panel de Administración
- Dashboard con estadísticas
- Gestión de usuarios con filtros avanzados
- Gestión de sesiones de tutoría
- Gestión de tutores y calificaciones
- Control de grupos y permisos

## 🛠️ Tecnologías Utilizadas

- **Backend**: Django 4.2.7, Django REST Framework
- **Base de Datos**: MySQL (desarrollo), PostgreSQL (producción)
- **Frontend**: HTML5, CSS3, JavaScript, Font Awesome
- **Servidor**: Gunicorn, WhiteNoise
- **Despliegue**: Render, Railway compatible

## 📦 Instalación Local

### Prerrequisitos
- Python 3.11+
- MySQL 8.0+
- pip

### Pasos

1. **Clonar el repositorio**
```bash
git clone https://github.com/tu-usuario/inacap-tutorias.git
cd inacap-tutorias
```

2. **Crear entorno virtual**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**
```bash
# Copiar el archivo de ejemplo
copy env.example .env  # Windows
cp env.example .env    # Linux/Mac

# Editar .env con tus configuraciones
```

5. **Crear base de datos MySQL**
```sql
CREATE DATABASE inacap_tutorias CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

6. **Ejecutar migraciones**
```bash
python manage.py migrate
```

7. **Crear superusuario**
```bash
python manage.py createsuperuser
```

8. **Ejecutar servidor de desarrollo**
```bash
python manage.py runserver
```

9. **Acceder a la aplicación**
- Sitio web: http://localhost:8000
- Admin Django: http://localhost:8000/admin
- API REST: http://localhost:8000/api/

## 🌍 Despliegue en Producción (Render)

1. **Crear cuenta en Render.com**

2. **Crear nuevo Web Service**
   - Conectar repositorio de GitHub
   - Build Command: `./build.sh`
   - Start Command: `gunicorn inacap_tutorias.wsgi:application`

3. **Configurar variables de entorno en Render**
```
SECRET_KEY=tu-clave-secreta-muy-larga
DEBUG=False
DATABASE_URL=postgres://... (proporcionado por Render)
PRODUCTION_URL=https://tu-app.onrender.com
```

4. **Crear base de datos PostgreSQL en Render**

## 📡 Endpoints de la API

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/tutores/` | Listar tutores |
| POST | `/api/tutores/` | Crear tutor |
| GET | `/api/tutores/{id}/` | Detalle tutor |
| PUT | `/api/tutores/{id}/` | Actualizar tutor |
| DELETE | `/api/tutores/{id}/` | Eliminar tutor |
| GET | `/api/sesiones/` | Listar sesiones |
| POST | `/api/sesiones/` | Crear sesión |
| GET | `/api/usuarios/` | Listar usuarios |
| GET | `/api/recursos/` | Listar recursos |
| GET | `/api/mensajes/` | Listar mensajes |

### Filtros disponibles
```
/api/tutores/?nombre=Juan
/api/tutores/?especialidad=Matemáticas
```

## 📁 Estructura del Proyecto

```
inacap_tutorias/
├── inacap_tutorias/          # Configuración del proyecto
│   ├── settings.py           # Configuración Django
│   ├── urls.py               # URLs principales
│   └── wsgi.py               # WSGI para producción
├── main/                     # Aplicación principal
│   ├── models.py             # Modelos de datos
│   ├── views.py              # Vistas
│   ├── api.py                # ViewSets de la API
│   ├── serializers.py        # Serializadores REST
│   ├── forms.py              # Formularios
│   ├── admin.py              # Configuración del admin
│   ├── middleware.py         # Middleware personalizado
│   ├── urls.py               # URLs de la app
│   ├── templates/            # Templates HTML
│   └── static/               # Archivos estáticos
├── media/                    # Archivos subidos
├── logs/                     # Logs de la aplicación
├── requirements.txt          # Dependencias Python
├── Procfile                  # Configuración Render
├── build.sh                  # Script de build
└── README.md                 # Este archivo
```

## 🔐 Seguridad

- Protección CSRF activa
- Cookies seguras en producción
- HSTS habilitado en producción
- Validación de contraseñas
- Sesión única por usuario
- Timeout de inactividad

## 👨‍💻 Autores

- **Bastián Arredondo** - Desarrollador principal

## 📄 Licencia

Este proyecto es de uso educativo para INACAP.

## 🤝 Contribuir

1. Fork el proyecto
2. Crear rama de feature (`git checkout -b feature/NuevaCaracteristica`)
3. Commit cambios (`git commit -m 'Agregar nueva característica'`)
4. Push a la rama (`git push origin feature/NuevaCaracteristica`)
5. Crear Pull Request

---

⭐ **INACAP Tutorías** - Sistema de gestión de tutorías académicas

