# python imports
from enum import Enum

import numpy as np


# region OSC Kinect ENUM classes

class OSCKinect1ConvertMode(Enum):
    OKCM_NOCONVERT = 0
    OKCM_NOTTRACKED = 1
    OKCM_INTERPOLATED_TRACKED = 2
    OKCM_INTERPOLATED_INFERRED = 3


class OSCKinectJoint(Enum):
    OKS_NONE = -1
    OKS_SPINE_BASE = 0
    OKS_SPINE_MID = 1
    OKS_SPINE_SHOULDER = 20
    OKS_NECK = 2
    OKS_HEAD = 3
    OKS_SHOULDER_RIGHT = 8
    OKS_SHOULDER_LEFT = 4
    OKS_ELBOW_RIGHT = 9
    OKS_ELBOW_LEFT = 5
    OKS_WRIST_RIGHT = 10
    OKS_WRIST_LEFT = 6
    OKS_HAND_RIGHT = 11
    OKS_HAND_LEFT = 7
    OKS_THUMB_RIGHT = 24
    OKS_THUMB_LEFT = 22
    OKS_HAND_TIP_RIGHT = 23
    OKS_HAND_TIP_LEFT = 21
    OKS_HIP_RIGHT = 16
    OKS_HIP_LEFT = 12
    OKS_KNEE_RIGHT = 17
    OKS_KNEE_LEFT = 13
    OKS_ANKLE_RIGHT = 18
    OKS_ANKLE_LEFT = 14
    OKS_FOOT_RIGHT = 19
    OKS_FOOT_LEFT = 15


class OSCJointTrackingState(Enum):
    OKTS_UNKNOWN = -1
    OKTS_NOTTRACKED = 0
    OKTS_INFERRED = 1
    OKTS_TRACKED = 2


class OSCKinectHandState(Enum):
    OKHS_HandState_Unknown = 0
    OKHS_HandState_NotTracked = 1
    OKHS_HandState_Open = 2
    OKHS_HandState_Closed = 3
    OKHS_HandState_Lasso = 4

# endregion


class SkeletonJoint(object):
    def __init__(self, x=0, y=0, z=0, joint_type=OSCKinectJoint.OKS_NONE):
        self.__joint_type = joint_type
        self.__x = x
        self.__y = y
        self.__z = z
        self.__tracking_state = OSCJointTrackingState.OKTS_UNKNOWN

    # region Properties

    @property
    def joint_type(self):
        return self.__joint_type

    @property
    def pos_x(self):
        return self.__x

    @pos_x.setter
    def pos_x(self, x):
        self.__x = x

    @property
    def pos_y(self):
        return self.__y

    @pos_y.setter
    def pos_y(self, y):
        self.__y = y

    @property
    def pos_z(self):
        return self.__z

    @pos_z.setter
    def pos_z(self, z):
        self.__z = z

    @property
    def tracking_state(self):
        return self.__tracking_state

    @tracking_state.setter
    def tracking_state(self, tracking_state):
        self.__tracking_state = tracking_state

    # endregion

    def get_joint_type_str(self):
        return OSCKinectJoint(self.joint_type).name


class Skeleton(object):

    def __init__(self, id):
        self.__id = id
        self.__joints = {}  # dictionary
        self.__left_hand_state = OSCKinectHandState.OKHS_HandState_Unknown
        self.__right_hand_state = OSCKinectHandState.OKHS_HandState_Unknown

    # region Properties

    @property
    def id(self):
        return self.__id

    @id.setter
    def id(self, id):
        self.__id = id

    @property
    def joints(self):
        return self.__joints

    @property
    def left_hand_state(self):
        return self.__left_hand_state

    @left_hand_state.setter
    def left_hand_state(self, left_hand_state):
        self.__left_hand_state = left_hand_state

    @property
    def right_hand_state(self):
        return self.__right_hand_state

    @right_hand_state.setter
    def right_hand_state(self, right_hand_state):
        self.__right_hand_state = right_hand_state

    # endregion

    def update_joint(self, joint_type, joint):

        # # if joint already exists - update
        # if self.__joints.has_key(joint_type):
        #     self.__joints[joint_type].x = joint.x
        #     self.__joints[joint_type].y = joint.y
        #     self.__joints[joint_type].z = joint.z
        #     self.__joints[joint_type].tracking_state = joint.tracking_state
        # # else create new joint
        # else:
        self.joints[joint_type] = joint

    def update_joint_smooth(self, joint_type, joint):

        if self.__joints.has_key(joint_type):
            last_joint_data = self.__joints[joint_type]

            old_share = 0.99
            self.joints[joint_type].tracking_state = joint.tracking_state
            self.joints[joint_type].pos_x = old_share * self.__joints[joint_type].pos_x + (1-old_share) * joint.pos_x
            self.joints[joint_type].pos_y = old_share * self.__joints[joint_type].pos_y + (1-old_share) * joint.pos_y
            self.joints[joint_type].pos_z = old_share * self.__joints[joint_type].pos_z + (1-old_share) * joint.pos_z

        self.joints[joint_type] = joint
