"""
Django settings for veo_menu_backend project.
"""

from pathlib import Path
from datetime import timedelta
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Helper function to replace decouple.config
def get_env(key, default=None, cast=None):
    value = os.environ.get(key)
    if value is None:
        return default
    if cast:
        if cast == bool:
            return str(value).lower() in ('true', '1', 'yes')
        elif cast == int:
            return int(value)
        else:
            return cast(value)
    return value

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_env('SECRET_KEY', 'django-insecure-*oh7c(dg)m&jph*sznq4mi(l==ux1($cm)h5=lsgt04x_f5cvt')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = get_env('DEBUG', True, cast=bool)

# Parse ALLOWED_HOSTS properly
allowed_hosts_str = get_env('ALLOWED_HOSTS', 'localhost,127.0.0.1')
if isinstance(allowed_hosts_str, str):
    ALLOWED_HOSTS = [s.strip() for s in allowed_hosts_str.split(',')]
else:
    ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Application definition
INSTALLED_APPS = [
    # Django admin theme
    'jazzmin',

    # Django core apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party apps
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_filters',
    'drf_spectacular',

    # Local apps
    'apps.authentication',
    'apps.instances',
    'apps.menus',
    'apps.analytics',
    'apps.support',
    'apps.ai',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # CORS before CommonMiddleware
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'veo_menu_backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'veo_menu_backend.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': get_env('DB_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': get_env('DB_NAME', BASE_DIR / 'db.sqlite3'),
        'USER': get_env('DB_USER', ''),
        'PASSWORD': get_env('DB_PASSWORD', ''),
        'HOST': get_env('DB_HOST', ''),
        'PORT': get_env('DB_PORT', ''),
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CORS Settings
cors_origins_str = get_env('CORS_ALLOWED_ORIGINS', 'http://localhost:3000,http://127.0.0.1:3000')
if isinstance(cors_origins_str, str):
    CORS_ALLOWED_ORIGINS = [s.strip() for s in cors_origins_str.split(',')]
else:
    CORS_ALLOWED_ORIGINS = ['http://localhost:3000', 'http://127.0.0.1:3000']
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'x-instance-id',  # Custom header for multi-tenancy
]

# REST Framework Settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# JWT Settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=get_env('JWT_ACCESS_TOKEN_LIFETIME', 60, cast=int)),
    'REFRESH_TOKEN_LIFETIME': timedelta(minutes=get_env('JWT_REFRESH_TOKEN_LIFETIME', 1440, cast=int)),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': get_env('JWT_SECRET_KEY', SECRET_KEY),
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}

# Email Settings (for magic links)
EMAIL_BACKEND = get_env('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = get_env('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = get_env('EMAIL_PORT', 587, cast=int)
EMAIL_USE_TLS = get_env('EMAIL_USE_TLS', True, cast=bool)
EMAIL_HOST_USER = get_env('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = get_env('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = get_env('DEFAULT_FROM_EMAIL', 'noreply@veomenu.com')

# Jazzmin Admin UI Settings
JAZZMIN_SETTINGS = {
    "site_title": "VEOmenu Admin",
    "site_header": "VEOmenu",
    "site_brand": "VEOmenu",
    "welcome_sign": "Welcome to VEOmenu Admin",
    "copyright": "VEOmenu",
    "search_model": "auth.User",
    "user_avatar": None,
    "topmenu_links": [
        {"name": "Home", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "API Docs", "url": "/api/schema/swagger-ui/", "new_window": True},
    ],
    "show_sidebar": True,
    "navigation_expanded": True,
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
    },
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
    "related_modal_active": False,
    "custom_css": None,
    "custom_js": None,
    "show_ui_builder": False,
    "changeform_format": "horizontal_tabs",
    "changeform_format_overrides": {"auth.user": "collapsible", "auth.group": "vertical_tabs"},
}

# API Documentation
SPECTACULAR_SETTINGS = {
    'TITLE': 'VEOmenu API',
    'DESCRIPTION': 'Multi-tenant digital menu platform API',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

# Custom User Model
AUTH_USER_MODEL = 'authentication.User'

# Frontend URL
FRONTEND_URL = get_env('FRONTEND_URL', 'http://localhost:3000')
