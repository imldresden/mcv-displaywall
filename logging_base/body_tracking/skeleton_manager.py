# internal import
from skeleton import Skeleton
from kinect_receiver import KinectReceiver


class SkeletonManager(object):
    """ Class to manage receiving kinect data including
    creation, update and deletion for skeletons and joints."""

    __SKELETON_LIFETIME = 30

    def __init__(self, ip="", update_interval=1):
        """ Initializes the skeleton manager by subscribing to receive kinect data."""

        self.__callbacks_skeleton_added = []  # list of functions to be called when a new skeleton appears
        self.__callbacks_skeleton_updated = []  # list of functions to be called when a skeleton moves
        self.__callbacks_skeleton_removed = []  # list of functions to be called when a skeleton disappears

        self.__skeletons = {}  # dictionary with skeleton_id and skeleton, always current value
        self.__active_skeletons = [] # list of skeleton_id that are complete (in terms of joints) and active
        self.__skeleton_changes = {} # dictionary with skeleton_id and #changes
        self.__skeleton_lifetimes = {}

        self.__update_interval = update_interval
        self.__kinect_receiver = KinectReceiver(ip)
        self.__kinect_receiver.subscribe(
            KinectReceiver.OSC_kinect_MessageID, self.__on_skeleton_changed
        )
        self.__kinect_receiver.subscribe(
            KinectReceiver.OSC_kinect_hand_MessageID, self.__on_skeleton_hand_changed
        )

    @property
    def skeletons(self):
        return self.__skeletons

    def on_frame(self):
        self.__kinect_receiver.onFrame()
        self.__lifetime_tick()

    def remove_as_known_skeleton(self, skeleton_id):
        self.__notify_remove_skeleton(skeleton_id)

    def start_listening(self, skeleton_added=None, skeleton_updated=None, skeleton_removed=None):
        callbacks = (
            (skeleton_added, self.__callbacks_skeleton_added),
            (skeleton_updated, self.__callbacks_skeleton_updated),
            (skeleton_removed, self.__callbacks_skeleton_removed)
        )

        for (func, callback) in callbacks:
            if func is not None and func not in callback:
                callback.append(func)

    def stop_listening(self, skeleton_added=None, skeleton_updated=None, skeleton_removed=None):
        callbacks = (
            (skeleton_added, self.__callbacks_skeleton_added),
            (skeleton_updated, self.__callbacks_skeleton_updated),
            (skeleton_removed, self.__callbacks_skeleton_removed)
        )

        for (function, callback) in callbacks:
            if function is not None:
                callback.remove(function)

    def __lifetime_tick(self):
        ids_to_remove = []
        for id in self.__skeleton_lifetimes:
            # print self.__skeleton_lifetimes[id]
            self.__skeleton_lifetimes[id] -= 1
            if self.__skeleton_lifetimes[id] < 0:
                ids_to_remove.append(id)
        for id in ids_to_remove:
            self.__notify_remove_skeleton(id)

    def __reset_lifetime(self, id):
        self.__skeleton_lifetimes[id] = SkeletonManager.__SKELETON_LIFETIME

    def __on_skeleton_changed(self, skeleton_message):
        """ reacts to publishers message by updating the skeletons and
        notifies listeners to create and remove objects accordingly.

        Args:
             skeleton_message (list): [0] skeleton_id (int) and [1] skeleton (Skeleton)
        """

        if len(skeleton_message) < 2:
            return

        skeleton_id = skeleton_message[0]

        if skeleton_message[1] is 'kill':
            # remove
            self.__notify_remove_skeleton(skeleton_id)
            return

        skeleton_joint = skeleton_message[1]
        # print 'joint type: ', skeleton_joint.joint_type

        # check if skeleton id is known
        # if yes - update can be done, just count another change
        if skeleton_id in self.__skeletons and skeleton_id in self.__skeleton_changes:
            self.__skeleton_changes[skeleton_id] += 1
        # if no - create skeleton so that update can be done
        else:
            self.__skeletons[skeleton_id] = Skeleton(skeleton_id)
            self.__skeleton_changes[skeleton_id] = 1

        # add or update joint
        # self.__skeletons[skeleton_id].update_joint(skeleton_joint.joint_type, skeleton_joint)
        self.__skeletons[skeleton_id].update_joint_smooth(skeleton_joint.joint_type, skeleton_joint)

        # if number of changes (joints) enough propagate to listeners: (create and) update objects
        # if skeleton_id in self.__skeleton_changes and self.__skeleton_changes[skeleton_id] > 24:
        # use update interval to react only to every Xth change of the skeleton, x = self.update_interval
        if skeleton_id in self.__skeleton_changes \
               and self.__skeleton_changes[skeleton_id] / 25.0 >= self.__update_interval:
            self.__skeleton_changes[skeleton_id] = 0
            # check if skeleton already complete and active before
            if skeleton_id not in self.__active_skeletons:
                self.__notify_create_skeleton(skeleton_id)

            # update listeners on skeleton change
            self.__notify_update_skeleton(skeleton_id)

        self.__reset_lifetime(skeleton_id)

    def __on_skeleton_hand_changed(self, skeleton_message):
        if len(skeleton_message) < 2:
            return

        skeleton_id = skeleton_message[0]

        if skeleton_id not in self.__skeletons:
            return

        hand_tuple = skeleton_message[1]
        if len(hand_tuple) < 2:
            return

        if hand_tuple[0] == "left":
            self.__skeletons[skeleton_id].left_hand_state = hand_tuple[1]
        elif hand_tuple[0] == "right":
            self.__skeletons[skeleton_id].right_hand_state = hand_tuple[1]

        # self.__notify_update_skeleton(skeleton_id)

    def __notify_create_skeleton(self, skeleton_id):
        """ calls listeners that skeleton has appeared
        """
        if skeleton_id in self.__skeletons:
            for callback in self.__callbacks_skeleton_added:
                callback(sender=self, skeleton=self.__skeletons[skeleton_id])
            self.__active_skeletons.append(skeleton_id)

    def __notify_update_skeleton(self, skeleton_id):
        """ calls listeners that skeleton has moved
        """
        if skeleton_id in self.__skeletons:
            for callback in self.__callbacks_skeleton_updated:
                callback(sender=self, skeleton=self.__skeletons[skeleton_id])

    def __notify_remove_skeleton(self, skeleton_id):
        """ calls listeners that skeleton has disappeared
        """
        if skeleton_id in self.__skeletons:
            for callback in self.__callbacks_skeleton_removed:
                callback(sender=self, skeleton=self.__skeletons[skeleton_id])

        # remove the skeleton from dictionaries
        if skeleton_id in self.__skeletons:
            del self.__skeletons[skeleton_id]
        if skeleton_id in self.__skeleton_changes:
            del self.__skeleton_changes[skeleton_id]
        if skeleton_id in self.__skeleton_lifetimes:
            del self.__skeleton_lifetimes[skeleton_id]
