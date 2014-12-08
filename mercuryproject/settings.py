"""
Django settings for mercuryproject project.

For more information on this file, see
https://docs.djangoproject.com/en/dev/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/dev/ref/settings/
"""
from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS as TCP

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
SETTINGS_DIR = os.path.dirname(__file__)
PROJECT_PATH = os.path.join(SETTINGS_DIR, os.pardir)
PROJECT_PATH = os.path.abspath(PROJECT_PATH)
TEMPLATE_PATH = os.path.join(PROJECT_PATH, 'templates')


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/dev/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'j!7+2%t4ks7saoh^s1p)1#vu*p^csz*qex&s*b@rjgf0si^6g+'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'suit',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    #'django_extensions',
    'rest_framework',
    'rest_framework_swagger',
    'datetimewidget',
    'mercuryservices',
    'mercurylab',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'mercuryproject.urls'

WSGI_APPLICATION = 'mercuryproject.wsgi.application'


# Database
# https://docs.djangoproject.com/en/dev/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'mercurydev',
        'USER': 'mercury_admin',
        'PASSWORD': 'm3rcury@dm1n',
        #'HOST': 'IGSARMEWVSWIM5.gs.doi.net',
        #'HOST': '130.11.161.159',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Internationalization
# https://docs.djangoproject.com/en/dev/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Chicago'

USE_I18N = True

USE_L10N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/dev/howto/static-files/
STATIC_ROOT = os.path.join(PROJECT_PATH, 'static')
STATIC_PATH = os.path.join(PROJECT_PATH, 'static/staticfiles')
STATIC_URL = '/static/'

STATICFILES_DIRS = (
    STATIC_PATH,
)

TEMPLATE_DIRS = (
    TEMPLATE_PATH,
)

TEMPLATE_CONTEXT_PROCESSORS = TCP + (
    'django.core.context_processors.request',
)

REST_FRAMEWORK = {
    #'DEFAULT_FILTER_BACKENDS': ('rest_framework.filters.DjangoFilterBackend',)
    #'DEFAULT_RENDERER_CLASSES': (
        #'rest_framework.renderers.TemplateHTMLRenderer',
        #'rest_framework.renderers.BrowsableAPIRenderer',
        #'rest_framework.renderers.JSONRenderer',
    #)
}

SWAGGER_SETTINGS = {
    "info": {
        'description': 'This is the documentation site for the MeRLIn '
                       '(Mercury Research Lab Information Management System) REST Services.',
        'title': 'MeRLIn REST Services Documentation',
    },
}

SUIT_CONFIG = {
    'ADMIN_NAME': 'Mercury Lab Admin',
    #'MENU': ('sites', {'app': 'mercuryservices', 'icon': 'icon-cog', 'models': ('Cooperator', 'Project', 'Site')}),
}
