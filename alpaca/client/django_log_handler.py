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

logger = logging.getLogger(__name__)

class ForcedSafeExceptionReporterFilter(SafeExceptionReporterFilter):
    def is_active(self, request):
        return True
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

def alpaca_report(exc_info=None, request=None):
    try:
        if not settings.ALPACA_ENABLED:
            return
        if exc_info is None:
            exc_info = sys.exc_info()
        stack_trace = _serialize_stack(exc_info[2])
        lowest_frame = stack_trace[-1]
        error_hash = hashlib.md5(
            ':'.join((
                lowest_frame['filename'],
                lowest_frame['function'],
                lowest_frame['context']
            ))
        ).hexdigest()
        exception_message = \
            ''.join(traceback.format_exception_only(*exc_info[:2])).strip()
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
            cookies = dict((
                (str(k), pprint.pformat(v))
                for k, v
                in request.COOKIES.iteritems()
            ))
            meta = dict((
                (str(k), pprint.pformat(v))
                for k, v
                in request.META.iteritems()
            ))
            message.update(dict(
                uri=request.build_absolute_uri(),
                get_data=request.GET.dict(),
                post_data= \
                    exception_reporter_filter.get_post_parameters(request),
                cookies=cookies,
                headers=meta,
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
            request = record.request
        except AttributeError:
            request = None
        try:
            alpaca_report(record.exc_info, request)
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
                variables=dict((
                    (str(k), pprint.pformat(v))
                    for k, v
                    in exception_reporter_filter\
                       .get_traceback_frame_variables(None, tb.tb_frame)
                ))
            ))
        tb = tb.tb_next
    return frames
