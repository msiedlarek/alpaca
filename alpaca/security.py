from pyramid.traversal import DefaultRootFactory
from pyramid.security import Everyone, Authenticated, Allow

User = 'alpaca.security.User'
Administrator = 'alpaca.security.Administrator'

class RootFactory(DefaultRootFactory):
    __acl__ = [
        (Allow, Everyone,      'alpaca.api.access'),
        (Allow, Everyone,      'alpaca.users.sign_in'),
        (Allow, Authenticated, 'alpaca.users.sign_out'),
        (Allow, Authenticated, 'alpaca.users.account'),
        (Allow, User,          'alpaca.problems.access'),
        (Allow, Administrator, 'alpaca.configuration.access'),
    ]
