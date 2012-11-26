import os
import json

from pyramid.config import Configurator
from pyramid.session import UnencryptedCookieSessionFactoryConfig
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from sqlalchemy import engine_from_config

from alpaca.models import DBSession, User
from alpaca.routes import ROUTES
from alpaca.security import RootFactory
from alpaca.assets import BUNDLES as ASSET_BUNDLES

def main(global_config, **settings):
    # Provide deployment-independent settings
    settings.update({
        # Webassets
        'webassets.base_dir': os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            'static'
        ),
        'webassets.base_url': settings.get('route.prefix', '') + '/static/',
        # Jinja2
        'jinja2.i18n.domain': 'alpaca',
    })
    # Configure database session.
    database_engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=database_engine)
    # Create configurator.
    config = Configurator(settings=settings)
    config.registry['settings'] = settings
    # Configure ACL.
    config.set_root_factory(RootFactory)
    # Configure security.
    authentication_policy = AuthTktAuthenticationPolicy(
        settings['session.secret'],
        callback=User.authentication_callback
    )
    config.set_authentication_policy(authentication_policy)
    authorization_policy = ACLAuthorizationPolicy()
    config.set_authorization_policy(authorization_policy)
    # Configure session.
    session_factory = UnencryptedCookieSessionFactoryConfig(
        settings['session.secret']
    )
    config.set_session_factory(session_factory)
    # Add translation directories.
    config.add_translation_dirs(os.path.join(
        os.path.dirname(__file__),
        'locale'
    ))
    # Include packages.
    config.include('pyramid_tm')
    config.include('pyramid_jinja2')
    config.include('pyramid_webassets')
    # Configure asset bundles.
    for name, bundle in ASSET_BUNDLES.iteritems():
        config.add_webasset(name, bundle)
    # Add Jinja2 extensions.
    config.add_jinja2_extension('jinja2.ext.with_')
    config.get_jinja2_environment().filters['tojson'] = json.dumps
    config.registry['jinja2_environment'] = config.get_jinja2_environment()
    # Add webassets extension to Jinja2.
    config.add_jinja2_extension('webassets.ext.jinja2.AssetsExtension')
    webassets_environment = config.get_webassets_env()
    config.get_jinja2_environment().assets_environment = webassets_environment
    # Configure routes.
    for name, pattern in ROUTES.iteritems():
        config.add_route(name, pattern)
    # Add static view.
    config.add_static_view('static', 'static', cache_max_age=3600)
    # Scan for view configuration.
    config.scan()
    return config.make_wsgi_app()
