from zope import interface


class IPersistenceManager(interface.Interface):

    session = interface.Attribute(
        """Factory of SQLAlchemy database sessions."""
    )

    def initialize_schema():
        """Creates missing database tables."""

    def add_if_not_exists(entity, discriminator):
        """
        Persists `entity` but only if there's no entity in the database with
        same value of a column `discriminator`. The logic of this is entirely
        database-side.
        """
