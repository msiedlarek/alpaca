from zope import interface


class IRandomGenerator(interface.Interface):
    """Random string generator."""

    def __call__(length):
        """Returns random, alpha-numeric string of given `length`."""


class IPasswordProcessor(interface.Interface):
    """
    Utility providing password hashing and verification facility using
    particular algorithm.
    """

    def get_password_hash(password):
        """
        Returns the implementation-specific ASCII string hash for given
        `password` string, up to 100 characters long.
        """

    def verify_password(correct_password_hash, alleged_password):
        """
        Returns True if `alleged_password` is valid for given
        `correct_password_hash`. Constant time of comparsion is guaranteed to
        prevent timing attacks.
        """


class ILayout(interface.Interface):
    """Alpaca views layout."""
