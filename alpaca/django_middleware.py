import httplib
import datetime
import logging
import threading
import traceback
from django.conf import settings
from django.utils import simplejson

logger = logging.getLogger('motointegrator.contrib.alpaca')

def send_alpaca_report(host, port, api_key, message):
    try:
        connection = httplib.HTTPConnection(host, port, timeout=10)
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

def alpaca_report(exception, request=None):
    try:
        message = dict(
            traceback=traceback.format_exc(exception).strip(),
            date=datetime.datetime.now().isoformat(),
            path=None,
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
                path=request.path,
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

class AlpacaMiddleware(object):

    def process_exception(self, request, exception):
        alpaca_report(exception, request)
