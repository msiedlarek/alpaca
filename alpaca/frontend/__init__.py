def main(global_configuration, **local_configuration):
    from pyramid.config import Configurator
    from pyramid.threadlocal import manager
    settings = global_configuration
    settings.update(local_configuration)
    configurator = Configurator(settings=settings)
    configurator.include(includeme)
    # Hook application registry to global `zope.component` registry,
    # register all components in it and unhook.
    configurator.hook_zca()
    manager.push({
        'registry': configurator.registry,
    })
    try:
        wsgi_application = configurator.make_wsgi_app()
    finally:
        manager.pop()
        configurator.unhook_zca()
    return wsgi_application


def includeme(configurator):
    from pyramid.session import UnencryptedCookieSessionFactoryConfig
    from pyramid.authentication import SessionAuthenticationPolicy
    from pyramid.authorization import ACLAuthorizationPolicy
    from alpaca.common.persistence.interfaces import IPersistenceManager
    from alpaca.common.persistence.persistence_manager import (
        PersistenceManager,
    )
    from alpaca.frontend.security import (
        authentication_callback,
        RootFactory,
    )
    from alpaca.frontend import requests

    settings = configurator.registry.settings

    configurator.set_session_factory(
        UnencryptedCookieSessionFactoryConfig(settings['session.secret'])
    )
    configurator.set_root_factory(RootFactory)
    configurator.set_authorization_policy(ACLAuthorizationPolicy())
    configurator.set_authentication_policy(
        SessionAuthenticationPolicy(callback=authentication_callback)
    )

    configurator.include('pyramid_tm')
    configurator.include('pyramid_zcml')
    configurator.include('pyramid_layout')
    configurator.include('deform_bootstrap')

    configurator.load_zcml(
        settings.get(
            'alpaca.component_configuration_path',
            'alpaca.frontend:configure.zcml'
        )
    )

    persistence_manager = PersistenceManager(
        configurator.registry.settings
    )
    configurator.registry.registerUtility(
        persistence_manager,
        IPersistenceManager
    )

    configurator.add_request_method(
        requests.get_persistence_manager,
        name='persistence_manager',
        property=True,
        reify=True
    )
    configurator.add_request_method(
        requests.get_user,
        name='user',
        property=True,
        reify=True
    )
