import logging

from alpaca.common.persistence.interfaces import IPersistenceManager


logger = logging.getLogger(__name__)


class InitializeDatabaseCommand:

    help = "create database schema"

    def configure_argument_parser(self, parser):
        pass

    def __call__(self, registry, arguments):
        persistence_manager = registry.getUtility(IPersistenceManager)
        logger.info("Initializing database schema...")
        persistence_manager.initialize_schema()
        logger.info("Done.")
