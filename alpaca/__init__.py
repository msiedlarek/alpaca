import logging
import importlib
import flask
import mongoengine

__all__ = ('create_application',)

DEFAULT_CONFIGURATION_MODULE = 'alpaca.configuration'

def create_application(configuration_module=DEFAULT_CONFIGURATION_MODULE,
                       override_configuration=None):
    # Create application instance
    application = flask.Flask(__name__, static_url_path='/global-static')
    # Load configuration
    application.config.from_object(configuration_module)
    # Override configuration
    if override_configuration is not None:
        for name, value in override_configuration.iteritems():
            application.config[name] = value
    # Setup log file
    if application.config['LOG_FILE'] is not None:
        handler = logging.FileHandler(application.config['LOG_FILE'])
        handler.setLevel(logging.INFO)
        handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
                '[in %(pathname)s:%(lineno)d]'
        ))
        application.logger.addHandler(handler)
    # Register blueprint modules
    for module_name, url_prefix in application.config['BLUEPRINTS']:
        blueprint_module = importlib.import_module(module_name)
        application.register_blueprint(blueprint_module.blueprint,
                                       url_prefix=url_prefix)
    # Register error handler
    register_error_handler(application)
    # Set up extensions
    setup_extensions(application)
    # Connect to MongoDB databases
    database_connect(application)
    # Return complete application object
    return application

def setup_extensions(application):
    from alpaca.ext import bcrypt, login_manager, assets, babel
    bcrypt.init_app(application)
    login_manager.setup_app(application)
    assets.init_app(application)
    babel.init_app(application)

def database_connect(application):
    if application.config['TESTING']:
        mongoengine.register_connection(
            'default',
            **application.config['MONGODB_CONNECTIONS']['testing']
        )
    else:
        mongoengine.register_connection(
            'default',
            **application.config['MONGODB_CONNECTIONS']['default']
        )

def register_error_handler(application):
    def error_handler(error):
        return flask.render_template('error/500.html'), 500
    application.error_handler_spec[None][500] = error_handler
