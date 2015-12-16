# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '<SECRET KEY>'

DEBUG = True

ALLOWED_HOSTS = ['*']

# Email server settings
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587

EMAIL_HOST_USER = "mhrdapp@gmail.com"

EMAIL_HOST_PASSWORD = "mhrdapp143"

EMAIL_USE_TLS = True

# Email Id which will appear in From header in email
EMAIL_FROM = "mhrdapp@gmail.com"

SERVER_EMAIL = "mhrdapp@gmail.com"

EMAIL_SUBJECT_PREFIX = '[MHRD] '

ADMINS = (
    ('Dheerendra Rathor', 'dheeru.rathor14@gmail.com'),
)

MEDIA_URL = "http://localhost:8000/media/"

STATIC_URL = "/static/"

SESSION_COOKIE_PATH = "/"

CSRF_COOKIE_PATH = "/"

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')