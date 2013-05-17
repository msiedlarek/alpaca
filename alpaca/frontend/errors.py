import sys
import logging
import traceback
import urllib

from pyramid import httpexceptions

from alpaca.frontend.i18n import translate as _


logger = logging.getLogger(__name__)


def not_found(exception, request):
    request.response.status = 404
    return {}


def forbidden(exception, request):
    if request.user is None:
        request.session.flash(
            _("You must sign in to see the requested page."),
            queue='warning'
        )
    else:
        request.session.flash(
            _(
                "You don't have permission to access the requested page. You"
                " may try signing in as a different user."
            ),
            queue='warning'
        )
    return httpexceptions.HTTPSeeOther(
        '?'.join((
            request.route_url('alpaca.frontend.accounts.sign_in'),
            'destination={}'.format(urllib.parse.quote_plus(request.path_qs)),
        ))
    )


def internal_server_error(exception, request):
    message = traceback.format_exception_only(
        type(exception),
        exception
    )[-1].strip()
    exception_information = sys.exc_info()
    if exception_information:
        exception_traceback = sys.exc_info()[2]
        if exception_traceback:
            exception_stack = traceback.extract_tb(exception_traceback)
            if exception_stack:
                file, line, function, code = exception_stack[-1]
                message = (
                    "{exception} in {function}() at {file}:{line}".format(
                        exception=message,
                        function=function,
                        file=file,
                        line=line
                    )
                )
    logger.error(message)
    if exception_information:
        logger.debug(
            ''.join(traceback.format_exception(*exception_information))
        )
    request.response.status = 500
    return {}
