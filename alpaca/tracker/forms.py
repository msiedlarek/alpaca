from flaskext import wtf

class LoginForm(wtf.Form):
    username = wtf.TextField("Username", validators=(
        wtf.Required(),
        wtf.Length(max=50),
    ))
    password = wtf.PasswordField("Password", validators=(
        wtf.Required(),
        wtf.Length(max=100),
    ))

class LogoutForm(wtf.Form):
    pass

class ChangePasswordForm(wtf.Form):
    password = wtf.PasswordField(
        "New password",
        validators=(
            wtf.Required(),
            wtf.Length(min=6, max=100),
        ),
        description="Minimum 6 characters long.",
    )
    repeat_password = wtf.PasswordField(
        "Repeat password",
        validators=(
            wtf.Required(),
            wtf.Length(min=6, max=100),
        ),
    )

class TagsForm(wtf.Form):
    tags = wtf.TextField()
