"""Settings of Evo app.

"""

from configparser import ConfigParser
from base import file

conf = ConfigParser()
conf.read(file('config.ini'))

['Default']
# Application Configuration
DEFAULT_THEME              = 'Greybird'
DEFAULT_DECORATED          = True
DEFAULT_PASSWORD_PROTECTED = False
DEFAULT_PASSWORD           = '3cf108a4e0a498347a5a75a792f23212'
                             # md5 hash in reverse order

# Connection Configuration
DEFAULT_CONNECTION_CHECKING_SERVER = 'https://www.google.com'
DEFAULT_RESPONSE_WAIT = None
DEFAULT_REQUEST_WAIT  = 10

['Custom']
# Application Configuration
THEME      = conf.getint('Custom', 'theme')
DECORATED  = conf.getboolean('Custom', 'decorated')
PASSWORD_PROTECTED = conf.getboolean('Custom', 'password_protected')
PASSWORD = conf.get('Custom', 'hash')

# Connection Configuration
CONNECTION_CHECKING_SERVER = conf.get('Custom', 'connection_checking_server')
try:
    RESPONSE_WAIT = conf.getint('Custom', 'response_wait')
except ValueError:
    RESPONSE_WAIT = None
REQUEST_WAIT  = conf.getint('Custom', 'request_wait')
