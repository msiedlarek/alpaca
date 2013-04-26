from zope import interface


class ILayout(interface.Interface):
    """Alpaca views layout."""

    stylesheets = interface.Attribute(
        """
        Iterrable of two-tuples (media, url) representing CSS stylesheets to
        include in the layout. `media` must be a valid media query (as defined
        in http://dev.w3.org/csswg/css3-mediaqueries/) determining when to
        apply given stylesheet (e.g. 'screen' or 'print').
        """
    )

    scripts = interface.Attribute(
        """
        Iterable of JavaScript script URLs to include in the layout.
        """
    )

    alpaca_version = interface.Attribute(
        """
        Currently running Alpaca version string as described by Semantic
        Versioning 2.0.0 specification (http://semver.org/).
        """
    )

    dashboard_path = interface.Attribute(
        """Path to the main dashboard."""
    )

    configuration_path = interface.Attribute(
        """Path to the configuration view or None if not allowed."""
    )

    account_settings_path = interface.Attribute(
        """Path to the account settings view or None if not allowed."""
    )

    favicon_path = interface.Attribute(
        """Path to the favicon."""
    )

    messages = interface.Attribute(
        """
        Iterable of two-key dictionaries representing flash messages. Each
        element has key `queue` (error, warning, success, info) and `content`.
        """
    )

    user = interface.Attribute(
        """Currently signed-in user or None."""
    )

    environments = interface.Attribute(
        """
        List of dictionaries (`id`, `name` and `path`) of available
        environments, or None if not authorized.
        """
    )

    current_environment_id = interface.Attribute(
        """
        ID of currently browsed environment, for navigation highlighting.
        """
    )
