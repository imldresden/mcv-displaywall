'''
uses pyOSC package
and adapted from code
- from nifty / anton.augsburg (https://git.imld.de/imlprojects/niftytransfer/blob/master/src/net/tracking.py)
- from pyOSC example (https://gitorious.org/pyosc/devel/source/633c0112318a3519314aa798a552a092566c73c1:examples/knect-rcv.py#L14-15)
'''

# python imports
from collections import namedtuple
from OSC import OSCServer, OSCError
# from tracking.py_osc import OSCServer, OSCError
from enum import Enum
import types
import configs.config_app as config

# libavg imports
from libavg import avg

# internal imports
from device_tracking.utils.point3d import Point3D

RigidBody = namedtuple(
    "RigidBody",
    "id name position orientation orientation_quat markers mrk_ids mrk_sizes mrk_mean_error"
)


class OptiTrackReceiver(avg.Publisher):
    OSC_optitrack_MessageID = avg.Publisher.genMessageID()
    OSC_optitrack_KillMessageID = avg.Publisher.genMessageID()

    def __init__(self, ip="", port="5103"):

        avg.Publisher.__init__(self)

        try:
            rigidbody_format = config.optitrack_osc_format
            self.__index_id = rigidbody_format.index("id")
            self.__index_x = rigidbody_format.index("x")
            self.__index_y = rigidbody_format.index("y")
            self.__index_z = rigidbody_format.index("z")
            self.__index_roll = rigidbody_format.index("roll")
            self.__index_pitch = rigidbody_format.index("pitch")
            self.__index_yaw = rigidbody_format.index("yaw")
            self.__index_name = rigidbody_format.index("name")
            self.__index_quat_1 = rigidbody_format.index("quat_1")
            self.__index_quat_2 = rigidbody_format.index("quat_2")
            self.__index_quat_3 = rigidbody_format.index("quat_3")
            self.__index_quat_4 = rigidbody_format.index("quat_4")
            self.__osc_format_length = len(rigidbody_format)
            self.__server = OSCServer((ip, int(port)))
            # TODO check the ThreadingOSCServer class as possible alternative

            print "Optitrack:", self.__server

            self.__server.handle_timeout = types.MethodType(
                self.__handle_timeout, self.__server
            )
            self.__server.timeout = 0

            self.__server.addMsgHandler(
                "/tracking/optitrack/rigidbodies", self.__on_osc_rigidbody_message_received
            )
            self.__server.addMsgHandler(
                "/kill", self.__on_osc_kill_message_received
            )

            self.publish(self.OSC_optitrack_MessageID)
            self.publish(self.OSC_optitrack_KillMessageID)
        except OSCError:
            print "############################################"
            print "####### could not open OSCServer ###########"
            print "############################################"
            return

    def __handle_timeout(self, status):
        """Handle server timeouts."""
        self.__server.timed_out = True

    def onFrame(self):
        """Stay active."""
        self.__server.timed_out = False
        # handle all pending requests than return
        while not self.__server.timed_out:
            self.__server.handle_request()

    def run(self):
        """Start running the server."""
        while True:
            self.__server.handle_request()
        self.__server.close()

    def __on_osc_rigidbody_message_received(self, addr, tags, data, client_address):
        """b
        Receives an OSC message, transforms the data and
        notifies subscribers by sending a message (type: list) containing skeleton_id and
        skeleton_joint (type: SkeletonJoint)

        Args:
            addr: the address (str e.g. /tracking/optitrack/rigidbodies)
            tags: tags (str with i for int32 and f for float, e.g. iiiifff)
            data: tracking data, containing
                    id (0), position in space (1-3), and orientation in space (4-6)
            client_address: client address as (ip, port) tuple
        """

        # check if length could actually be a rigid body message
        if len(data) < self.__osc_format_length:
            return

        data[self.__index_x] = data[self.__index_x] * 100
        data[self.__index_y] = config.display_height_cm - data[self.__index_y] * 100
        data[self.__index_z] = data[self.__index_z] * 100

        # create RigidBody tuple
        rb = RigidBody(
            id=data[self.__index_id],
            name=data[self.__index_name],
            position=Point3D(data[self.__index_x], data[self.__index_y], data[self.__index_z]),
            orientation=(data[self.__index_roll], data[self.__index_pitch], data[self.__index_yaw]),
            orientation_quat=(data[self.__index_quat_1], data[self.__index_quat_2], data[self.__index_quat_3], data[self.__index_quat_4]),
            markers=None,
            mrk_ids=None,
            mrk_sizes=None,
            mrk_mean_error=None
        )

        # send new rigidbody to subscriber
        self.notifySubscribers(self.OSC_optitrack_MessageID, [rb])

    def __on_osc_kill_message_received(self, addr, tags, data, client_address):
        """
        receives the kill event from oscserver and
        reacts ??
        """
        self.notifySubscribers(self.OSC_optitrack_KillMessageID, data)
