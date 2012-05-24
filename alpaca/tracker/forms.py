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
