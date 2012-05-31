"""
Stanard python `logging` handler for Django applications.
Requires Requests package (http://python-requests.org)
"""

import sys
import hmac
import hashlib
import datetime
import logging
import threading
import traceback
import requests
from django.conf import settings
from django.utils import simplejson

logger = logging.getLogger(__name__)

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
    except Exception as exception:
        logger.error("Error while sending report to Alpaca: %s"
                     % str(exception))

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
        lowest_frame = traceback.extract_tb(exc_info[2])[-1]
        error_hash = hashlib.md5(
            ':'.join((lowest_frame[0], lowest_frame[2], lowest_frame[3]))
        ).hexdigest()
        traceback_ = '\n'.join(traceback.format_exception(*exc_info)).strip()
        message = dict(
            error_hash=error_hash,
            traceback=traceback_,
            date=datetime.datetime.utcnow().isoformat(),
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
            settings.ALPACA_URL,
            settings.ALPACA_REPORTER,
            settings.ALPACA_API_KEY,
            simplejson.dumps(message),
            ca_bundle=settings.ALPACA_CA_BUNDLE,
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
