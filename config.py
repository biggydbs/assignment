import os

_basedir = os.path.abspath(os.path.dirname("config.py"))

def _get_bool_env_var(varname, default=None):
    value = os.environ.get(varname, default)
    if value is None:
        return False
    elif isinstance(value, str) and value.lower() == 'false':
        return False
    elif bool(value) is False:
        return False
    else:
        return bool(value)

DEBUG = True
MONGODB_SERVER = "localhost"
MONGODB_PORT = 27017

SECRET_KEY = "assignment"
CSRF_ENABLED = True
CSRF_SESSION_KEY = "secret"

MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.googlemail.com')
MAIL_PORT = int(os.environ.get('MAIL_PORT', 465))
MAIL_USE_TLS = _get_bool_env_var('MAIL_USE_TLS', False)
MAIL_USE_SSL = _get_bool_env_var('MAIL_USE_SSL', True)
MAIL_USERNAME = os.environ.get('MAIL_USERNAME',"cinchire@gmail.com")
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER',"cinchire@gmail.com")

WEB_URL = "http://127.0.0.1:5000/"

