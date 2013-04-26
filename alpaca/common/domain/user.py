from zope import interface
import sqlalchemy as sql

from alpaca.common.domain.interfaces import IUser
from alpaca.common.domain.model_base import ModelBase
from alpaca.common.utilities.interfaces import IPasswordProcessor


@interface.implementer(IUser)
class User(ModelBase):

    __tablename__ = 'alpaca_users'

    email = sql.Column(
        sql.String(length=200),
        index=True,
        unique=True,
        nullable=False
    )
    password_processor = sql.Column(
        sql.String(length=50),
        nullable=False
    )
    password_hash = sql.Column(
        sql.String(length=100),
        nullable=False
    )
    is_administrator = sql.Column(
        sql.Boolean(),
        nullable=False,
        default=False
    )

    def set_password(self, new_password, processor_name, processor):
        self.password_processor = processor_name
        self.password_hash = processor.get_password_hash(new_password)

    def password_equals(self, alleged_password, registry):
        password_processor = registry.getUtility(
            IPasswordProcessor,
            self.password_processor
        )
        return password_processor.verify_password(
            self.password_hash,
            alleged_password
        )
