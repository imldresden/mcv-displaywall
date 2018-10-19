import threading

from tornado.web import RequestHandler
from tornado.websocket import WebSocketHandler


class BaseRequestHandler(RequestHandler):
    def __init__(self, application, request, **kwargs):
        self._web_path = None

        super(BaseRequestHandler, self).__init__(application, request, **kwargs)

    def initialize(self, web_path):
        """
        :type web_path: str
        """
        self._web_path = web_path

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "content-type")
        self.set_header("Access-Control-Allow-Methods", "POST, GET")

    def options(self, *args, **kwargs):
        # TODO: Is this correct?
        self.set_status(204)
        self.finish()


class BaseWebSocketHandler(WebSocketHandler):
    def __init__(self, application, request, **kwargs):
        self._connection_id = None
        self._controller = None

        super(BaseWebSocketHandler, self).__init__(application, request, **kwargs)

    def initialize(self, controller):
        """
        :type controller: DivicoControl
        """
        super(BaseWebSocketHandler, self).initialize()
        self._controller = controller

    @property
    def ws_id(self):
        """
        :rtype: int
        """
        return self._connection_id

    def check_origin(self, origin):
        return True

    def _send_msg(self, send_method):
        """
        Sends a message. It will check if the thread is the server thread. If not it will call this method in this thread.

        :param send_method: The send method.
        :type send_method: callable
        """
        assert callable(send_method), "{} is not callable".format(send_method)

        if threading.current_thread().getName() == self._controller.tornado_server.thread_name:
            send_method()
        else:
            self._controller.tornado_server.call_from_thread(send_method)
