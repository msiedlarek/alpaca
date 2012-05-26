import sys
import httplib
import hmac
import hashlib
import datetime
import logging
import threading
import traceback
from django.conf import settings
from django.utils import simplejson

logger = logging.getLogger(__name__)

def send_alpaca_report(host, port, reporter, api_key, message):
    try:
        signature = hmac.new(
            api_key,
            message,
            hashlib.sha256
        ).hexdigest()
        connection = httplib.HTTPConnection(host, port, timeout=5)
        connection.putrequest('POST', '/api/report')
        connection.putheader('Content-length', len(message))
        connection.putheader('Content-type', 'application/json')
        connection.putheader('X-Alpaca-Reporter', reporter)
        connection.putheader('X-Alpaca-Signature', signature)
        connection.endheaders()
        connection.send(message)
        response = connection.getresponse()
        connection.close()
        if response.status != httplib.OK:
            raise RuntimeError("Alpaca responded with HTTP %d %s" % (
                response.status,
                response.reason,
            ))
    except Exception as exception:
        logger.error("Error while sending report to Alpaca: %s"
                     % str(exception))

def async_send_alpaca_report(host, port, reporter, api_key, message):
    threading.Thread(target=send_alpaca_report, args=(
        host,
        port,
        reporter,
        api_key,
        message,
    )).start()

def alpaca_report(exc_info=None, request=None):
    try:
        if not settings.ALPACA_ENABLED:
            return
        if exc_info is None:
            exc_info = sys.exc_info
        lowest_frame = traceback.extract_tb(exc_info[2])[-1]
        error_hash = hashlib.md5(
            ':'.join((lowest_frame[0], lowest_frame[2], lowest_frame[3]))
        ).hexdigest()
        traceback_ = '\n'.join(traceback.format_exception(*exc_info)).strip()
        message = dict(
            error_hash=error_hash,
            traceback=traceback_,
            date=datetime.datetime.now().isoformat(),
            uri=None,
            get_data=None,
            post_data=None,
            cookies=None,
            headers=None,
        )
        if request is not None:
            meta = request.META
            for key, value in meta.iteritems():
                try:
                    meta[key] = str(value)
                except ValueError:
                    continue
            message.update(dict(
                uri=request.build_absolute_uri(),
                get_data=request.GET.dict(),
                post_data=request.POST.dict(),
                cookies=request.COOKIES,
                headers=meta,
            ))
        async_send_alpaca_report(
            settings.ALPACA_HOST,
            settings.ALPACA_PORT,
            settings.ALPACA_REPORTER,
            settings.ALPACA_API_KEY,
            simplejson.dumps(message),
        )
    except Exception as exception:
        logger.error("Error while sending report to Alpaca: %s"
                     % str(exception))

class AlpacaLogHandler(logging.Handler):

    def emit(self, record):
        try:
            request = record.request
        except AttributeError:
            request = None
        try:
            alpaca_report(record.exc_info, request)
        except Exception as exception:
            logger.error("Error while sending report to Alpaca: %s"
                         % str(exception))
