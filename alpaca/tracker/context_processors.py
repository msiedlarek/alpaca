import flask
from alpaca.tracker import blueprint, forms

@blueprint.context_processor
def provide_logout_form():
    return dict(logout_form=forms.LogoutForm())

@blueprint.context_processor
def provide_reporters_list():
    return dict(reporters=flask.current_app.config['CLIENTS'].values())
