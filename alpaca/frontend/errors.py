import sys
import logging
import traceback
import random
import urllib

from pyramid import httpexceptions

from alpaca.frontend.i18n import translate as _


logger = logging.getLogger(__name__)

alpaca_facts = (
    (
        "Alpacas were domesticated by the Incas more than 6,000 years ago."
    ),
    (
        "Alpaca fiber is flame-resistant, meeting the Class 1 standard of "
        "the U.S. Consumer Product Safety Commission."
    ),
    (
        "Alpaca fiber comes in 16 tones that are recognized by the textile "
        "industry."
    ),
    (
        "Alpacas and llamas can successfully cross-breed."
    ),
    (
        "Because of their predisposition for using a dung pile, some alpacas "
        "have been successfully house-trained."
    ),
    (
        "Alpacas can live for up to 20 years."
    ),
    (
        "Alpacas are intelligent and easy to train. They quickly learn to "
        " accept a halter, be led, and load in and out of a vehicle."
    ),
    (
        "Alpacas have three compartment stomachs."
    ),
    (
        "Average alpaca eats 2-3 bales of grass hay per month."
    ),
    (
        "Alpacas will occasionally spit at each other when they are competing "
        " for food."
    ),
    (
        "Alpacas only have bottom teeth."
    ),
)


def not_found(exception, request):
    request.response.status = 404
    return {
        'alpaca_fact': random.choice(alpaca_facts),
    }


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
    return {
        'alpaca_fact': random.choice(alpaca_facts),
    }
