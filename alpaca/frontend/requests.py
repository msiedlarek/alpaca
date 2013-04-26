from pyramid import security

from alpaca.common.persistence.interfaces import IPersistenceManager
from alpaca.common.services.interfaces import IUserService


def get_persistence_manager(request):
    return request.registry.getUtility(IPersistenceManager)


def get_user(request):
    authenticated_user_id = security.authenticated_userid(request)
    if authenticated_user_id is not None:
        user_service = request.registry.getAdapter(
            request.persistence_manager,
            IUserService
        )
        return user_service.get_user(authenticated_user_id)
    else:
        return None
