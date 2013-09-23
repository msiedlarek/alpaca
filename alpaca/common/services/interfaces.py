from zope import interface


class IEnvironmentService(interface.Interface):
    """Service providing environment handling logic."""

    def create_environment(environment):
        """Persists given `environment` object and returns it."""

    def delete_environment(environment):
        """Deletes given environment from the database."""

    def get_environment(id):
        """Returns environment of given `id` or None if not found."""

    def get_environment_by_name(name):
        """Returns environment of given `name` or None if not found."""

    def get_all_environments():
        """Returns iterable of all environments, sorted by name."""

    def get_affected_environments(problem):
        """
        Returns all environments affected by given problem, sorted by name.
        """


class IProblemService(interface.Interface):
    """Service providing problem handling logic."""

    def create_or_update_problem(problem):
        """
        Persists given `problem` if no other problem of same `hash` exists in
        the database, updates description, last occurrence date and increments
        occurrence counter either way.
        """

    def update_problem(user):
        """Persists given problem and returns it."""

    def get_problem(id):
        """Returns problem of given `id` or None if not found."""

    def get_occurrence(id):
        """Returns occurrence of given `id` or None if not found."""

    def get_problem_by_hash(hash):
        """Returns problem of given `hash` or None if not found."""

    def create_occurrence_of_problem(occurrence, problem_hash):
        """
        Persists given `occurrence` and creats relation with a problem of given
        `problem_hash`. Returns `occurrence`.
        """

    def get_environment_problems(environment, limit=None):
        """
        Returns a tuple of all the problems that occurred in given
        `environment` and dates of last occurrence in that environment.
        Optionally `limit` the number of results.
        """

    def get_problem_occurrence_ids(problem):
        """
        Returns iterable of all occurrences of given problem, but only with id
        field, sorted descendingly by the occurrence time. Optionally `limit`
        the number of results.
        """

    def limit_problem_history(problem_hash, limit):
        """Delete problem occurrences leaving only last `limit` of them."""

    def set_problem_tags(problem, tags):
        """Sets problem tags."""


class IUserService(interface.Interface):
    """Service providing user handling logic."""

    def create_user(user):
        """Persists given user and returns it."""

    def update_user(user):
        """Persists given user and returns it."""

    def delete_user(user):
        """Deletes given user from the database."""

    def get_user(id):
        """Returns user with given `id` or None if not found."""

    def get_user_by_email(email):
        """Returns user with given `email` or None if not found."""

    def get_all_users():
        """Returns iterable of all users sorted by email."""

    def set_user_permissions(self, permissions_dict):
        """
        Bulk-sets user permissions basing on `permissions_dict` mapping of:
            {
                user_id: {
                    permission_name: permission_value,
                    ...
                },
                ...
            }
        """
