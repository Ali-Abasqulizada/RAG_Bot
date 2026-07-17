from config.settings.com import *

DEBUG = False

ALLOWED_HOSTS = ['*']


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': env('POSTGRE_NAME', default=""),
        'USER': env('POSTGRE_USER', default=""),
        'PASSWORD': env('POSTGRE_PASS', default=""),
        'HOST': env('POSTGRE_HOST', default=""),
        'PORT': env('POSTGRE_PORT', default="5432"),
    }
}

BASE_URL = 'https://b2club.az'
STATIC_ROOT = BASE_DIR / 'static'




#SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
#SECURE_SSL_REDIRECT = True
#SESSION_COOKIE_SECURE = True
#CSRF_COOKIE_SECURE = True
