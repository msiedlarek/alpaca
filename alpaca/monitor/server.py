import logging

import zmq
from zmq.eventloop.ioloop import IOLoop
from zmq.eventloop.zmqstream import ZMQStream


logger = logging.getLogger(__name__)


class Server:

    _encoding = 'utf-8'

    def __init__(self, application, settings):
        self.host = settings.get('host', '*')
        self.port = int(settings.get('port', 8195))
        self.application = application

        self._context = zmq.Context()
        self._context.set(
            zmq.MAX_SOCKETS,
            int(settings.get('alpaca.connection_limit', 10000))
        )

        queued_message_limit = int(
            settings.get('alpaca.queued_message_limit', 1000)
        )
        self._socket = self._context.socket(zmq.SUB)
        self._socket.subscribe = bytes()
        self._socket.rcvhwm = queued_message_limit * 2  # 2-part messages

        self._io_loop = IOLoop()

        self._zmq_stream = ZMQStream(self._socket, io_loop=self._io_loop)
        self._zmq_stream.on_recv(self.application)

    def serve(self):
        self._socket.bind(
            'tcp://{host}:{port}'.format(host=self.host, port=self.port)
        )
        logger.info("Listening on {host}:{port}...".format(
            host=self.host,
            port=self.port
        ))
        self._io_loop.start()
