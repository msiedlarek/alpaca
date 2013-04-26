import logging

import colander
import deform
from pyramid import httpexceptions

from alpaca.common.utilities.interfaces import (
    IRandomGenerator,
    IPasswordProcessor,
)
from alpaca.common.services.interfaces import (
    IUserService,
    IEnvironmentService,
)
from alpaca.common.domain.user import User
from alpaca.common.domain.environment import Environment

from alpaca.frontend.i18n import translate as _
from alpaca.frontend.forms import CSRFSecuredSchema


logger = logging.getLogger(__name__)


class ConfigurationView:

    _default_password_length = 10
    _invalid_form_message = _(
        "There was a problem with your submission. Please check the form for"
        " details."
    )

    def __init__(self, request):
        self.request = request
        self.user_service = request.registry.getAdapter(
            self.request.persistence_manager,
            IUserService
        )
        self.environment_service = request.registry.getAdapter(
            self.request.persistence_manager,
            IEnvironmentService
        )
        self.all_users = self.user_service.get_all_users()

    def __call__(self):
        actions = {
            'submit-update-permissions': self._action_update_permissions,
            'submit-new-user': self._action_new_user,
            'submit-new-environment': self._action_new_environment,
            'submit-delete-user': self._action_delete_user,
            'submit-delete-environment': self._action_delete_environment,
            'submit-reset-user-password': self._action_reset_user_password,
        }
        context = {}
        for submit_name, action in actions.items():
            result = action(submit_name)
            if isinstance(result, httpexceptions.HTTPException):
                return result
            context.update(result)
        context['authenticated_user_id'] = self.request.user.id
        context['users'] = [
            {
                'id': user.id,
                'email': user.email,
                'reset_password_form': deform.Form(
                    ResetUserPasswordSchema().bind(
                        session=self.request.session
                    ),
                    buttons=(
                        deform.Button(
                            name='submit-reset-user-password',
                            title=_("Reset password"),
                            css_class='btn-mini'
                        ),
                    ),
                    bootstrap_form_style='form-inline'
                ).render({'id': user.id}),
                'delete_form': (
                    None
                    if user.id == self.request.user.id else
                    deform.Form(
                        DeleteUserSchema().bind(
                            session=self.request.session
                        ),
                        buttons=(
                            deform.Button(
                                name='submit-delete-user',
                                title=_("Delete"),
                                css_class='btn-mini btn-danger'
                            ),
                        ),
                        bootstrap_form_style='form-inline'
                    ).render({'id': user.id})
                ),
            }
            for user in self.all_users
        ]
        context['environments'] = [
            {
                'id': environment.id,
                'name': environment.name,
                'delete_form': deform.Form(
                    DeleteEnvironmentSchema().bind(
                        session=self.request.session
                    ),
                    buttons=(
                        deform.Button(
                            name='submit-delete-environment',
                            title=_("Delete"),
                            css_class='btn-mini btn-danger'
                        ),
                    ),
                    bootstrap_form_style='form-inline'
                ).render({'id': environment.id}),
            }
            for environment in self.environment_service.get_all_environments()
        ]
        return context

    def _action_new_user(self, submit_name):
        new_user_form = deform.Form(
            NewUserSchema().bind(
                session=self.request.session,
                user_service=self.user_service,
            ),
            buttons=(
                deform.Button(
                    name=submit_name,
                    title=_("Add user")
                ),
            )
        )
        if submit_name in self.request.POST:
            try:
                appstruct = new_user_form.validate(self.request.POST.items())
            except deform.ValidationFailure:
                self.request.session.flash(
                    self._invalid_form_message,
                    queue='error'
                )
            else:
                user = User(
                    email=appstruct['email']
                )
                password = self._reset_user_password(user)
                self.user_service.create_user(user)
                self.request.session.flash(
                    _(
                        "User ${email} has been successfuly added with"
                        " password ${password}",
                        mapping={
                            'email': user.email,
                            'password': password,
                        }
                    ),
                    queue='success'
                )
                return httpexceptions.HTTPFound(self.request.url)
        return {
            'new_user_form': new_user_form.render(),
        }

    def _action_new_environment(self, submit_name):
        new_environment_form = deform.Form(
            NewEnvironmentSchema().bind(
                session=self.request.session,
                environment_service=self.environment_service,
            ),
            buttons=(
                deform.Button(
                    name=submit_name,
                    title=_("Add environment")
                ),
            )
        )
        if submit_name in self.request.POST:
            try:
                appstruct = new_environment_form.validate(
                    self.request.POST.items()
                )
            except deform.ValidationFailure:
                self.request.session.flash(
                    self._invalid_form_message,
                    queue='error'
                )
            else:
                environment = Environment(
                    name=appstruct['name']
                )
                self.environment_service.create_environment(environment)
                self.request.session.flash(
                    _("Environment has been successfuly added."),
                    queue='success'
                )
                return httpexceptions.HTTPFound(self.request.url)
        return {
            'new_environment_form': new_environment_form.render(),
        }

    def _action_delete_user(self, submit_name):
        if submit_name in self.request.POST:
            delete_user_form = deform.Form(DeleteUserSchema())
            try:
                appstruct = delete_user_form.validate(
                    self.request.POST.items()
                )
            except deform.ValidationFailure:
                pass
            else:
                if appstruct['id'] == self.request.user.id:
                    raise httpexceptions.HTTPBadRequest()
                user = self.user_service.get_user(appstruct['id'])
                if user is not None:
                    user_email = user.email
                    self.user_service.delete_user(user)
                    self.request.session.flash(
                        _(
                            "User ${email} has been successfuly deleted.",
                            mapping={
                                'email': user_email,
                            }
                        ),
                        queue='success'
                    )
            return httpexceptions.HTTPFound(self.request.url)
        return {}

    def _action_delete_environment(self, submit_name):
        if submit_name in self.request.POST:
            delete_environment_form = deform.Form(DeleteEnvironmentSchema())
            try:
                appstruct = delete_environment_form.validate(
                    self.request.POST.items()
                )
            except deform.ValidationFailure:
                pass
            else:
                environment = self.environment_service.get_environment(
                    appstruct['id']
                )
                if environment is not None:
                    environment_name = environment.name
                    self.environment_service.delete_environment(environment)
                    self.request.session.flash(
                        _(
                            "Environment ${environment_name} has been"
                            " successfuly deleted.",
                            mapping={
                                'environment_name': environment_name,
                            }
                        ),
                        queue='success'
                    )
            return httpexceptions.HTTPFound(self.request.url)
        return {}

    def _action_reset_user_password(self, submit_name):
        if submit_name in self.request.POST:
            reset_user_password_form = deform.Form(ResetUserPasswordSchema())
            try:
                appstruct = reset_user_password_form.validate(
                    self.request.POST.items()
                )
            except deform.ValidationFailure:
                pass
            else:
                user = self.user_service.get_user(appstruct['id'])
                if user is not None:
                    user_email = user.email
                    password = self._reset_user_password(user)
                    self.user_service.update_user(user)
                    self.request.session.flash(
                        _(
                            "User ${email} has been given new password:"
                            " ${password}",
                            mapping={
                                'email': user_email,
                                'password': password,
                            }
                        ),
                        queue='success'
                    )
            return httpexceptions.HTTPFound(self.request.url)
        return {}

    def _action_update_permissions(self, submit_name):
        update_permissions_form = deform.Form(
            UpdateUserPermissionsSchema().bind(
                session=self.request.session
            ),
            buttons=(
                deform.Button(
                    name=submit_name,
                    title=_("Save permissions")
                ),
            )
        )
        if submit_name in self.request.POST:
            try:
                appstruct = update_permissions_form.validate(
                    self.request.POST.items()
                )
            except deform.ValidationFailure:
                raise
            else:
                permissions_dict = {
                    row['id']: {
                        'is_administrator': row['is_administrator'],
                    }
                    for row in appstruct['user_permissions']
                    if row['id'] != self.request.user.id
                }
                self.user_service.set_user_permissions(permissions_dict)
                self.request.session.flash(
                    _("User permissions have been successfuly saved."),
                    queue='success'
                )
            return httpexceptions.HTTPFound(self.request.url)
        update_permissions_form.set_appstruct({
            'user_permissions': [
                {
                    'id': user.id,
                    'email': user.email,
                    'is_administrator': user.is_administrator,
                }
                for user in self.all_users
            ],
        })
        return {
            'update_permissions_form': update_permissions_form,
        }

    def _reset_user_password(self, user):
        random_generator = self.request.registry.getUtility(IRandomGenerator)
        password_processor_name = (
            self.request.registry.settings['alpaca.password_processor']
        )
        password_processor = self.request.registry.getUtility(
            IPasswordProcessor,
            password_processor_name
        )
        password = random_generator(self._default_password_length)
        user.set_password(
            password,
            password_processor_name,
            password_processor
        )
        return password


@colander.deferred
def _validate_user_email(node, kwargs):
    def __validate(value):
        user_service = kwargs['user_service']
        if user_service.get_user_by_email(value) is not None:
            return _("There is already a user with this email.")
        return True
    return colander.All(
        colander.Email(),
        colander.Function(__validate)
    )


class NewUserSchema(CSRFSecuredSchema):

    email = colander.SchemaNode(
        colander.String(),
        validator=_validate_user_email,
    )


class DeleteUserSchema(CSRFSecuredSchema):

    id = colander.SchemaNode(
        colander.Integer(),
        widget=deform.widget.HiddenWidget()
    )


class ResetUserPasswordSchema(CSRFSecuredSchema):

    id = colander.SchemaNode(
        colander.Integer(),
        widget=deform.widget.HiddenWidget()
    )


@colander.deferred
def _validate_environment_name(node, kwargs):
    def __validate(value):
        environment_service = kwargs['environment_service']
        if environment_service.get_environment_by_name(value) is not None:
            return _("There is already an environment defined with this name.")
        return True
    return colander.Function(__validate)


class NewEnvironmentSchema(CSRFSecuredSchema):

    name = colander.SchemaNode(
        colander.String(),
        validator=_validate_environment_name
    )


class DeleteEnvironmentSchema(CSRFSecuredSchema):

    id = colander.SchemaNode(
        colander.Integer(),
        widget=deform.widget.HiddenWidget()
    )


class UserPermissionsSchema(colander.MappingSchema):

    id = colander.SchemaNode(
        colander.Integer(),
        widget=deform.widget.HiddenWidget()
    )
    email = colander.SchemaNode(
        colander.String(),
        missing=''
    )
    is_administrator = colander.SchemaNode(colander.Boolean())


class UserPermissionsSequenceSchema(colander.SequenceSchema):

    user_permissions = UserPermissionsSchema()


class UpdateUserPermissionsSchema(CSRFSecuredSchema):

    user_permissions = UserPermissionsSequenceSchema()
