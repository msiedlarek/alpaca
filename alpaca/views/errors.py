import urllib

from pyramid.view import (view_config, notfound_view_config,
    forbidden_view_config)
from pyramid.security import authenticated_userid
from pyramid import httpexceptions
from pyramid.i18n import get_localizer
from pyramid.response import Response

from alpaca.translation import translate as _

@view_config(
    context='pyramid.httpexceptions.HTTPBadRequest',
    renderer='alpaca:templates/errors/bad_request.jinja2'
)
def error_bad_request(exception, request):
    if 'X-Requested-With' in request.headers:
        return Response(str(exception) + '\r\n', status=400)
    request.response.status = 400
    return {}

@forbidden_view_config()
def error_forbidden(exception, request):
    if 'X-Requested-With' in request.headers:
        return Response(status=403)
    if authenticated_userid(request) is None:
        request.session.flash(
            get_localizer(request).translate(_(
                "You must sign in to see the requested page."
            )),
            queue='error'
        )
    else:
        request.session.flash(
            get_localizer(request).translate(_(
                "You don't have permission to see this page."
                " Try logging in as a different user."
            )),
            queue='error'
        )
    return httpexceptions.HTTPSeeOther(
        '?'.join((
            request.route_url('alpaca.users.sign_in'),
            'destination=%s' % urllib.quote_plus(request.path_qs)
        ))
    )

@notfound_view_config(
    renderer='alpaca:templates/errors/not_found.jinja2'
)
def error_not_found(exception, request):
    if 'X-Requested-With' in request.headers:
        return Response(status=404)
    request.response.status = 404
    return {}
