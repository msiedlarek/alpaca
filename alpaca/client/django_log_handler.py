import sys
import httplib
import hashlib
import datetime
import logging
import threading
import traceback
from django.conf import settings
from django.utils import simplejson

logger = logging.getLogger('motointegrator.contrib.alpaca')

def send_alpaca_report(host, port, api_key, message):
    try:
        connection = httplib.HTTPConnection(host, port, timeout=5)
        connection.putrequest('POST', '/report/%s' % api_key)
        connection.putheader('Content-length', len(message))
        connection.putheader('Content-type', 'application/json')
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

def async_send_alpaca_report(host, port, api_key, message):
    threading.Thread(target=send_alpaca_report, args=(
        host,
        port,
        api_key,
        message,
    )).start()

def alpaca_report(exc_info, request=None):
    try:
        lowest_frame = traceback.extract_tb(exc_info[2])[-1]
        hash_ = hashlib.md5(
            ':'.join((lowest_frame[0], lowest_frame[2], lowest_frame[3]))
        ).hexdigest()
        traceback_ = '\n'.join(traceback.format_exception(*exc_info))
        message = dict(
            hash=hash_,
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
