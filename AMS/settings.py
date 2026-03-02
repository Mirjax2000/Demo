"""
Django settings for AMS project.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Načtení env souborů — .env (základní) + .env_rhemove (email credentials)
load_dotenv(override=True, verbose=True)
load_dotenv(Path(__file__).resolve().parent.parent / ".env_rhemove", override=True, verbose=True)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# SECURITY WARNING: keep the secret key used in production secret!
_secret_key = os.getenv("SECRET_KEY", default="")
if not _secret_key:
    if os.getenv("DJANGO_ENV") == "production":
        raise RuntimeError(
            "SECRET_KEY nesmí být prázdný v produkci! "
            "Nastavte proměnnou prostředí SECRET_KEY."
        )
    # Insecure fallback POUZE pro lokální vývoj
    _secret_key = "django-insecure-dev-only-NOT-FOR-PRODUCTION"
SECRET_KEY = _secret_key
SYSTEM_USERNAME = "allspark"

# Šifrování osobních údajů zákazníků (GDPR) — Fernet AES-128-CBC
FIELD_ENCRYPTION_KEY = os.getenv("FIELD_ENCRYPTION_KEY", default="")
if not FIELD_ENCRYPTION_KEY and os.getenv("DJANGO_ENV") == "production":
    raise RuntimeError(
        "FIELD_ENCRYPTION_KEY nesmí být prázdný v produkci! "
        "Nastavte proměnnou prostředí FIELD_ENCRYPTION_KEY."
    )


# Nastavení pro produkci: https nastaveni
IS_PRODUCTION = os.getenv("DJANGO_ENV") == "production"
USE_HTTPS = os.getenv("USE_HTTPS") == "true"
# --- bere bool z .envu
DEBUG = not IS_PRODUCTION
# --- https
CSRF_COOKIE_SECURE = IS_PRODUCTION and USE_HTTPS
SESSION_COOKIE_SECURE = IS_PRODUCTION and USE_HTTPS
SECURE_SSL_REDIRECT = IS_PRODUCTION and USE_HTTPS
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")


ALLOWED_HOSTS: list = os.getenv("ALLOWED_HOSTS", "127.0.0.1").split(",")


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "simple_history",
    "accounts",
    "app_sprava_montazi",
    "api_v1",
    # --- znakova sada pro dump/load
    "django_dump_load_utf8",
    # --- restframework
    "rest_framework",
    "rest_framework.authtoken",
    "drf_spectacular",
    # --- filtry a CORS
    "django_filters",
    "corsheaders",
    # --- model Phone
    "phonenumber_field",
]


REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "api_v1.authentication.CookieJWTAuthentication",
        "rest_framework.authentication.TokenAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "api_v1.permissions.RBACPermission",
    ],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_PAGINATION_CLASS": "api_v1.pagination.StandardPagination",
    "PAGE_SIZE": 25,
    # ── Rate limiting ──
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "30/minute",
        "user": "120/minute",
        "login": "5/minute",
    },
}
# --- token na API
TOKEN_EXPIRE_MINUTES = 1440
# model modul "phonenumber_field"
PHONENUMBER_DEFAULT_REGION = "CZ"
PHONENUMBER_DB_FORMAT = "E164"
PHONENUMBER_DEFAULT_FORMAT = "E164"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "simple_history.middleware.HistoryRequestMiddleware",
    "middleware.gdpr_audit_middleware.GDPRAuditMiddleware",
]

ROOT_URLCONF = "AMS.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "AMS.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.postgresql",
#         "NAME": os.getenv("DB_NAME"),
#         "USER": os.getenv("DB_USER"),
#         "PASSWORD": os.getenv("DB_PASSWORD"),
#         "HOST": os.getenv("DB_HOST", "localhost"),
#         "PORT": os.getenv("DB_PORT", "5432"),
#     }
# }


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


LANGUAGE_CODE = "cs"

TIME_ZONE = "Europe/Prague"
USE_TZ = True

USE_I18N = True
# --- static files pro collect statics
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
# --- pro ukladani soubor jako path z databze
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media/"


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Auth URLs — admin panel only
LOGIN_URL = "/admin/login/"
# --- email settings (webzdarma.cz — smtp.webzdarma.cz:587 STARTTLS)
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.webzdarma.cz"
EMAIL_PORT = 587
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")

EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = "Rhenus HD — AMS <montaze@rhemove.cz>"

# --- logovani chyb do adresare logs
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "login_file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": os.path.join(BASE_DIR, "logs", "login_failures.log"),
        },
        # Přidáme nový handler pro chyby
        "error_file": {
            "level": "ERROR",
            "class": "logging.FileHandler",
            "filename": os.path.join(BASE_DIR, "logs", "django_error.log"),
        },
        # GDPR audit log
        "gdpr_audit_file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": os.path.join(BASE_DIR, "logs", "gdpr_audit.log"),
            "formatter": "simple",
        },
    },
    "formatters": {
        "simple": {
            "format": "%(asctime)s %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "loggers": {
        "login": {
            "handlers": ["login_file"],
            "level": "INFO",
            "propagate": False,
        },
        # Přidáme nový logger pro všechny Django chyby
        "django": {
            "handlers": ["error_file"],
            "level": "ERROR",
            "propagate": True,
        },
        # GDPR audit — kdo přistupoval k osobním údajům
        "gdpr_audit": {
            "handlers": ["gdpr_audit_file"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

# --- swagger
SPECTACULAR_SETTINGS = {
    "TITLE": "AMS API",
    "VERSION": "2.0.0",
    "DESCRIPTION": "REST API pro systém správy montáží (AMS)",
    "SERVE_INCLUDE_SCHEMA": False,
    "SECURITY": [{"BearerAuth": []}, {"TokenAuth": []}],
    "COMPONENTS": {
        "securitySchemes": {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
            },
            "TokenAuth": {
                "type": "apiKey",
                "in": "header",
                "name": "Authorization",
            },
        },
    },
}

# --- CORS nastavení
CORS_ALLOWED_ORIGINS = os.getenv(
    "CORS_ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
).split(",")
CORS_ALLOW_CREDENTIALS = True

# --- JWT nastavení
from datetime import timedelta  # noqa: E402

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# --- JWT Cookie nastavení (httpOnly → ochrana proti XSS)
JWT_COOKIE_NAME = "ams_access"
JWT_REFRESH_COOKIE_NAME = "ams_refresh"
JWT_COOKIE_SECURE = IS_PRODUCTION and USE_HTTPS
JWT_COOKIE_SAMESITE = "Lax"
JWT_COOKIE_HTTPONLY = True
JWT_COOKIE_PATH = "/api/"
JWT_REFRESH_COOKIE_PATH = "/api/v1/auth/"

# CSRF pro cookie-based auth
CSRF_COOKIE_HTTPONLY = False  # FE musí číst CSRF token z cookie
CSRF_COOKIE_NAME = "csrftoken"
CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS.copy()
