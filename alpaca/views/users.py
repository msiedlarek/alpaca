from sqlalchemy.orm import exc as database_exceptions
from pyramid.view import view_config
from pyramid import security
from pyramid import httpexceptions
from pyramid.i18n import get_localizer
from pyramid.security import authenticated_userid

from alpaca.models import DBSession, User
from alpaca import forms
from alpaca.translation import translate as _

@view_config(
    route_name='alpaca.users.sign_in',
    renderer='alpaca:templates/sign_in.jinja2',
    permission='alpaca.users.sign_in'
)
def sign_in(request):
    destination = request.GET.get(
        'destination',
        request.route_url('alpaca.problems.dashboard')
    )
    sign_in_form = forms.AuthenticationForm(csrf_context=request)
    if request.method == 'POST':
        sign_in_form.process(request.POST)
        if sign_in_form.validate():
            try:
                user = DBSession.query(User).filter(
                    User.email == sign_in_form.email.data
                ).one()
            except database_exceptions.NoResultFound:
                pass
            else:
                if user.valid_password(sign_in_form.password.data):
                    return httpexceptions.HTTPFound(
                        destination,
                        headers=security.remember(request, user.id)
                    )
        request.session.flash(
            get_localizer(request).translate(_(
                "Invalid credentials."
            )),
            queue='error'
        )
    return {
        'sign_in_form': sign_in_form,
    }

@view_config(
    route_name='alpaca.users.sign_out',
    request_method='POST',
    permission='alpaca.users.sign_out'
)
def sign_out(request):
    sign_out_form = forms.SignOutForm(
        request.POST,
        csrf_context=request
    )
    if sign_out_form.validate():
        headers = security.forget(request)
    else:
        raise httpexceptions.HTTPBadRequest()
    return httpexceptions.HTTPSeeOther(
        request.route_url('alpaca.users.sign_in'),
        headers=headers
    )

@view_config(
    route_name='alpaca.users.account',
    renderer='alpaca:templates/account.jinja2',
    permission='alpaca.users.account'
)
def account(request):
    change_password_form = forms.ChangePasswordForm(
        csrf_context=request
    )
    if request.method == 'POST':
        change_password_form.process(request.POST)
        if change_password_form.validate():
            try:
                user = DBSession.query(User).filter(
                    User.id == authenticated_userid(request)
                ).one()
            except database_exceptions.NoResultFound:
                raise httpexceptions.HTTPNotFound()
            user.set_password(change_password_form.password.data)
            DBSession.add(user)
            request.session.flash(
                get_localizer(request).translate(_(
                    "Your password has been successfuly changed."
                )),
                queue='success'
            )
            return httpexceptions.HTTPFound(
                request.route_url('alpaca.users.account')
            )
        else:
            request.session.flash(
                get_localizer(request).translate(_(
                    "There were some problems with your request."
                    " Please check the form for error messages."
                )),
                queue='error'
            )
    return {
        'change_password_form': change_password_form,
    }
