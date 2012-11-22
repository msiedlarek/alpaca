from sqlalchemy.orm import exc as database_exceptions
from pyramid.view import view_config
from pyramid import httpexceptions
from pyramid.i18n import get_localizer
from pyramid.security import authenticated_userid

from alpaca.models import DBSession, User, Environment
from alpaca import forms
from alpaca.translation import translate as _

@view_config(
    route_name='alpaca.configuration.configuration',
    renderer='alpaca:templates/configuration.jinja2',
    permission='alpaca.configuration.access',
)
def configuration(request):
    environments = DBSession.query(Environment).order_by('name')
    users = DBSession.query(User).order_by('email')
    # Changing permissions
    if 'change-permissions-submit' in request.POST:
        post_keys = filter(
            lambda key: key.startswith('role_administrator-'),
            request.POST.iterkeys()
        )
        user_ids = []
        for post_key in post_keys:
            try:
                user_ids.append(int(post_key.split('-')[-1]))
            except (KeyError, ValueError):
                continue
        DBSession.query(User).filter(
            User.id != authenticated_userid(request)
        ).update({
            'role_administrator': False,
        })
        DBSession.query(User).filter(
            User.id != authenticated_userid(request),
            User.id.in_(user_ids)
        ).update({
            'role_administrator': True,
        }, synchronize_session=False)
        request.session.flash(
            get_localizer(request).translate(_(
                "User permissions have been successfuly saved."
            )),
            queue='success'
        )
        return httpexceptions.HTTPFound(
            request.route_url('alpaca.configuration.configuration')
        )
    # Adding user
    add_user_form = forms.AddUserForm(csrf_context=request)
    if 'add-user-submit' in request.POST:
        add_user_form.process(request.POST)
        if add_user_form.validate():
            user = User()
            add_user_form.populate_obj(user)
            new_password = user.generate_random_password()
            DBSession.add(user)
            request.session.flash(
                get_localizer(request).translate(_(
                    "New user <code>${email}</code> has been successfuly"
                    " created. Its temporary password is:"
                    " <code>${password}</code>",
                    mapping={
                        'email': user.email,
                        'password': new_password,
                    }
                )),
                queue='success'
            )
            return httpexceptions.HTTPFound(
                request.route_url('alpaca.configuration.configuration')
            )
        else:
            request.session.flash(
                get_localizer(request).translate(_(
                    "There were some problems with your request."
                    " Please check the form for error messages."
                )),
                queue='error'
            )
    # Resetting user password
    if 'reset-user-password-submit' in request.POST:
        reset_user_password_form = forms.ResetUserPasswordForm(
            request.POST,
            csrf_context=request
        )
        if reset_user_password_form.validate():
            try:
                user = DBSession.query(User).filter(
                    User.id == reset_user_password_form.user_id.data
                ).one()
            except database_exceptions.NoResultFound:
                raise httpexceptions.HTTPNotFound()
            new_password = user.generate_random_password()
            DBSession.add(user)
            request.session.flash(
                get_localizer(request).translate(_(
                    "New password for user <code>${email}</code> is:"
                    " <code>${password}</code>",
                    mapping={
                        'email': user.email,
                        'password': new_password,
                    }
                )),
                queue='success'
            )
        return httpexceptions.HTTPFound(
            request.route_url('alpaca.configuration.configuration')
        )
    # Deleting user
    if 'delete-user-submit' in request.POST:
        delete_user_form = forms.DeleteUserForm(
            request.POST,
            csrf_context=request
        )
        if delete_user_form.validate():
            DBSession.query(User).filter(
                User.id == delete_user_form.user_id.data
            ).delete()
            request.session.flash(
                get_localizer(request).translate(_(
                    "User has been successfuly deleted."
                )),
                queue='success'
            )
            return httpexceptions.HTTPFound(
                request.route_url('alpaca.configuration.configuration')
            )
        else:
            request.session.flash(
                get_localizer(request).translate(_(
                    "There were some problems with your request."
                    " Please check the form for error messages."
                )),
                queue='error'
            )
    # Adding environment
    add_environment_form = forms.AddEnvironmentForm(csrf_context=request)
    if 'add-environment-submit' in request.POST:
        add_environment_form.process(request.POST)
        if add_environment_form.validate():
            environment = Environment()
            add_environment_form.populate_obj(environment)
            environment.regenerate_api_key()
            DBSession.add(environment)
            request.session.flash(
                get_localizer(request).translate(_(
                    "New environment <code>${name}</code> has been successfuly"
                    " created. Its API key is: <code>${api_key}</code>",
                    mapping={
                        'name': environment.name,
                        'api_key': environment.api_key,
                    }
                )),
                queue='success'
            )
            return httpexceptions.HTTPFound(
                request.route_url('alpaca.configuration.configuration')
            )
        else:
            request.session.flash(
                get_localizer(request).translate(_(
                    "There were some problems with your request."
                    " Please check the form for error messages."
                )),
                queue='error'
            )
    # Regenerating environment API key
    if 'regenerate-environment-api-key-submit' in request.POST:
        regenerate_api_key_form = forms.RegenerateEnvironmentApiKeyForm(
            request.POST,
            csrf_context=request
        )
        if regenerate_api_key_form.validate():
            try:
                environment = DBSession.query(Environment).filter(
                    (Environment.id ==
                        regenerate_api_key_form.environment_id.data)
                ).one()
            except database_exceptions.NoResultFound:
                raise httpexceptions.HTTPNotFound()
            environment.regenerate_api_key()
            DBSession.add(environment)
            request.session.flash(
                get_localizer(request).translate(_(
                    "New API key for environment <code>${name}</code> is:"
                    " <code>${api_key}</code>",
                    mapping={
                        'name': environment.name,
                        'api_key': environment.api_key,
                    }
                )),
                queue='success'
            )
        return httpexceptions.HTTPFound(
            request.route_url('alpaca.configuration.configuration')
        )
    # Deleting environment
    if 'delete-environment-submit' in request.POST:
        delete_environment_form = forms.DeleteEnvironmentForm(
            request.POST,
            csrf_context=request
        )
        if delete_environment_form.validate():
            DBSession.query(Environment).filter(
                Environment.id == delete_environment_form.environment_id.data
            ).delete()
            request.session.flash(
                get_localizer(request).translate(_(
                    "Environment has been successfuly deleted."
                )),
                queue='success'
            )
            return httpexceptions.HTTPFound(
                request.route_url('alpaca.configuration.configuration')
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
        'environments': [
            {
                'id': environment.id,
                'name': environment.name,
                'url': request.route_url(
                    'alpaca.problems.environment',
                    environment_name=environment.name
                ),
                'delete_form': forms.DeleteEnvironmentForm(
                    environment_id=environment.id,
                    csrf_context=request
                ),
                'regenerate_api_key_form': (
                    forms.RegenerateEnvironmentApiKeyForm(
                        environment_id=environment.id,
                        csrf_context=request
                    )
                ),
            }
            for environment in environments
        ],
        'users': [
            {
                'id': user.id,
                'email': user.email,
                'role_administrator': user.role_administrator,
                'delete_form': forms.DeleteUserForm(
                    user_id=user.id,
                    csrf_context=request
                ),
                'reset_password_form': forms.ResetUserPasswordForm(
                    user_id=user.id,
                    csrf_context=request
                ),
            }
            for user in users
        ],
        'add_environment_form': add_environment_form,
        'add_user_form': add_user_form,
    }
