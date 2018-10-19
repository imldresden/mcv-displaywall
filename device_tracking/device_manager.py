from optitrack_receiver import OptiTrackReceiver
from device import Device
from libavg import avg
import configs.config_app as config_app

from tornado_server.helper.ip_mapper import IpMapper


class DeviceManager(avg.Publisher):
    DEVICE_ADDED = avg.Publisher.genMessageID()
    DEVICE_UPDATED = avg.Publisher.genMessageID()
    DEVICE_REMOVED = avg.Publisher.genMessageID()

    def __init__(self, ip, port=5103):
        # list of all known rigid body ids
        self.__rb_known_ids = {}

        avg.Publisher.__init__(self)

        self.publish(self.DEVICE_ADDED)
        self.publish(self.DEVICE_UPDATED)
        self.publish(self.DEVICE_REMOVED)

        # optitrack setup
        self.__optitrack_receiver = OptiTrackReceiver(ip=ip, port=port)
        self.__optitrack_receiver.subscribe(
            OptiTrackReceiver.OSC_optitrack_MessageID,
            self.on_rigidbody_changed
        )

        self.__devices = {}  # dictionary with device_id and device
        self.__devices_websockets = {}  # dict with websocket_id and device_id

        self.__event_id = 0  # event id for the touch injection

    @property
    def devices(self):
        return self.__devices

    @devices.setter
    def devices(self, devices):
        self.__devices = devices

    def on_pair_webclient(self, websocketId):
        self.__on_web_connection_request(websocketId)

    def __on_web_connection_request(self, websocketId):
        # retrieve list of rigid body ids as candidates for pairing
        rb_candidates = []
        for rb in self.__rb_known_ids.itervalues():
            id_is_paired = rb.id in self.__devices
            if not id_is_paired:
                rb_candidates.append(rb)

        if len(rb_candidates) == 0:
            return

        self.__device_ip = IpMapper.get_ip_from_id(websocketId)
        for rb in rb_candidates:
            if self.__device_ip not in config_app.mobile_devices:
                continue

            if rb.name == config_app.mobile_devices[self.__device_ip]:
                self.__create_device(websocket_id=websocketId, rb_id=rb.id)

    def __create_device(self, websocket_id, rb_id):
        device = Device(
            device_id=rb_id,
            websocket_id=websocket_id
        )
        self.devices[device.id] = device
        self.__devices_websockets[websocket_id] = device.id
        self.notifySubscribers(self.DEVICE_ADDED, [device])
        print "{!s}: Paired webclient (websocketId={!s}) to rigid body (id={!s})".format(
            type(self).__name__, websocket_id, rb_id
        )

    def on_rigidbody_changed(self, rigidbody):
        id_is_known = rigidbody.id in self.__rb_known_ids
        id_is_paired = id_is_known and rigidbody.id in self.__devices

        if id_is_paired:
            # todo think about reduction of updates by, e.g., checking if changes are large enough
            self.devices[rigidbody.id].update_from_rigidbody(rigidbody)
            self.notifySubscribers(self.DEVICE_UPDATED, [self.devices[rigidbody.id]])
            return

        if not id_is_known:
            self.__rb_known_ids[rigidbody.id] = rigidbody
            print "{!s}: Added new rigid body id (id={!s}) to queue (now {!s}).".format(
                type(self).__name__, rigidbody.id, self.__rb_known_ids.keys()
            )

    def get_device_from_connection_id(self, connection_id):
        if connection_id not in self.__devices_websockets:
            return None

        device_id = self.__devices_websockets[connection_id]
        if device_id not in self.__devices:
            return

        return self.devices[device_id]

    def on_frame(self):
        """
        Needs to be called every frame of the program.
        """
        self.__optitrack_receiver.onFrame()