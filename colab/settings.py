# Django settings for colab project.

import os.path

gettext = lambda s: s

DEBUG = True
TEMPLATE_DEBUG = DEBUG

if DEBUG:
    import logging
    logging.root.setLevel(logging.DEBUG)


ADMINS = (
   ( 'admin', 'eliezerfot123@gmail.com'),
)

PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))

MANAGERS = ADMINS

LOGIN_URL = '/login/'

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
#TIME_ZONE = 'America/Sao_Paulo'
TIME_ZONE = 'America/Caracas'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
#LANGUAGE_CODE = 'pt-br'
LANGUAGE_CODE = 'es-ve'
LANGUAGES = (
    ('en', gettext('English')),
    ('es', gettext('Spanish')),
    ('pt-BR', gettext('Portuguese')),

)

LOCALE_PATHS = (PROJECT_PATH + "/locale",)

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

MEDIA_ROOT = os.path.join(PROJECT_PATH, os.pardir, 'site_media/media')
MEDIA_URL = '/media/'

STATIC_ROOT = os.path.join(PROJECT_PATH, os.pardir, 'site_media/static')
STATIC_URL = '/static/'

ADMIN_MEDIA_PREFIX = '/static/admin/'

# Additional locations of static files
STATICFILES_DIRS = (
    os.path.join(PROJECT_PATH, 'static'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.request',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    #'debug_toolbar.middleware.DebugToolbarMiddleware',
)

ROOT_URLCONF = 'colab.urls'

TEMPLATE_DIRS = (
    os.path.join(PROJECT_PATH, 'templates'),
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    
    # Not standard apps
    'south',
    'cliauth',
    #'debug_toolbar',

    # My apps
    'colab.super_archives',
    'colab.api',
    'colab.rss',
    'django_auth_ldap',
)

import ldap
from django_auth_ldap.config import LDAPSearch, GroupOfNamesType

AUTHENTICATION_BACKENDS = (
    'django_auth_ldap.backend.LDAPBackend',
    'django.contrib.auth.backends.ModelBackend',
)
AUTH_LDAP_SERVER_URI = "ldap://LDAP_SERVER_URL"
AUTH_LDAP_BASE = "o=organizacion"
AUTH_LDAP_BIND_DN = "cn=admin, ou=departamento,"+AUTH_LDAP_BASE
AUTH_LDAP_BIND_PASSWORD = "contrasena"
AUTH_LDAP_USER__DN_TEMPLATE = 'uid=%(user)s,'+AUTH_LDAP_BASE


AUTH_LDAP_USER_SEARCH = LDAPSearch("ou=plataforma,"+AUTH_LDAP_BASE, ldap.SCOPE_SUBTREE, "(uid=%(user)s)")

# Set up the basic group parameters.
AUTH_LDAP_USER_ATTR_MAP = {
    "first_name":"givenName",
    "last_name":"sn",
    "password":"userPassword",
    "email":"mail"
}

AUTH_LDAP_ALWAYS_UPDATE_USER = True

AUTH_LDAP_FIND_GROUP_PERMS = False

AUTH_LDAP_CACHE_GROUPS = True

AUTH_LDAP_GROUP_CACHE_TIMEOUT = 3600

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
            'filters': [],
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

SERVER_EMAIL = '"Colab Interlegis" <noreply@interlegis.leg.br>'
EMAIL_HOST_USER = SERVER_EMAIL

#SOLR_HOSTNAME = 'solr.interlegis.leg.br'
#SOLR_HOSTNAME = '10.1.2.154'
#SOLR_PORT = '8080'
SOLR_HOSTNAME = 'localhost'
SOLR_PORT = '8983'
SOLR_SELECT_PATH = '/solr/select'

#SOLR_COLAB_URI = 'http://colab.interlegis.leg.br'
SOLR_COLAB_URI = 'http://localhost'
SOLR_BASE_QUERY = """
    ((Type:changeset OR Type:ticket OR Type:wiki OR Type:thread) AND Title:["" TO *]) 
"""

from settings_local import *

