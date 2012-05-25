import os
import datetime

APPLICATION_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                '..'))

# Enable/disable debug mode
DEBUG = False

# Enable/disable testing mode
TESTING = False

# The secret key
SECRET_KEY = None

# The name of the session cookie
SESSION_COOKIE_NAME = 'session'

# The lifetime of a permanent session
PERMANENT_SESSION_LIFETIME = datetime.timedelta(days=30)

# List of blueprints to register in application and their URL prefixes
BLUEPRINTS = (
    ('alpaca.tracker', ''),
)

# Enables cross-site request forgery protection on WTForms
CSRF_ENABLED = True

# Mapping of API keys to their client identifiers
CLIENTS = {}

# Number of last occurences stored for each error
ERROR_OCCURRENCE_HISTORY_LIMIT = 30
