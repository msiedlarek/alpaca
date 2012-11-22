from wtforms import fields, validators
from wtforms.ext.csrf.form import SecureForm as BaseSecureForm

from alpaca.models import DBSession, User, Environment
from alpaca.translation import translate as _

class SecureForm(BaseSecureForm):

    def generate_csrf_token(self, csrf_context):
        return csrf_context.session.get_csrf_token()

class AuthenticationForm(SecureForm):

    email = fields.TextField(
        "E-mail",
        validators=(
            validators.DataRequired(),
            validators.Length(max=200),
            validators.Email(),
        )
    )
    password = fields.PasswordField(
        "Password",
        validators=(
            validators.DataRequired(),
            validators.Length(max=1000),
        )
    )

class SignOutForm(SecureForm):
    pass

class ChangePasswordForm(SecureForm):

    password = fields.PasswordField(
        "Password",
        validators=(
            validators.DataRequired(),
            validators.Length(max=1000),
        )
    )
    password_repeated = fields.PasswordField(
        "Repeat password",
        validators=(
            validators.DataRequired(),
            validators.Length(max=1000),
            validators.EqualTo('password'),
        )
    )

class AddEnvironmentForm(SecureForm):

    name = fields.TextField(
        "Name",
        validators=(
            validators.DataRequired(),
            validators.Length(max=100),
            validators.Regexp(
                r'^[\S]+$',
                message=(
                    "Environment name cannot contain whitespace characters."
                )
            )
        )
    )

    def validate_name(self, field):
        count = DBSession.query(Environment).filter(
            Environment.name == field.data
        ).count()
        if count != 0:
            raise validators.ValidationError(
                _("There is already an environment having this name.")
            )

class RegenerateEnvironmentApiKeyForm(SecureForm):

    environment_id = fields.HiddenField(
        validators=(
            validators.DataRequired(),
        )
    )

class DeleteEnvironmentForm(SecureForm):

    environment_id = fields.HiddenField(
        validators=(
            validators.DataRequired(),
        )
    )

class AddUserForm(SecureForm):

    email = fields.TextField(
        "E-mail",
        validators=(
            validators.DataRequired(),
            validators.Length(max=200),
            validators.Email(),
        )
    )

    def validate_email(self, field):
        count = DBSession.query(User).filter(
            User.email == field.data
        ).count()
        if count != 0:
            raise validators.ValidationError(
                _("There is already an account registered with this e-mail"
                  " address.")
            )

class ResetUserPasswordForm(SecureForm):

    user_id = fields.HiddenField(
        validators=(
            validators.DataRequired(),
        )
    )

class DeleteUserForm(SecureForm):

    user_id = fields.HiddenField(
        validators=(
            validators.DataRequired(),
        )
    )
