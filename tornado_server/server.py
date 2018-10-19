import os
import threading

from libavg import player
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.web import Application, StaticFileHandler

from configs import config_app
from events.event_dispatcher import EventDispatcher
from tornado_server.request_handler.index_handler import IndexHandler
from tornado_server.request_handler.static_handlers import JsStaticFileHandler, CssStaticFileHandler
from tornado_server.request_handler.touchpad_web_socket import ConnectionWebSocket


class TornadoServer(threading.Thread, EventDispatcher):
    __CONNECTION_OPENED = "connectionOpened"
    __CONNECTION_CLOSED = "connectionClosed"

    __current_server_instance = None

    def __init__(self, divico_controller):
        """
        :type divico_controller: DivicoControl
        """
        self.__thread_name = "TornadoServer-Thread"

        super(TornadoServer, self).__init__()
        EventDispatcher.__init__(self)
        self.setName(self.__thread_name)
        self.setDaemon(True)

        self.__started = False

        self.__controller = divico_controller

        self.__data_web_sockets = []
        self.__data_web_sockets_id_counter = 0

        # Get the right paths to the files.
        working_directory = os.getcwd()
        if "tornado_server" not in working_directory:
            working_directory += "/tornado_server"
        web_path = "{}/{}".format(working_directory, "web")

        self.__touchpad_webSocket_parameters = {
            "controller": self.__controller,
            "on_web_socket_opened": self.__on_data_web_socket_opened,
            "on_web_socket_closed": self.__on_data_web_socket_closed,
        }

        self.__handlers = [
            (r"/js/(.*)", JsStaticFileHandler, dict(path="{}/{}".format(working_directory, "web/js"))),
            (r"/css/(.*)", CssStaticFileHandler, dict(path="{}/{}".format(working_directory, "web/css"))),
            (r"/assets/(.*)", StaticFileHandler, dict(path="{}/{}".format(working_directory, "web/assets"))),
            (r"/", IndexHandler, dict(web_path=web_path)),
            (r"/ws/touch_pad", ConnectionWebSocket, self.__touchpad_webSocket_parameters),
        ]
        self.__settings = {
            "debug": True,
            "autoreload": False,
        }

        self.__tornado_web_app = Application(self.__handlers, **self.__settings)
        self.__http_server = HTTPServer(self.__tornado_web_app)
        self.__io_loop = None

    @property
    def thread_name(self):
        """
        :rtype: str
        """
        return self.__thread_name

    def run(self):
        """
        Starts the server represented through this object.
        """
        if self.__started:
            return

        self.__http_server.listen(config_app.server_port)
        self.__io_loop = IOLoop.current()
        self.__io_loop.start()

    def dispatch(self, event_name, **kwargs):
        """
        Allows that this dispatch will be in the main thread rather than in the sever thread.
        """
        # Create a "worker" for the libavg thread.
        def inner_dispatch():
            super(TornadoServer, self).dispatch(event_name, **kwargs)

        player.callFromThread(inner_dispatch)

    def call_from_thread(self, method, *args, **kwargs):
        """
        Calls a method from the thread of this server.
        """
        assert callable(method), "{} is not callable".format(method)
        self.__io_loop.add_callback(method, *args, **kwargs)

    def __on_data_web_socket_opened(self, sender):
        """
        :type sender: ViewWebSocket
        """
        if sender in self.__data_web_sockets:
            return

        self.__data_web_sockets.append(sender)

        self.dispatch(self.__CONNECTION_OPENED, sender=self, connection_id=sender.ws_id)

    def __on_data_web_socket_closed(self, sender):
        """
        :type sender: ViewWebSocket
        """
        if sender not in self.__data_web_sockets:
            return

        self.__data_web_sockets.remove(sender)

        self.dispatch(self.__CONNECTION_CLOSED, sender=self, connection_id=sender.ws_id)

    def start_listening(self, connection_opened=None, connection_closed=None):
        """
        Registers a callback to listen to changes to this server. Listeners can register to any number of the provided
        events. For the required structure of the callbacks see below.

        :param connection_opened: Called when a new connection on the device website view (through a websocket) has opened.
        :type connection_opened: function(sender:TornadoServer, connection_id:int)
        :param connection_closed: Called when an open connection on the device website view has closed.
        :type connection_closed: function(sender:TornadoServer, connection_id:int)
        """
        self.bind(self.__CONNECTION_OPENED, connection_opened)
        self.bind(self.__CONNECTION_CLOSED, connection_closed)

    def stop_listening(self, connection_opened=None, connection_closed=None):
        """
        Stops listening to an event the listener has registered to previously. The provided callback needs to be the
        same that was used to listen to the event in the fist place.

        :param connection_opened: Called when a new connection on the device website view (through a websocket) has opened.
        :type connection_opened: function(sender:TornadoServer, connection_id:int)
        :param connection_closed: Called when an open connection on the device website view has closed.
        :type connection_closed: function(sender:TornadoServer, connection_id:int)
        """
        self.unbind(self.__CONNECTION_OPENED, connection_opened)
        self.unbind(self.__CONNECTION_CLOSED, connection_closed)
