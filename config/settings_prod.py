"""
Production settings — overrides config.settings for deployed environments.
"""
from .settings import *
import os

DEBUG = False

ALLOWED_HOSTS = [h.strip() for h in os.getenv('ALLOWED_HOSTS', 'localhost').split(',')]

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

# -----------------------------------------------------------------------
# Security
# -----------------------------------------------------------------------
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
SECURE_CONTENT_TYPE_NOSNIFF = True

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
