import os
import sys

import transaction
from sqlalchemy import engine_from_config
from pyramid.paster import get_appsettings, setup_logging

from alpaca.models import DBSession, ModelBase, User

def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri>\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)

def main(argv=sys.argv):
    if len(argv) != 2:
        usage(argv)
    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    ModelBase.metadata.create_all(engine)
    user = User(
        email='admin@example.com',
        role_administrator=True
    )
    user.set_password('admin')
    DBSession.add(user)
    transaction.commit()
