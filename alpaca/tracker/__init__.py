import flask
from alpaca.ext import login_manager
from alpaca.tracker.models import User

__all__ = ('blueprint',)

blueprint = flask.Blueprint(
    'tracker',
    __name__,
    static_folder='static',
    template_folder='templates',
)

@login_manager.user_loader
def load_user(user_id):
    return User.objects.get(id=user_id)

import alpaca.tracker.assets
import alpaca.tracker.views
import alpaca.tracker.context_processors
