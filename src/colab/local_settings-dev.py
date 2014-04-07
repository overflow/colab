
from custom_settings import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
)

MANAGERS = ADMINS

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
#EMAIL_HOST = ''
#EMAIL_PORT = 587
EMAIL_SUBJECT_PREFIX = ''

# Make this unique, and don't share it with anybody.
SECRET_KEY = ')(jksdfhsjkadfhjkh234ns!8fqu-1186h$vuj'

SITE_URL = 'http://localhost:8000'

ALLOWED_HOSTS = ['*']

INTERNAL_IPS = ('127.0.0.1', )

CONVERSEJS_BOSH_SERVICE_URL = 'http://localhost:5280/http-bind'

DATABASES['default']['PASSWORD'] = 'colab'
DATABASES['default']['HOST'] = 'localhost'
DATABASES['trac']['PASSWORD'] = 'colab'
DATABASES['trac']['HOST'] = 'localhost'
DATABASES['mediawiki']['PASSWORD'] = 'colab'
DATABASES['mediawiki']['HOST'] = 'localhost'

'''Select the search engine you want to use "Solr or Whoosh" '''
#Configuration for Solr
HAYSTACK_CONNECTIONS['default']['URL'] = 'http://localhost:8983/solr/'

#Configuration for Whoosh
HAYSTACK_CONNECTIONS['default']['PATH'] = 'whoosh/'
HAYSTACK_CONNECTIONS['default']['ENGINE'] = 'haystack.backends.whoosh_backend.WhooshEngine'

COLAB_TRAC_URL = 'http://localhost:5000/'
COLAB_CI_URL = 'http://localhost:8080/ci/'

CONVERSEJS_ENABLED = False

DIAZO_THEME = SITE_URL
