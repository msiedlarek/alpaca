from flaskext.bcrypt import Bcrypt
bcrypt = Bcrypt()

from flaskext.login import LoginManager
login_manager = LoginManager()
login_manager.login_view = 'tracker.login'
login_manager.login_message = "You must log in to see this page."
