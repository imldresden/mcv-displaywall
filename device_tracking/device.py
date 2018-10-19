import glm
from abc import ABCMeta

from libavg import avg, player
import time
from enum import Enum
from one_euro_filter import OneEuroFilter
import configs.config_app as config_app
from logging_base.study_logging import StudyLog
from tornado_server.helper.ip_mapper import IpMapper


class PositionMapping(Enum):
    Orthogonal = 0
    Interpolation = 1
    Perspective = 2
    Perspective_Weighted = 3


class SmoothingTyp(Enum):
    Quaternion = 0,
    Pixel = 1


class Device(object):
    __metaclass__ = ABCMeta

    weighted_front_dist_cm = 50  # Without orientation
    weighted_back_dist_cm = 180  # Without orientation

    def __init__(self, device_id=None, websocket_id=""):
        self.__id = device_id
        self.__websocket_id = websocket_id
        self.__device_name = config_app.mobile_devices[IpMapper.get_ip_from_id(websocket_id)]
        self.__pixel_per_cm = config_app.pixel_per_cm
        self.__canvas = None
        self.__pos_space = None
        self.__pos_screen = None
        self.__orientation = None
        self.__orientation_quat = None
        self.__mapping = PositionMapping(config_app.pointing_mode)
        self.__smoothing = SmoothingTyp.Pixel
        self.__is_frozen = False
        self.__cursor_down = False

        self.__callbacks_device_moved = []
        self.__callbacks_device_touched = []
        self.__callbacks_update_content = []

        # ToDo remove, when config exists to know which rigidbody_id has which device dimensions
        self.__size = avg.Point2D(1920, 1200)

        self.__one_euro_filter_pitch = OneEuroFilter(freq=60, mincutoff=0.575, beta=0.85, dcutoff=1.0)
        self.__one_euro_filter_roll = OneEuroFilter(freq=60, mincutoff=0.575, beta=0.85, dcutoff=1.0)

        self.__one_euro_filter_quat_1 = OneEuroFilter(freq=60, mincutoff=0.575, beta=2, dcutoff=1.0)
        self.__one_euro_filter_quat_2 = OneEuroFilter(freq=60, mincutoff=0.575, beta=2, dcutoff=1.0)
        self.__one_euro_filter_quat_3 = OneEuroFilter(freq=60, mincutoff=0.575, beta=2, dcutoff=1.0)
        self.__one_euro_filter_quat_4 = OneEuroFilter(freq=60, mincutoff=0.575, beta=2, dcutoff=1.0)

        self.__one_euro_filter_screen_x_inter = OneEuroFilter(freq=60, mincutoff=0.575, beta=0.85, dcutoff=1.0)
        self.__one_euro_filter_screen_y_inter = OneEuroFilter(freq=60, mincutoff=0.575, beta=0.85, dcutoff=1.0)

    def update_from_position(self, pos_space):
        self.__pos_space = pos_space
        self.__update_position()

    def update_position_relative(self, rel_x, rel_y, ignore_frozen=True):
        if not ignore_frozen and self.__is_frozen:
            return

        self.__pos_screen = (
            self.pos_screen_x + rel_x,
            self.pos_screen_y + rel_y
        )
        # self.__update_position()
        for callback in self.__callbacks_device_moved:
            callback(sender=self, pos_space=self.__pos_space, pos_screen=self.__pos_screen)

    def update_from_rigidbody(self, rigidbody, ignore_frozen=False):
        self.__pos_space = rigidbody.position
        self.__orientation = rigidbody.orientation
        self.__orientation_quat = rigidbody.orientation_quat

        if not ignore_frozen and self.__is_frozen:
            return
        self.__update_position()

    def __update_position(self):
        if self.__mapping is PositionMapping.Orthogonal:
            self.__pos_screen = (
                float(self.__pos_space.pos_x) * self.__pixel_per_cm,
                float(self.__pos_space.pos_y) * self.__pixel_per_cm
            )

            # temp. calculation for surface in wall labor needed!
            # self.__pos_screen = (self.__pos_space.pos_x,self.__pos_space.pos_y)

        elif self.__mapping is PositionMapping.Interpolation:
            # pitch influences y value; yaw influences x value

            # dx = tan(self.pitch) * self.pos_space_z * -1  # *-1 because x direction is negative
            # pitch left wall corner: 0.8; right wall corner: -0.8
            pitch = self.__one_euro_filter_pitch(self.pitch, time.time())
            dx = self.map_value(pitch, config_app.pitch_min_max)

            # dy = tan(self.roll) * self.pos_space_z
            # top of wall: roll = -0.7; bottom of wall: 0.7
            roll = self.__one_euro_filter_roll(self.roll, time.time())
            dy = self.map_value(roll, config_app.roll_min_max)

            self.__pos_screen = (
                float(self.__pos_space.pos_x) * self.__pixel_per_cm + dx,
                float(self.__pos_space.pos_y) * self.__pixel_per_cm + dy
            )
        elif self.__mapping in [PositionMapping.Perspective, PositionMapping.Perspective_Weighted]:
            # Get all necessary values.
            position = glm.vec3(
                self.pos_space_x,
                # Invert the space y coordinate because it was inverted in the optitrack_receiver before.
                config_app.display_height_cm - self.pos_space_y,
                self.pos_space_z
            )
            if self.__smoothing is SmoothingTyp.Quaternion:
                vec_orientation = glm.quat(
                    self.__one_euro_filter_quat_1(self.__orientation_quat[0], time.time()),
                    self.__one_euro_filter_quat_2(self.__orientation_quat[1], time.time()),
                    self.__one_euro_filter_quat_3(self.__orientation_quat[2], time.time()),
                    self.__one_euro_filter_quat_4(self.__orientation_quat[3], time.time())
                )
            else:
                vec_orientation = glm.quat(
                    self.__orientation_quat[0],
                    self.__orientation_quat[1],
                    self.__orientation_quat[2],
                    self.__orientation_quat[3]
                )

            if self.__mapping is PositionMapping.Perspective_Weighted:
                vec_orientation_unit = glm.quat(-1, 0, 0, 0)

                weight = (position.z - self.weighted_front_dist_cm) / (self.weighted_back_dist_cm - self.weighted_front_dist_cm)
                weight = max(min(weight, 1), 0)
                vec_orientation = glm.quat.slerp(vec_orientation_unit, vec_orientation, weight)

            # -1 for the z coordinate to prevent that the device "stands" behind the wall.
            vec_rotation = vec_orientation * glm.vec3(0, 0, -position.z)

            # Calculate a factor for the rotation.
            if vec_rotation.z != 0:
                # -1 for the z coordinate to prevent that the device "stands" behind the wall.
                factor = -position.z / vec_rotation.z
            else:
                factor = -1
            # Calculate the new pointing position.
            if factor <= 0:
                pos_pointed = position * -1
            else:
                pos_pointed = position + (vec_rotation * factor)

            # Convert the cm to pixels.
            pos_pointed *= self.__pixel_per_cm
            # Invert the y position to match it with the wall coordinate system
            pos_pointed.y = config_app.app_resolution[1] - pos_pointed.y

            if self.__smoothing is SmoothingTyp.Pixel:
                # Interpolate the pixels.
                pos_pointed_inter = (
                    (pos_pointed.x / config_app.app_resolution[0]),
                    (pos_pointed.y / (config_app.app_resolution[1]))
                )
                pos_pointed_inter = (
                    max(min(pos_pointed_inter[0], 1), 0),
                    max(min(pos_pointed_inter[1], 1), 0)
                )
                # Use the filter on the interpolation.
                pos_pointed_inter = (
                    self.__one_euro_filter_screen_x_inter(pos_pointed_inter[0], time.time()),
                    self.__one_euro_filter_screen_y_inter(pos_pointed_inter[1], time.time())
                )
                # Calculate it back.
                pos_pointed = glm.vec3(
                    config_app.app_resolution[0] * pos_pointed_inter[0],
                    config_app.app_resolution[1] * pos_pointed_inter[1],
                    0
                )

            # Clamp the pointer position to the resolution of the application.
            # b1 = glm.vec3(0, config_app.app_resolution[1] / 12, 0)
            b1 = glm.vec3(0, 0, 0)
            b2 = glm.vec3(config_app.app_resolution[0], config_app.app_resolution[1] * 11.0/12.0, 0)
            if (pos_pointed.x < b1.x or pos_pointed.x > b2.x or
                    pos_pointed.y < b1.y or pos_pointed.y > b2.y):
                pos_pointed.x = max(pos_pointed.x, b1.x)
                pos_pointed.x = min(pos_pointed.x, b2.x)
                pos_pointed.y = max(pos_pointed.y, b1.y)
                pos_pointed.y = min(pos_pointed.y, b2.y)

            self.__pos_screen = pos_pointed.x, pos_pointed.y

        for callback in self.__callbacks_device_moved:
            callback(sender=self, pos_space=self.__pos_space, pos_screen=self.__pos_screen)

        if config_app.study_mode:
            StudyLog.get_instance().write_device(self)

    def start_listening(self, device_moved=None, update_content=None, device_touched=None):
        if device_moved is not None and device_moved not in self.__callbacks_device_moved:
            self.__callbacks_device_moved.append(device_moved)
        if update_content is not None and update_content not in self.__callbacks_update_content:
            self.__callbacks_update_content.append(update_content)
        if device_touched is not None and device_touched not in self.__callbacks_device_touched:
            self.__callbacks_device_touched.append(device_touched)

    def stop_listening(self, device_moved=None, update_content=None, device_touched=None):
        if device_moved is not None:
            self.__callbacks_device_moved.remove(device_moved)
        if update_content is not None:
            self.__callbacks_update_content.remove(update_content)
        if device_touched is not None:
            self.__callbacks_device_touched.remove(device_touched)

    def require_content_update(self):
        for callback in self.__callbacks_update_content:
            callback(sender=self)

    # region Properties

    @property
    def websocket_id(self):
        return self.__websocket_id

    @property
    def rui_proxy_name(self):
        return self.__device_name

    @property
    def id(self):
        return self.__id

    @id.setter
    def id(self, device_id):
        self.__id = device_id

    @property
    def pos_screen(self):
        return self.__pos_screen

    @property
    def pos_screen_x(self):
        if self.__pos_screen is None:
            return None
        return self.__pos_screen[0]

    @property
    def pos_screen_y(self):
        if self.__pos_screen is None:
            return None
        return self.__pos_screen[1]

    @property
    def pos_space(self):
        return self.__pos_space

    @property
    def pos_space_x(self):
        if self.__pos_space is None:
            return None
        return self.__pos_space.pos_x

    @property
    def pos_space_y(self):
        if self.__pos_space is None:
            return None
        return self.__pos_space.pos_y

    @property
    def pos_space_z(self):
        if self.__pos_space is None:
            return None
        return self.__pos_space.pos_z

    @property
    def rotation(self):
        return self.yaw, self.pitch, self.roll

    @property
    def roll(self):
        return self.__orientation[0]

    @property
    def pitch(self):
        return self.__orientation[1]

    @property
    def yaw(self):
        return self.__orientation[2]

    @property
    def position_mapping(self):
        return self.__mapping

    @position_mapping.setter
    def position_mapping(self, mapping):
        self.__mapping = mapping

    @property
    def is_frozen(self):
        return self.__is_frozen

    @is_frozen.setter
    def is_frozen(self, freeze):
        self.__is_frozen = freeze

    @property
    def size(self):
        return self.__size

    @size.setter
    def size(self, size):
        self.__size = size

    @property
    def canvas(self):
        return self.__canvas

    @canvas.setter
    def canvas(self, canvas):
        self.__canvas = canvas

    # endregion

    @staticmethod
    def map_value(value, from_low, from_high, to_low, to_high):
        old_range = (from_high - from_low)
        new_range = (to_high - to_low)
        new_value = float(((value - from_low) * new_range) / old_range) + to_low
        return new_value
