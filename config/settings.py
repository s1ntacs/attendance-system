import os
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'local-development-only-change-before-deployment')
DEBUG = os.environ.get('DJANGO_DEBUG', '1') == '1'
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1,testserver').split(',')
INSTALLED_APPS = ['django.contrib.auth', 'django.contrib.contenttypes', 'django.contrib.sessions', 'django.contrib.messages', 'django.contrib.staticfiles', 'rest_framework', 'journal']
MIDDLEWARE = ['django.middleware.security.SecurityMiddleware','django.contrib.sessions.middleware.SessionMiddleware','django.middleware.common.CommonMiddleware','django.middleware.csrf.CsrfViewMiddleware','django.contrib.auth.middleware.AuthenticationMiddleware','django.contrib.messages.middleware.MessageMiddleware']
ROOT_URLCONF = 'config.urls'
TEMPLATES = [{'BACKEND':'django.template.backends.django.DjangoTemplates','DIRS':[BASE_DIR/'templates'],'APP_DIRS':True,'OPTIONS':{'context_processors':['django.template.context_processors.request','django.contrib.auth.context_processors.auth','django.contrib.messages.context_processors.messages']}}]
WSGI_APPLICATION = 'config.wsgi.application'
if os.environ.get('POSTGRES_HOST'):
 DATABASES = {'default': {'ENGINE':'django.db.backends.postgresql','NAME':os.environ['POSTGRES_DB'],'USER':os.environ['POSTGRES_USER'],'PASSWORD':os.environ['POSTGRES_PASSWORD'],'HOST':os.environ['POSTGRES_HOST'],'PORT':5432}}
else:
 DATABASES = {'default': {'ENGINE':'django.db.backends.sqlite3','NAME':BASE_DIR/'db.sqlite3'}}
AUTH_USER_MODEL = 'journal.User'
AUTH_PASSWORD_VALIDATORS = [{'NAME':'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},{'NAME':'django.contrib.auth.password_validation.MinimumLengthValidator'},{'NAME':'django.contrib.auth.password_validation.CommonPasswordValidator'},{'NAME':'django.contrib.auth.password_validation.NumericPasswordValidator'}]
LANGUAGE_CODE='ru-ru'
TIME_ZONE='Europe/Moscow'
USE_TZ=True
STATIC_URL='/static/'
STATIC_ROOT=BASE_DIR/'staticfiles'
DEFAULT_AUTO_FIELD='django.db.models.BigAutoField'
LOGIN_URL='/login/'
LOGIN_REDIRECT_URL='/'
LOGOUT_REDIRECT_URL='/login/'
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE='Lax'
CSRF_COOKIE_SAMESITE='Lax'
REST_FRAMEWORK={'DEFAULT_AUTHENTICATION_CLASSES':['rest_framework.authentication.SessionAuthentication'],'DEFAULT_PERMISSION_CLASSES':['rest_framework.permissions.IsAuthenticated'],'DEFAULT_RENDERER_CLASSES':['rest_framework.renderers.JSONRenderer'],'EXCEPTION_HANDLER':'journal.api.exception_handler'}
