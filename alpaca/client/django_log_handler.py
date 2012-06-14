"""
Stanard Python `logging` handler for Django applications.
Requires Requests package (http://python-requests.org)

Required settings:
    ALPACA_ENABLED
    ALPACA_URL
    ALPACA_REPORTER
    ALPACA_API_KEY
    ALPACA_CA_BUNDLE
"""

import re
import sys
import hmac
import pprint
import hashlib
import datetime
import logging
import threading
import traceback
import requests
from django.conf import settings
from django.utils import simplejson
from django.views.debug import SafeExceptionReporterFilter

logger = logging.getLogger('alpaca')

class ForcedSafeExceptionReporterFilter(SafeExceptionReporterFilter):

    def is_active(self, request):
        return True

    def get_traceback_frame_variables(self, *args, **kwargs):
        variables = super(ForcedSafeExceptionReporterFilter, self)\
                        .get_traceback_frame_variables(*args, **kwargs)
        return [
            (
                key,
                (
                    value
                    if not key.lower().startswith('password')
                        and not key.lower().startswith('passwd')
                    else
                    '*****'
                )
            ) for key, value in variables
        ]

exception_reporter_filter = ForcedSafeExceptionReporterFilter()

def send_alpaca_report(url, reporter, api_key, message, ca_bundle=None):
    try:
        signature = hmac.new(
            api_key,
            message,
            hashlib.sha256
        ).hexdigest()
        if ca_bundle is None:
            # You can pass `verify` the path to a CA_BUNDLE file for private
            # certs or just True to perform normal, browser-like verification.
            ca_bundle = True
        response = requests.post(
            '/'.join((url.rstrip('/'), 'api/report')),
            data=message,
            headers = {
                'Content-Type': 'application/json',
                'X-Alpaca-Reporter': reporter,
                'X-Alpaca-Signature': signature,
            },
            timeout=5,
            verify=ca_bundle
        )
        if response.status_code != 200:
            raise RuntimeError("Alpaca responded with HTTP %d: %s" % (
                response.status_code,
                response.content.strip()
            ))
    except:
        logger.error("Error while sending report to Alpaca: %s"
                     % '\n'.join(traceback.format_exception_only(
                        *sys.exc_info()[:2]
                     )).strip())

def async_send_alpaca_report(url, reporter, api_key, message, ca_bundle=None):
    threading.Thread(target=send_alpaca_report, args=(
        url,
        reporter,
        api_key,
        message,
        ca_bundle
    )).start()

def alpaca_report(message, exc_info=None, request=None):
    try:
        if not settings.ALPACA_ENABLED:
            return
        if exc_info is None:
            exc_info = sys.exc_info()
        if exc_info != (None, None, None):
            exception_message = (
                ''.join(traceback.format_exception_only(*exc_info[:2])).strip()
            )
            stack_trace = _serialize_stack(exc_info[2])
            lowest_frame = stack_trace[-1]
            error_hash = hashlib.md5(
                ':'.join((
                    lowest_frame['filename'],
                    lowest_frame['function'],
                    lowest_frame['context']
                ))
            ).hexdigest()
        else:
            exception_message = message
            stack_trace = []
            error_hash = hashlib.md5(
                message
            ).hexdigest()
        message = dict(
            error_hash=error_hash,
            message=exception_message,
            stack_trace=stack_trace,
            date=datetime.datetime.utcnow().isoformat(),
            uri=None,
            get_data=dict(),
            post_data=dict(),
            cookies=dict(),
            headers=dict(),
        )
        if request is not None:
            message.update(dict(
                uri=request.build_absolute_uri(),
                get_data=request.GET.dict(),
                post_data= \
                    exception_reporter_filter.get_post_parameters(request),
                cookies=request.COOKIES,
                headers=_serialize_object_dict(request.META.iteritems()),
            ))
        async_send_alpaca_report(
            settings.ALPACA_URL,
            settings.ALPACA_REPORTER,
            settings.ALPACA_API_KEY,
            simplejson.dumps(message),
            ca_bundle=settings.ALPACA_CA_BUNDLE,
        )
    except Exception:
        logger.error("Error while sending report to Alpaca: %s"
                     % '\n'.join(traceback.format_exception_only(
                        *sys.exc_info()[:2]
                     )).strip())

class AlpacaLogHandler(logging.Handler):
    def emit(self, record):
        try:
            if hasattr(record, 'request'):
                request = record.request
            else:
                request = None
            if hasattr(record, 'exc_info'):
                exc_info = record.exc_info
            else:
                exc_info = None
            try:
                message = record.msg % record.args
            except:
                message = '[formatting_error] ' + record.msg
            alpaca_report(message, exc_info, request)
        except Exception:
            logger.error("Error while sending report to Alpaca: %s"
                         % '\n'.join(traceback.format_exception_only(
                            *sys.exc_info()[:2]
                         )).strip())

def _get_lines_from_file(filename, lineno, context_lines, loader=None,
                         module_name=None):
    """
    Returns context_lines before and after lineno from file.
    Returns (pre_context_lineno, pre_context, context_line, post_context).
    """
    source = None
    if loader is not None and hasattr(loader, "get_source"):
        source = loader.get_source(module_name)
        if source is not None:
            source = source.splitlines()
    if source is None:
        try:
            with open(filename, 'rb') as fp:
                source = fp.readlines()
        except (OSError, IOError):
            pass
    if source is None:
        return None, [], None, []
    encoding = 'ascii'
    for line in source[:2]:
        # File coding may be specified. Match pattern from PEP-263
        # (http://www.python.org/dev/peps/pep-0263/)
        match = re.search(r'coding[:=]\s*([-\w.]+)', line)
        if match:
            encoding = match.group(1)
            break
    source = [unicode(sline, encoding, 'replace') for sline in source]
    lower_bound = max(0, lineno - context_lines)
    upper_bound = lineno + context_lines
    pre_context = [line.strip('\n') for line in source[lower_bound:lineno]]
    context_line = source[lineno].strip('\n')
    post_context = [line.strip('\n') for line in source[lineno+1:upper_bound]]
    return lower_bound, pre_context, context_line, post_context

def _serialize_stack(tb):
    frames = []
    while tb is not None:
        # Support for __traceback_hide__ which is used by a few libraries
        # to hide internal frames.
        if tb.tb_frame.f_locals.get('__traceback_hide__'):
            tb = tb.tb_next
            continue
        filename = tb.tb_frame.f_code.co_filename
        function = tb.tb_frame.f_code.co_name
        lineno = tb.tb_lineno - 1
        loader = tb.tb_frame.f_globals.get('__loader__')
        module_name = tb.tb_frame.f_globals.get('__name__') or ''
        pre_context_lineno, pre_context, context_line, post_context = \
            _get_lines_from_file(filename, lineno, 7, loader, module_name)
        if pre_context_lineno is not None:
            frames.append(dict(
                filename=filename,
                line_number=lineno,
                function=function,
                pre_context=pre_context,
                context=context_line,
                post_context=post_context,
                variables=_serialize_object_dict(
                    exception_reporter_filter \
                        .get_traceback_frame_variables(None, tb.tb_frame)
                )
            ))
        tb = tb.tb_next
    return frames

def _serialize_object_dict(iterable_of_twotuples):
    result = dict()
    for key, value in iterable_of_twotuples:
        try:
            formatted_value = pprint.pformat(value)
        except Exception as exception:
            formatted_value = "Formatting error: %s" % str(exception)
        result[key] = formatted_value
    return result
