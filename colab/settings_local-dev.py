
DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', 
        'NAME': 'colab.db',
    }
}

# Local time zone
TIME_ZONE = 'America/Caracas'

# Language code for this installation
LANGUAGE_CODE = 'es'

################ LDAP
LDAP_ENABLED = True
LDAP_SERVER_URL = "ldap.mycompany.com"
LDAP_SERVER_O = "organization"
LDAP_SERVER_CN = "admin"
LDAP_SERVER_OU = "organization_unit"
LDAP_SERVER_BIND_PASSWORD = "password"

AUTH_LDAP_SERVER_URI = "ldap://{0}".format(LDAP_SERVER_URL)
AUTH_LDAP_BASE = "o={0}".format(LDAP_SERVER_O)
AUTH_LDAP_BIND_DN = "cn={0}, ou={1}, ".format(LDAP_SERVER_CN,LDAP_SERVER_OU)+AUTH_LDAP_BASE
AUTH_LDAP_BIND_PASSWORD = LDAP_SERVER_BIND_PASSWORD
AUTH_LDAP_USER__DN_TEMPLATE = 'uid=%(user)s,'+AUTH_LDAP_BASE
AUTH_LDAP_USER_SEARCH = LDAPSearch("ou={0},".format(LDAP_SERVER_OU)+AUTH_LDAP_BASE, ldap.SCOPE_SUBTREE, "(uid=%(user)s)")

################ Mail Server
SERVER_EMAIL = '"Colab Interlegis" <noreply@interlegis.leg.br>'
EMAIL_HOST_USER = SERVER_EMAIL

################ Solr
#SOLR_HOSTNAME = 'solr.interlegis.leg.br'
#SOLR_HOSTNAME = '10.1.2.154'
#SOLR_PORT = '8080'
SOLR_HOSTNAME = 'localhost'
SOLR_PORT = '8983'
SOLR_SELECT_PATH = '/solr/select'

#SOLR_COLAB_URI = 'http://colab.interlegis.leg.br'
SOLR_COLAB_URI = 'http://localhost'

# Make this unique, and don't share it with anybody.
SECRET_KEY = ')(jksdfhsjkadfhjkh234ns!8fqu-1186h$vuj'

################ Socks
#import socks
#SOCKS_TYPE = socks.PROXY_TYPE_SOCKS5
#SOCKS_SERVER = '127.0.0.1'
#SOCKS_PORT = 9050