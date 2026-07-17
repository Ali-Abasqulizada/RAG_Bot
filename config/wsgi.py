import os

from django.core.wsgi import get_wsgi_application

from dotenv import load_dotenv


load_dotenv()  # loads the configs from .env


ENVIRONMENT = os.getenv('ENVIRONMENT', 'dev')


os.environ.setdefault('DJANGO_SETTINGS_MODULE', f'config.settings.{ENVIRONMENT}')

application = get_wsgi_application()