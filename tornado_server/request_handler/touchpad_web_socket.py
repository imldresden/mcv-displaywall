import json

from libavg import player

from events.event_dispatcher import EventDispatcher
from tornado_server.helper.ip_mapper import IpMapper
from tornado_server.request_handler.base_handlers import BaseWebSocketHandler


class ConnectionWebSocket(BaseWebSocketHandler, EventDispatcher):
    """
    WebSocket for the communication with the touchPad on the clients website.
    """
    __WEB_SOCKET_OPENED = "webSocketOpened"
    __WEB_SOCKET_CLOSED = "webSocketClosed"

    def __init__(self, application, request, **kwargs):
        self.__app_size = None

        super(ConnectionWebSocket, self).__init__(application, request, **kwargs)

    def initialize(self, controller, on_web_socket_opened=None, on_web_socket_closed=None):
        """
        :type controller: WebClientController
        :param on_web_socket_opened: Called when a new websocket has opened.
        :type on_web_socket_opened: function(sender:DataWebSocketHandler)
        :param on_web_socket_closed: Called when this open websocket has closed.
        :type on_web_socket_closed: function(sender:DataWebSocketHandler)
        """
        super(ConnectionWebSocket, self).initialize(controller=controller)
        EventDispatcher.__init__(self)

        if not IpMapper.is_ip_already_known(self.request.remote_ip):
            self._connection_id = IpMapper.get_id_from_ip(self.request.remote_ip)

        self.bind(self.__WEB_SOCKET_OPENED, on_web_socket_opened)
        self.bind(self.__WEB_SOCKET_CLOSED, on_web_socket_closed)

    def open(self):
        self.dispatch(self.__WEB_SOCKET_OPENED, sender=self)

    def on_close(self):
        if self._connection_id is not None:
            IpMapper.remove_ip_id(self.request.remote_ip)

        self.dispatch(self.__WEB_SOCKET_CLOSED, sender=self)
        self._unbind_all()

    # -------------------------------- Common WebSocket Events --------------------------------
    def on_message(self, message):
        data = json.loads(message)

        if IpMapper.get_id_from_ip(self.request.remote_ip) != self._connection_id:
            return

        # Decide which request should be used.
        if data["messageType"] == "TouchPadData-Request":
            self._on_msg_touchpad_created()
        elif data["messageType"] == "TouchUpdate":
            self._on_msg_touchupdate(data["data"])

    def _on_msg_touchupdate(self, data):
        """
        Called when a device has registered a touchup or touchdown event
        """
        def dispatch():
            self._controller.on_device_touchpad_event(
                connection_id=self._connection_id,
                update_type=data["updateType"]
            )
        player.callFromThread(dispatch)

    def _on_msg_touchpad_created(self):
        """
        Called when a device has registerd a new websocket
        """
        def dispatch():
            self._controller.on_device_touchpad_created(
                connection_id=self._connection_id,
            )
        player.callFromThread(dispatch)
