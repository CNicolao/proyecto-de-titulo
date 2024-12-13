import os
from pathlib import Path
from dotenv import load_dotenv
from django.shortcuts import render


# Cargar variables de entorno desde .env
load_dotenv()

# Base Directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Seguridad
SECRET_KEY = os.getenv('SECRET_KEY', 'clave-predeterminada-no-segura')
DEBUG = os.getenv('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = [".replit.dev", ".replit.app",  '127.0.0.1', '192.168.1.2', 
    'localhost', ]

CSRF_TRUSTED_ORIGINS = os.getenv(
    'CSRF_TRUSTED_ORIGINS', 'https://*.replit.dev,https://*.replit.app'
).split(',')

# Aplicaciones
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'STIWEBSERVICE',
    'corsheaders', # Añadido para CORS
    'import_export', # Añadido para importar e exportar
    
       
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Añadido para CORS
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

if "REPLIT_DEPLOYMENT" in os.environ:
    MIDDLEWARE.append('django.middleware.clickjacking.XFrameOptionsMiddleware')

ROOT_URLCONF = 'django_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'django_project.wsgi.application'

# Base de Datos
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'stidb',  # Nombre de la base de datos
        'USER': 'stidb_owner',  # Usuario
        'PASSWORD': 'u94XPgVWxdmO',  # Contraseña
        'HOST': 'ep-dawn-frog-a5qrzwbk.us-east-2.aws.neon.tech',  # Host
        'PORT': '5432',  # Puerto predeterminado de PostgreSQL
        'OPTIONS': {
            'sslmode': 'require',  # Obligatorio para Neon
        },
    }
}

# Validación de contraseñas
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Configuración de Internacionalización
LANGUAGE_CODE = 'es-es'
TIME_ZONE = 'America/Santiago'
USE_I18N = True
USE_TZ = True

# Configuración de URLs
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'

# Archivos estáticos
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Configuración del modelo de usuario personalizado
AUTH_USER_MODEL = 'STIWEBSERVICE.CustomUser'

# Configuración de errores personalizados
HANDLER403 = 'django_project.settings.error_403'


def error_403(request, exception=None):
    return render(request, '403.html', status=403)

# Configuraciones de CORS
CORS_ALLOWED_ORIGINS = os.getenv(
    'CORS_ALLOWED_ORIGINS', 'http://localhost:3000,http://127.0.0.1:3000'
).split(',')

# Permitir todas las cabeceras y métodos para desarrollo
CORS_ALLOW_HEADERS = ['*']
CORS_ALLOW_METHODS = ['*']

#configuracion correo 
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'coordinadorticket.sti@gmail.com'
EMAIL_HOST_PASSWORD = 'xkfl ccxw rmum jjoo'
DEFAULT_FROM_EMAIL = 'coordinadorticket.sti@gmail.com'

# Configuraciones adicionales para producción
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_SECONDS = 31536000  # 1 año
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'