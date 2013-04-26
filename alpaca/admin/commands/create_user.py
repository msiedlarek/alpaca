import logging
import getpass

import transaction

from alpaca.common.utilities.interfaces import IPasswordProcessor
from alpaca.common.persistence.interfaces import IPersistenceManager
from alpaca.common.domain.user import User
from alpaca.common.services.interfaces import IUserService


logger = logging.getLogger(__name__)


class CreateUserCommand:

    help = "create new user"

    _default_password_length = 10

    def configure_argument_parser(self, parser):
        parser.add_argument(
            'email',
            help="e-mail address of new user"
        )
        parser.add_argument(
            '--administrator', '-a',
            action='store_true',
            help="give new user administrator role"
        )

    def __call__(self, registry, arguments):
        password_processor_name = (
            registry.settings['alpaca.password_processor']
        )
        password_processor = registry.getUtility(
            IPasswordProcessor,
            password_processor_name
        )
        persistence_manager = registry.getUtility(IPersistenceManager)
        user_service = registry.getAdapter(
            persistence_manager,
            IUserService
        )
        if '@' not in arguments.email or len(arguments.email) < 3:
            logger.error("Invalid e-mail address.")
            return 1
        if user_service.get_user_by_email(arguments.email) is not None:
            logger.error("There is already a user with this email.")
            return 1
        logger.info("Creating user...")
        user = User(
            email=arguments.email,
            is_administrator=arguments.administrator
        )
        password = getpass.getpass("New password: ")
        password2 = getpass.getpass("Repeat password: ")
        if not password:
            logger.error("Password cannot be empty.")
            return 1
        if password != password2:
            logger.error("Passwords don't match.")
            return 1
        user.set_password(
            password,
            password_processor_name,
            password_processor
        )
        with transaction.manager:
            user_service.create_user(user)
        logger.info("User successfuly created.")
