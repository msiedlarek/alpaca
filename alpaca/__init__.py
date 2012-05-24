import importlib
import flask
import mongoengine

__all__ = ('create_application',)

DEFAULT_CONFIGURATION_MODULE = 'alpaca.configuration'

def create_application(configuration_module=DEFAULT_CONFIGURATION_MODULE):
    # Create application instance
    application = flask.Flask(__name__, static_url_path='/global-static')
    # Load configuration
    application.config.from_object(configuration_module)
    # Register blueprint modules
    for module_name, url_prefix in application.config['BLUEPRINTS']:
        blueprint_module = importlib.import_module(module_name)
        application.register_blueprint(blueprint_module.blueprint,
                                       url_prefix=url_prefix)
    # Set up extensions
    setup_extensions(application)
    # Connect to MongoDB databases
    database_connect(application)
    # Return complete application object
    return application

def setup_extensions(application):
    from alpaca.ext import bcrypt, login_manager
    bcrypt.init_app(application)
    login_manager.setup_app(application)

def database_connect(application):
    for alias, parameters in application.config['MONGODB_CONNECTIONS'].items():
        mongoengine.register_connection(alias, **parameters)
