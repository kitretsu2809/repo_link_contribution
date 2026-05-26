"""
Production settings — overrides config.settings for deployed environments.
"""
from .settings import *
import os
from urllib.parse import urlparse

DEBUG = False

ALLOWED_HOSTS = [
    h.strip() for h in os.getenv(
        'ALLOWED_HOSTS',
        'localhost,127.0.0.1,.vercel.app'
    ).split(',')
    if h.strip()
]

CSRF_TRUSTED_ORIGINS = [
    origin.strip() for origin in os.getenv('CSRF_TRUSTED_ORIGINS', '').split(',')
    if origin.strip()
]

CORS_ALLOW_ALL_ORIGINS = True

APP_BASE_URL = os.getenv('APP_BASE_URL', '').strip()
if APP_BASE_URL:
    parsed = urlparse(APP_BASE_URL)
    host = parsed.hostname
    if host and host not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(host)
    if parsed.scheme and host:
        origin = f'{parsed.scheme}://{host}'
        if parsed.port:
            origin = f'{origin}:{parsed.port}'
        if origin not in CSRF_TRUSTED_ORIGINS:
            CSRF_TRUSTED_ORIGINS.append(origin)

# -----------------------------------------------------------------------
# Database — PostgreSQL
# -----------------------------------------------------------------------
import dj_database_url  # noqa: E402

DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL', 'sqlite:///db.sqlite3'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# -----------------------------------------------------------------------
# Static files
# -----------------------------------------------------------------------
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATIC_URL = '/static/'

# -----------------------------------------------------------------------
# Security
# -----------------------------------------------------------------------
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# -----------------------------------------------------------------------
# Logging — container-friendly (stdout)
# -----------------------------------------------------------------------
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {module} — {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

# -----------------------------------------------------------------------
# Celery — use env var for broker/backend URLs
# -----------------------------------------------------------------------
REDIS_URL = os.getenv('REDIS_URL', 'redis://redis:6379/0')
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
