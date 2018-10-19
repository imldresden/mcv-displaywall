'''
uses pyOSC package
and adapted from code
- from nifty / anton.augsburg (https://git.imld.de/imlprojects/niftytransfer/blob/master/src/net/py_osc_server.py)
- from pyOSC example (https://gitorious.org/pyosc/devel/source/633c0112318a3519314aa798a552a092566c73c1:examples/knect-rcv.py#L14-15)
'''
import types

from OSC import OSCServer, OSCError
from libavg import avg

from logging_base.body_tracking.skeleton import OSCJointTrackingState, SkeletonJoint


class KinectReceiver(avg.Publisher):
    """Class to process OSC messages from the kinect tracking system.
    Subscribers will receive messages for each joint or kill,
    containing either [skeleton_id, skeleton_joint] or [skeleton_id, 'kill')
    """

    OSC_kinect_MessageID = avg.Publisher.genMessageID()
    OSC_kinect_hand_MessageID = avg.Publisher.genMessageID()

    def __init__(self, ip):
        """Initialize the server on localhost."""

        avg.Publisher.__init__(self)

        self.__active_skeleton_ids = []

        try:
            self.__server = OSCServer((ip, 27015))
            self.__server.print_tracebacks = True
            # TODO check the ThreadingOSCServer class as possible alternative
        except OSCError:
            print "############################################"
            print "####### could not open OSCServer ###########"
            print "############################################"
            return

        if self.__server is None:
            print "OSC KINECT RECEIVER: server is not initialized"
            return

        print "Kinect receiver: ", self.__server

        self.__server.handle_timeout = types.MethodType(
            self.__handle_timeout, self.__server
        )
        self.__server.timeout = 0
        self.__server.addMsgHandler(
            "/joint", self.__on_osc_joint_message_received
        )
        self.__server.addMsgHandler(
            "/hand", self.__on_osc_hand_message_received
        )
        self.__server.addMsgHandler(
            "/kill", self.__on_osc_kill_message_received
        )

        self.publish(self.OSC_kinect_MessageID)
        self.publish(self.OSC_kinect_hand_MessageID)

    def __handle_timeout(self, statusnachricht):
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

    def __on_osc_joint_message_received(self, addr, tags, data, client_address):
        """Receives an OSC message, transforms the data and
        notifies subscribers by sending a message (type: list) containing skeleton_id and
        skeleton_joint (type: SkeletonJoint)

        Args:
            addr: the address (str e.g. /joint)
            tags: tags (str with i for int32 and f for float, e.g. iiiifff)
            data: tracking data, containing
                    id, convertMode, jointtype, trackingstate, and if trackingstate != OKTS_NOTTRACKED, x,y and z
            client_address: client address as (ip, port) tuple
        """

        # check if length could actually be a skeleton joint message
        if len(data) < 4:
            return

        # initialize position values
        x = 0
        y = 0
        z = 0

        # only if joint is tracked, additional position values are given
        if data[3] is not OSCJointTrackingState.OKTS_NOTTRACKED and len(data) >= 7:
            x = data[4]
            y = data[5]
            z = data[6]

        # create the skeleton joint from received data
        # joint_type = OSCKinectJoint(data[2])
        joint_type = data[2]
        skeleton_joint = SkeletonJoint(x, y, z, joint_type)
        skeleton_joint.tracking_state = data[3]

        # add skeletonID to active skeleton list
        if data[0] not in self.__active_skeleton_ids:
            self.__active_skeleton_ids.append(data[0])

        # message for subscribers consists of skeletonID and joint
        message = [data[0], skeleton_joint]

        # send new skeleton_joint to subscriber

        self.notifySubscribers(self.OSC_kinect_MessageID, [message])

    def __on_osc_hand_message_received(self, addr, tags, data, client_address):
        """
            received hand state events from oscserver and if this skeleton already exists
            it norfies subscribers with message skeleton_id and list["left"/"right", value]
        """
        if len(data) < 3:
            return

        if data[1] != "left" and data[1] != "right":
            return

        if data[0] in self.__active_skeleton_ids:
            message = [data[0], (data[1], data[2])]
            self.notifySubscribers(self.OSC_kinect_hand_MessageID, [message])

    def __on_osc_kill_message_received(self, addr, tags, data, client_address):
        """
        receives the kill event from oscserver and
        reacts by sending out a message (list) ONCE that includes skeleton_id and 'kill'
        """

        # kill will be received constantly, only send message once
        # when skeletonID is still in active skeleton list
        if data[0] in self.__active_skeleton_ids:
            # message for subscribers consists of skeletonID and 'kill'
            message = [data[0], 'kill']
            # send message

            self.notifySubscribers(self.OSC_kinect_MessageID, [message])
            # remove skeletonID from active skeleton list
            self.__active_skeleton_ids.remove(data[0])
        pass
