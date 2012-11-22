from pyramid import events, security

from alpaca.models import DBSession, Environment
from alpaca import forms

@events.subscriber(events.BeforeRender)
def add_user_id(event):
    event['user_id'] = security.authenticated_userid(event['request'])

@events.subscriber(events.BeforeRender)
def add_environments(event):
    environment_set = DBSession.query(
        Environment.id,
        Environment.name
    ).order_by(Environment.name);
    event['all_environments'] = [
        {
            'id':   environment.id,
            'name': environment.name
        }
        for environment in environment_set
    ]

@events.subscriber(events.BeforeRender)
def add_sign_out_form(event):
    event['sign_out_form'] = forms.SignOutForm(
        csrf_context=event['request']
    )

@events.subscriber(events.BeforeRender)
def add_permissions(event):
    event['permissions'] = {
        'can_access_configuration': security.has_permission(
            'alpaca.configuration.access',
            event['request'].context,
            event['request']
        ),
        'can_sign_out': security.has_permission(
            'alpaca.users.sign_out',
            event['request'].context,
            event['request']
        ),
        'can_access_account': security.has_permission(
            'alpaca.users.account',
            event['request'].context,
            event['request']
        ),
    }
