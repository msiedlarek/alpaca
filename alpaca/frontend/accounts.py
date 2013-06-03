import time
import random

import colander
import deform
import pyramid.security
from pyramid import httpexceptions
from pkg_resources import resource_stream

from alpaca.common.utilities.interfaces import IPasswordProcessor
from alpaca.common.services.interfaces import IUserService
from alpaca.frontend.i18n import translate as _
from alpaca.frontend.forms import CSRFSecuredSchema


def sign_in(request):
    authentication_form = deform.Form(
        AuthenticationSchema().bind(
            session=request.session
        ),
        buttons=(
            deform.Button(
                name='submit-authentication-form',
                title=_("Sign in")
            ),
        )
    )
    if request.method == 'POST':
        try:
            appstruct = authentication_form.validate(request.POST.items())
        except deform.ValidationFailure:
            pass
        else:
            user_service = request.registry.getAdapter(
                request.persistence_manager,
                IUserService
            )
            user = user_service.get_user_by_email(appstruct['email'])
            if user is not None:
                password_correct = user.password_equals(
                    appstruct['password'],
                    request.registry
                )
                if password_correct:
                    destination = request.GET.get('destination')
                    if destination is None:
                        destination = request.route_url(
                            'alpaca.frontend.monitoring.dashboard'
                        )
                    else:
                        destination = request.host_url + destination
                    headers = pyramid.security.remember(request, user.id)
                    return httpexceptions.HTTPSeeOther(
                        destination,
                        headers=headers
                    )
            # Password processor already guarantees constant comparsion time to
            # prevent timing attack, so this 1 second is just to piss them
            # nasty blackhats off.
            time.sleep(1)
            request.session.flash(
                _("Invalid credentials."),
                queue='error'
            )
    return {
        'authentication_form': authentication_form.render(),
        'alpaca_fact': _get_random_alpaca_fact(),
    }


def sign_out(request):
    sign_out_form = deform.Form(
        SignOutSchema().bind(
            session=request.session
        )
    )
    try:
        sign_out_form.validate(request.POST.items())
    except deform.ValidationFailure:
        raise
        raise httpexceptions.HTTPBadRequest()
    headers = pyramid.security.forget(request)
    return httpexceptions.HTTPSeeOther(
        request.route_url('alpaca.frontend.accounts.sign_in'),
        headers=headers
    )


def settings(request):
    change_password_form = deform.Form(
        ChangePasswordSchema().bind(
            session=request.session
        ),
        buttons=(
            deform.Button(
                name='submit-change-password',
                title=_("Change password")
            ),
        )
    )
    if request.method == 'POST':
        try:
            appstruct = change_password_form.validate(request.POST.items())
        except deform.ValidationFailure:
            pass
        else:
            password_processor_name = (
                request.registry.settings['alpaca.password_processor']
            )
            password_processor = request.registry.getUtility(
                IPasswordProcessor,
                password_processor_name
            )
            request.user.set_password(
                appstruct['password'],
                password_processor_name,
                password_processor
            )
            request.session.flash(
                _("Your password has been successfuly changed."),
                queue='success'
            )
    return {
        'change_password_form': change_password_form.render(),
    }


class AuthenticationSchema(CSRFSecuredSchema):

    email = colander.SchemaNode(
        colander.String(),
        validator=colander.Email(),
    )
    password = colander.SchemaNode(
        colander.String(),
        widget=deform.widget.PasswordWidget()
    )


class SignOutSchema(CSRFSecuredSchema):
    pass


class ChangePasswordSchema(CSRFSecuredSchema):

    password = colander.SchemaNode(
        colander.String(),
        title=_("New password"),
        widget=deform.widget.CheckedPasswordWidget()
    )


_alpaca_facts = None
def _get_random_alpaca_fact():
    global _alpaca_facts
    if _alpaca_facts is None:
        with resource_stream(__name__, 'resources/alpaca_facts.txt') as file:
            _alpaca_facts = tuple((
                fact.strip() for fact in file.readlines() if fact.strip()
            ))
    return random.choice(_alpaca_facts)
