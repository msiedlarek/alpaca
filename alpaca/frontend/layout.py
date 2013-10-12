from zope import interface
import pyramid.security
import deform

from alpaca import __version__ as version
from alpaca.common.services.interfaces import IEnvironmentService
from alpaca.frontend.i18n import translate as _
from alpaca.frontend.interfaces import ILayout
from alpaca.frontend.accounts import SignOutSchema


@interface.implementer(ILayout)
class Layout:

    alpaca_version = version

    _stylesheets = (
        ('screen', 'bootstrap/css/bootstrap.min.css'),
        ('screen', 'select2/select2.min.css'),
        ('screen', 'alpaca/stylesheets/base.css'),
    )

    _scripts = (
        'alpaca/scripts/jquery-1.9.1.min.js',
        'bootstrap/js/bootstrap.min.js',
        'select2/select2.min.js',
        'timeago/jquery.timeago.js',
    )

    def __init__(self, context, request):
        self.current_environment_id = None

        self.stylesheets = [
            (
                media_query,
                request.static_path('alpaca.frontend:assets/' + asset_path)
            )
            for media_query, asset_path in self._stylesheets
        ]
        self.scripts = [
            request.static_path('alpaca.frontend:assets/' + asset_path)
            for asset_path in self._scripts
        ]
        self.favicon_path = request.static_path(
            'alpaca.frontend:assets/alpaca/images/favicon.ico'
        )
        self.dashboard_path = request.route_path(
            'alpaca.frontend.monitoring.dashboard'
        )

        self.messages = []
        for queue in ('error', 'warning', 'success', 'info',):
            for message in request.session.pop_flash(queue=queue):
                self.messages.append({
                    'queue': queue,
                    'content': message,
                })

        can_access_configuration = pyramid.security.has_permission(
            'alpaca.frontend.configuration.access',
            request.context,
            request
        )
        if can_access_configuration:
            self.configuration_path = request.route_path(
                'alpaca.frontend.configuration.configuration'
            )
        else:
            self.configuration_path = None

        can_access_account_settings = pyramid.security.has_permission(
            'alpaca.frontend.accounts.access_settings',
            request.context,
            request
        )
        if can_access_account_settings:
            self.account_settings_path = request.route_path(
                'alpaca.frontend.accounts.settings'
            )
        else:
            self.account_settings_path = None

        can_sign_out = pyramid.security.has_permission(
            'alpaca.frontend.accounts.sign_out',
            request.context,
            request
        )
        if can_sign_out:
            self.sign_out_form = deform.Form(
                SignOutSchema().bind(
                    session=request.session
                ),
                buttons=(
                    deform.Button(
                        name='submit-sign-out',
                        title=_("Sign out"),
                        css_class='btn-small btn-inverse'
                    ),
                ),
                action=request.route_path('alpaca.frontend.accounts.sign_out'),
                bootstrap_form_style='form-inline'
            ).render()
        else:
            self.sign_out_form = None

        can_access_monitoring = pyramid.security.has_permission(
            'alpaca.frontend.monitoring.access',
            request.context,
            request
        )
        if can_access_monitoring:
            self.environments = self._get_environments(request)
        else:
            self.environments = None

    def _get_environments(self, request):
        environment_service = request.registry.getAdapter(
            request.persistence_manager,
            IEnvironmentService
        )
        return [
            {
                'id': environment.id,
                'name': environment.name,
                'path': request.route_path(
                    'alpaca.frontend.monitoring.environment',
                    environment_name=environment.name
                ),
            }
            for environment in environment_service.get_all_environments()
        ]
