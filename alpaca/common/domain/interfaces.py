from zope import interface


class IModelBase(interface.Interface):

    id = interface.Attribute(
        """Unique ID."""
    )


class IUser(IModelBase):

    email = interface.Attribute(
        """E-mail address."""
    )
    password_processor = interface.Attribute(
        """Name of password processor used to hash the password."""
    )
    password_hash = interface.Attribute(
        """Password hashed using bcrypt algorithm."""
    )
    is_administrator = interface.Attribute(
        """True if user has administrator privileges."""
    )

    def set_password(new_password, processor_name, processor):
        """
        Sets user password to `new_password` using given password `processor`
        registered in component registry as `processor_name`.
        """

    def password_equals(alleged_password, registry):
        """
        Checks if user password equals `alleged_password` using password
        processors registered in `registry`.
        """


class IEnvironment(IModelBase):

    name = interface.Attribute(
        """Unique name."""
    )


class IProblem(IModelBase):

    hash = interface.Attribute(
        """
        Hash of important problem attributes differing one problem from
        another.
        """
    )
    description = interface.Attribute(
        """Human-readable description of a problem."""
    )
    first_occurrence = interface.Attribute(
        """Date of the first known problem occurrence."""
    )
    last_occurrence = interface.Attribute(
        """Date of the last known problem occurrence."""
    )
    occurrence_count = interface.Attribute(
        """Number of known problem occurrences."""
    )
    tags = interface.Attribute(
        """List of user-provided tags."""
    )


class IOccurrence(IModelBase):

    problem = interface.Attribute(
        """The problem (`IProblem`) this occurrence refers to."""
    )
    environment = interface.Attribute(
        """The environment (`IEnvironment`) this occurrence occurred in."""
    )
    date = interface.Attribute(
        """Date (`datetime`) of the occurrence."""
    )
    message = interface.Attribute(
        """Occurrence-specific problem message."""
    )
    stack_trace = interface.Attribute(
        """Serialized list of stack trace frames."""
    )
    environment_data = interface.Attribute(
        """Dictionary of serialized environment variables and various data."""
    )
