#!/usr/bin/env python

import os
import sys

BASE_PATH = os.path.abspath(os.path.dirname(__file__))

def get_wsgi_application():
    PROJECT_PATH = os.path.join(BASE_PATH, 'alpaca')
    PYTHON_ENV_PATH = os.path.join(BASE_PATH, 'environment')
    PYTHON_ENV_ACTIVATOR = os.path.join(PYTHON_ENV_PATH, 'bin',
                                        'activate_this.py')
    # Activate virtualenv
    execfile(PYTHON_ENV_ACTIVATOR, dict(__file__=PYTHON_ENV_ACTIVATOR))
    # Insert important import paths at the beginning of PATH
    sys.path.insert(0, PROJECT_PATH)
    sys.path.insert(1, BASE_PATH)
    # Import WSGI application
    from alpaca import create_application
    return create_application()

application = get_wsgi_application()
