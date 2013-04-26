from zope import (
    interface,
    component,
)
from sqlalchemy.orm import exc as db_exc

from alpaca.common.persistence.interfaces import IPersistenceManager
from alpaca.common.services.interfaces import IUserService
from alpaca.common.domain.user import User


@component.adapter(IPersistenceManager)
@interface.implementer(IUserService)
class UserService:

    def __init__(self, persistence_manager):
        self._persistence_manager = persistence_manager

    def create_user(self, user):
        self._persistence_manager.session.add(user)
        return user

    def update_user(self, user):
        self._persistence_manager.session.add(user)
        return user

    def delete_user(self, user):
        self._persistence_manager.session.delete(user)

    def get_user(self, id):
        try:
            return self._persistence_manager.session.query(
                User
            ).filter(
                User.id == id
            ).one()
        except db_exc.NoResultFound:
            return None

    def get_user_by_email(self, email):
        try:
            return self._persistence_manager.session.query(
                User
            ).filter(
                User.email == email
            ).one()
        except db_exc.NoResultFound:
            return None

    def get_all_users(self):
        return self._persistence_manager.session.query(
            User
        ).order_by(
            User.email
        )

    def set_user_permissions(self, permissions_dict):
        for id, permissions in permissions_dict.items():
            self._persistence_manager.session.query(
                User
            ).filter(
                User.id == id
            ).update({
                getattr(User, name): value
                for name, value in permissions.items()
            })
