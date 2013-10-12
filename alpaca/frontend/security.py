from pyramid.traversal import DefaultRootFactory
from pyramid.security import Everyone, Allow

from alpaca.common.services.interfaces import IUserService


User = 'alpaca.frontend.security.User'
Administrator = 'alpaca.frontend.security.Administrator'


class RootFactory(DefaultRootFactory):
    __acl__ = [
        (Allow, Everyone,      'alpaca.frontend.accounts.sign_in'),
        (Allow, User,          'alpaca.frontend.accounts.sign_out'),
        (Allow, User,          'alpaca.frontend.accounts.access_settings'),
        (Allow, User,          'alpaca.frontend.monitoring.access'),
        (Allow, Administrator, 'alpaca.frontend.configuration.access'),
    ]


def authentication_callback(user_id, request):
    user_service = request.registry.getAdapter(
        request.persistence_manager,
        IUserService
    )
    user = user_service.get_user(user_id)
    if user is None:
        return None
    if user.is_administrator:
        return (User, Administrator,)
    return (User,)
