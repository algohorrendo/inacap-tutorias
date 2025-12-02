import os
from pathlib import Path
from decouple import config, Csv  # Importar python-decouple
import dj_database_url

# Configurar PyMySQL como driver MySQL (compatible con Railway)
try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass

BASE_DIR = Path(__file__).resolve().parent.parent

# ===========================================
# SEGURIDAD - VARIABLES DE ENTORNO
# ===========================================
# Las variables sensibles ahora vienen del archivo .env
SECRET_KEY = config('SECRET_KEY', default='django-insecure-fallback-only-for-development')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '10.58.3.116',
    '.onrender.com',
    '.railway.app',
]

# Agregar host de producción desde variable de entorno
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)


# ===========================================
# APLICACIONES INSTALADAS
# ===========================================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',  # Django REST Framework
    'main',
]

# ===========================================
# MIDDLEWARE
# ===========================================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Para servir archivos estáticos en producción
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',  # Debe estar incluido y en posición correcta.
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'main.middleware.OneSessionPerUserMiddleware',
    'main.middleware.SessionTimeoutMiddleware',
]

ROOT_URLCONF = 'inacap_tutorias.urls'

# ===========================================
# TEMPLATES
# ===========================================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Directorio global de templates
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'inacap_tutorias.wsgi.application'

# ===========================================
# BASE DE DATOS - MySQL CON VARIABLES DE ENTORNO
# ===========================================
# Configuración por defecto para MySQL local
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DB_NAME', default='inacap_tutorias'),
        'USER': config('DB_USER', default='root'),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# Usar DATABASE_URL si está disponible (para Railway/Render con MySQL o PostgreSQL)
DATABASE_URL = config('DATABASE_URL', default=None)
if DATABASE_URL:
    # Si la URL es MySQL, configurar manualmente
    if 'mysql://' in DATABASE_URL or 'mysql2://' in DATABASE_URL:
        from urllib.parse import urlparse
        
        # Parsear la URL MySQL
        # Formato: mysql://user:password@host:port/database
        parsed = urlparse(DATABASE_URL.replace('mysql2://', 'mysql://'))
        
        DATABASES['default'] = {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': parsed.path.lstrip('/'),
            'USER': parsed.username or 'root',
            'PASSWORD': parsed.password or '',
            'HOST': parsed.hostname or 'localhost',
            'PORT': parsed.port or 3306,
            'OPTIONS': {
                'charset': 'utf8mb4',
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            },
        }
    else:
        # Para PostgreSQL u otros
        DATABASES['default'] = dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
        )

# ===========================================
# VALIDACIÓN DE CONTRASEÑAS
# ===========================================
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# ===========================================
# MODELO DE USUARIO PERSONALIZADO
# ===========================================
AUTH_USER_MODEL = 'main.Usuario'

# ===========================================
# CONFIGURACIÓN DE SESIONES
# ===========================================
# Para desarrollo (HTTP sin SSL)
SESSION_COOKIE_SECURE = False  # Cambiar a True en producción con HTTPS
SESSION_COOKIE_HTTPONLY = True  # Cookie no accesible por JavaScript (seguridad XSS)
SESSION_COOKIE_SAMESITE = 'Lax'  # Protección contra CSRF
SESSION_EXPIRE_AT_BROWSER_CLOSE = False  # Sesión persiste al cerrar navegador
SESSION_COOKIE_AGE = config('SESSION_COOKIE_AGE', default=86400, cast=int)  # 24 horas
SESSION_SAVE_EVERY_REQUEST = True  # Actualizar sesión en cada request

# ===========================================
# CONFIGURACIÓN DE LOGIN/LOGOUT
# ===========================================
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'

# ===========================================
# INTERNACIONALIZACIÓN
# ===========================================
LANGUAGE_CODE = 'es-cl'
TIME_ZONE = 'America/Santiago'
USE_I18N = True
USE_TZ = True

# ===========================================
# ARCHIVOS ESTÁTICOS
# ===========================================
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'main' / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Whitenoise para servir archivos estáticos en producción
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ===========================================
# ARCHIVOS MEDIA (uploads)
# ===========================================
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ===========================================
# CAMPO AUTO INCREMENTAL
# ===========================================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ===========================================
# SEGURIDAD - CSRF PROTECTION
# ===========================================

CSRF_COOKIE_SECURE = False  # Cambiar a True en producción
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_TRUSTED_ORIGINS = [
    'http://localhost', 
    'http://127.0.0.1', 
    'http://localhost:8000',
    'https://*.onrender.com',
    'https://*.railway.app',
]


# ===========================================
# SEGURIDAD - SSL/HTTPS (DESARROLLO)
# ===========================================
# En desarrollo usamos HTTP, por lo que estas están en False
SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False

# ===========================================
# SEGURIDAD ADICIONAL
# ===========================================
# Protección contra clickjacking
X_FRAME_OPTIONS = 'DENY'

# Protección XSS
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True

# ===========================================
# DJANGO REST FRAMEWORK
# ===========================================
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ]
}

# ===========================================
# CONFIGURACIÓN PARA PRODUCCIÓN
# ===========================================
# Cuando DEBUG=False, activar todas las medidas de seguridad
if not DEBUG:
    # SSL/HTTPS obligatorio
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    
    # HSTS (HTTP Strict Transport Security)
    SECURE_HSTS_SECONDS = 31536000  # 1 año
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    
    # Proxy SSL
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    
    # Cookies más estrictas
    SESSION_COOKIE_SAMESITE = 'Strict'
    CSRF_COOKIE_SAMESITE = 'Strict'
    
    # Dominio de producción desde .env
    PRODUCTION_URL = config('PRODUCTION_URL', default='')
    if PRODUCTION_URL:
        CSRF_TRUSTED_ORIGINS = [PRODUCTION_URL]
        ALLOWED_HOSTS = [PRODUCTION_URL.replace('https://', '').replace('http://', '')]

# ===========================================
# LOGGING (Opcional - para debugging)
# ===========================================
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
        },
        'main': {  # Tu app
            'handlers': ['console', 'file'],
            'level': 'DEBUG' if DEBUG else 'INFO',
        },
    },
}

# Crear directorio de logs si no existe
LOGS_DIR = BASE_DIR / 'logs'
if not LOGS_DIR.exists():
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

# ===========================================
# CONFIGURACIÓN DEL ADMIN
# ===========================================
ADMIN_SITE_TITLE = "INACAP Tutorías - Panel Administrativo"
ADMIN_INDEX_TITLE = "Bienvenido al Panel de Administración"
ADMIN_SITE_HEADER = "INACAP Tutorías"

# Habilitar filtros numéricos en el admin
DJANGO_ADMIN_NUMERIC_RANGE_FILTER = True