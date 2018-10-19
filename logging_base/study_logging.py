import logging, os
from libavg import player

from configs import config_app
from configs.config_app import kinect_data_ip
from configs.config_study import LoggingDefaults
from logging_base.body_tracking.skeleton_manager import SkeletonManager
from logging_base.body_tracking.skeleton import OSCKinectJoint


class LogFileHandlerWithHeader(logging.FileHandler):

    def __init__(self, filename, header,  mode='a', encoding=None, delay=0):
        self.__header = header
        # check if the file exists to decide if adding header is needed
        self.__file_pre_exists = os.path.exists(filename)
        if not self.__file_pre_exists:
            folder_path = filename[:filename.rindex('/')]
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)

        super(LogFileHandlerWithHeader, self).__init__(filename, mode, encoding)

        # Write the header if file stream was created and file did not exist yet.
        if not self.__file_pre_exists and self.stream is not None:
            self.stream.write('%s\n' % header)

    def emit(self, record):
        if self.stream is None:
            self.stream = self._open()

            # write header if does not exist yet
            if not self.__file_pre_exists:
                self.stream.write('%s\n' % self.__header)

        super(LogFileHandlerWithHeader, self).emit(record)


class BodyTrackingLog(object):
    """
        writes the following messages to logging_base:
            (removed) on device added:
                    'added, <skeleton_id>'
            on device moved:
                    '<skeleton_id>, <joint_type1>, <x1>, <y1>, <z1>, <tracking_state1>,
                    ..., <joint_typeN>, <xN>, <yN>, <zN>, <tracking_stateN>
            (removed) on device removed:
                   'removed, <skeleton_id>'
    """

    def __init__(self, name, all_joints=True, speed_in_ms=None):
        self.__body_tracking_log = logging.getLogger(name)

        if all_joints:
            self.__joint_types = {
                OSCKinectJoint.OKS_SPINE_BASE : 0,
                OSCKinectJoint.OKS_SPINE_MID : 1,
                OSCKinectJoint.OKS_SPINE_SHOULDER : 20,
                OSCKinectJoint.OKS_NECK : 2,
                OSCKinectJoint.OKS_HEAD : 3,
                OSCKinectJoint.OKS_SHOULDER_RIGHT : 8,
                OSCKinectJoint.OKS_SHOULDER_LEFT : 4,
                OSCKinectJoint.OKS_ELBOW_RIGHT : 9,
                OSCKinectJoint.OKS_ELBOW_LEFT : 5,
                OSCKinectJoint.OKS_WRIST_RIGHT : 10,
                OSCKinectJoint.OKS_WRIST_LEFT : 6,
                OSCKinectJoint.OKS_HAND_RIGHT : 11,
                OSCKinectJoint.OKS_HAND_LEFT : 7,
                OSCKinectJoint.OKS_THUMB_RIGHT : 24,
                OSCKinectJoint.OKS_THUMB_LEFT : 22,
                OSCKinectJoint.OKS_HAND_TIP_RIGHT : 23,
                OSCKinectJoint.OKS_HAND_TIP_LEFT : 21,
                OSCKinectJoint.OKS_HIP_RIGHT : 16,
                OSCKinectJoint.OKS_HIP_LEFT : 12,
                OSCKinectJoint.OKS_KNEE_RIGHT : 17,
                OSCKinectJoint.OKS_KNEE_LEFT : 13,
                OSCKinectJoint.OKS_ANKLE_RIGHT : 18,
                OSCKinectJoint.OKS_ANKLE_LEFT : 14,
                OSCKinectJoint.OKS_FOOT_RIGHT : 19,
                OSCKinectJoint.OKS_FOOT_LEFT : 15
            }
        # else:
        #     self.__joint_types = [
        #         OSCKinectJoint.OKS_HEAD,
        #         OSCKinectJoint.OKS_SPINE_MID,
        #         OSCKinectJoint.OKS_HAND_LEFT,
        #         OSCKinectJoint.OKS_HAND_RIGHT,
        #         OSCKinectJoint.OKS_ELBOW_RIGHT,
        #         OSCKinectJoint.OKS_ELBOW_LEFT
        #     ]

        # handling of body tracking
        self.__skeleton_manager = SkeletonManager(kinect_data_ip)
        if speed_in_ms is None:
            self.__skeleton_manager.start_listening(
                skeleton_added=self.__log_skeleton_added,
                skeleton_updated=self.__log_skeleton_moved,
                skeleton_removed=self.__log_skeleton_removed
            )
        else:
            player.setInterval(speed_in_ms, self.__log_on_time)

    def get_header_str(self):
        header = "%s, %s" % ('day, time', 'skeleton_id')
        for joint_type in self.__joint_types.iterkeys():
            joint_type_str = OSCKinectJoint(joint_type).name
            # ToDo map to meters in coordinate space of display wall
            header += ", %s, %s, %s, %s" % \
                      (joint_type_str + '_x',
                       joint_type_str + '_y',
                       joint_type_str + '_z',
                       joint_type_str + '_tracking-state')
        return header

    def __log_on_time(self):
        for skeleton_id, skeleton in self.__skeleton_manager.skeletons.iteritems():
            self.__log_skeleton_position(skeleton)

    def __log_skeleton_added(self, sender, skeleton):
        # msg = '%s, %i' % ("added", skeleton.id)
        # self.__body_tracking_log.info(msg)
        self.__log_skeleton_position(skeleton)

    def __log_skeleton_moved(self, sender, skeleton):
        # possibly not on every frame, but only at timeout?
        self.__log_skeleton_position(skeleton)

    def __log_skeleton_removed(self, sender, skeleton):
        self.__log_skeleton_position(skeleton)
        # msg = '%s, %i' % ("removed", skeleton.id)
        # self.__body_tracking_log.info(msg)

    def __log_skeleton_position(self, skeleton):
        msg = '%s' % skeleton.id
        for j_type in self.__joint_types.itervalues():
            j = skeleton.joints[j_type]
            pos_x, pos_y, pos_z = self.position_to_meter(j.pos_x, j.pos_y, j.pos_z)
            msg += ', %f, %f, %f, %s' % (pos_x, pos_y, pos_z, j.tracking_state)
        self.__body_tracking_log.log(logging.INFO, msg)

    @staticmethod
    def position_to_meter(pos_x, pos_y, pos_z):
        # ToDo check min/max of kinect values and map
        return pos_x, pos_y, pos_z

    def on_frame(self):
        self.__skeleton_manager.on_frame()


class StudyLog(object):
    __instance = None

    @staticmethod
    def get_instance():
        if StudyLog.__instance is None:
            StudyLog.__instance = StudyLog()
        return StudyLog.__instance

    def __init__(self):
        session_id = config_app.SESSION

        # init loggers: GENERAL EVENTS
        self.__general_event_log = logging.getLogger('general')
        self.__general_event_log.setLevel(logging.INFO)

        # init loggers: BODY TRACKING
        name_body_tracking = 'body_tracking'
        self.__body_tracking_log = logging.getLogger(name_body_tracking)
        self.__body_tracking = BodyTrackingLog(
            name_body_tracking, speed_in_ms=LoggingDefaults.LOG_SPEED_SKELETON_TRACKING
        )
        self.__body_tracking_log.setLevel(logging.INFO)

        # init loggers: DEVICE POSITION
        self.__devices = {}
        self.__device_position_log = logging.getLogger('device_position')
        self.__device_position_log.setLevel(logging.INFO)

        # init loggers: DEVICE CANVAS TOUCH EVENT
        self.__devices_canvas_event_log = logging.getLogger('device_event')
        self.__devices_canvas_event_log.setLevel(logging.INFO)

        # init loggers: TOUCH
        self.__touch_log = logging.getLogger('touch')
        self.__touch_log.setLevel(logging.INFO)

        # init loggers: TOUCH INJECTION
        self.__touch_injection_log = logging.getLogger('touch_injection')
        self.__touch_injection_log.setLevel(logging.INFO)

        # init format
        csv_formatter = logging.Formatter("%(asctime)s.%(msecs)d, %(message)s", "%Y-%m-%d, %H:%M:%S")

        # add general event logging to console
        console = logging.StreamHandler()
        self.__general_event_log.addHandler(console)

        if not config_app.study_mode:
            return

        # init files and # connect logger and file and formatter
        task_file = LogFileHandlerWithHeader(
            filename=str('study_logs/session_' + str(session_id) + '_task.csv'),
            header='%s, %s, %s' % ('day, time', 'event_name', 'arguments')
        )
        task_file.setFormatter(csv_formatter)
        self.__general_event_log.addHandler(task_file)

        body_tracking_file = LogFileHandlerWithHeader(
            filename='study_logs/session_' + str(session_id) + '_body_tracking.csv',
            header=self.__body_tracking.get_header_str()
        )
        body_tracking_file.setFormatter(csv_formatter)
        self.__body_tracking_log.addHandler(body_tracking_file)

        device_position_file = LogFileHandlerWithHeader(
            filename='study_logs/session_' + str(session_id) + '_device_position.csv',
            header='%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s' %
                   ('day, time', 'device_id', 'rui-proxy_name',
                    'screen_pos_x_in_px', 'screen_pos_y_in_px',
                    'space_pos_x_in_m', 'space_pos_y_in_m', 'space_pos_z_in_m',
                    'yaw_in_rad', 'pitch_in_rad', 'roll_in_rad')
        )
        device_position_file.setFormatter(csv_formatter)
        self.__device_position_log.addHandler(device_position_file)

        touch_file = LogFileHandlerWithHeader(
            filename='study_logs/session_' + str(session_id) + '_touch.csv',
            header='%s, %s, %s, %s, %s' %
                   ('day, time', 'pos_x_in_px', 'pos_y_in_px', 'user_id_str', 'event_type_str')
        )
        touch_file.setFormatter(csv_formatter)
        self.__touch_log.addHandler(touch_file)

        touch_injection_file = LogFileHandlerWithHeader(
            filename='study_logs/session_' + str(session_id) + '_touch_injection.csv',
            header='%s, %s, %s, %s, %s' %
                   ('day, time', 'pos_x_in_px', 'pos_y_in_px', 'user_id_str', 'event_type_str')
        )
        touch_injection_file.setFormatter(csv_formatter)
        self.__touch_injection_log.addHandler(touch_injection_file)

        device_event_file = LogFileHandlerWithHeader(
            filename=str('study_logs/session_' + str(session_id) + '_device_event.csv'),
            header=', '.join(['day, time', 'device_id', 'rui-proxy_name',
                              'event_type', 'canvas_pos_x_in_px', 'canvas_pos_y_in_px',
                              'cursor_id'])
        )
        device_event_file.setFormatter(csv_formatter)
        self.__devices_canvas_event_log.addHandler(device_event_file)

        # handle logging speed if set in config
        if LoggingDefaults.LOG_SPEED_DEVICE_POSITION is not None:
            player.setInterval(LoggingDefaults.LOG_SPEED_DEVICE_POSITION,self.__write_device_on_timeout)

    def on_frame(self):
        self.__body_tracking.on_frame()

    def write_event_log(self, message_str):
        self.__general_event_log.info(message_str)

    def __write_device(self, d):
        self.__device_position_log.info(
            '%i, %s, %f, %f, %f, %f, %f, %f, %f, %f' %
            (d.id, d.rui_proxy_name,
             d.pos_screen_x, d.pos_screen_y,
             d.pos_space_x/100.0, d.pos_space_y/100.0, d.pos_space_z/100.0,
             d.rotation[0], d.rotation[1], d.rotation[2])
        )

    def __write_device_on_timeout(self):
        if len(self.__devices) > 0:
            for device in self.__devices.values():
                self.__write_device(device)

    def write_device(self, d):
        if LoggingDefaults.LOG_SPEED_DEVICE_POSITION is None:
            self.__write_device(d)
        else:
            # remember devices to logging on timeout
            self.__devices[d.id] = d

    def write_device_canvas_touch(self, d, event_type, event):
        msg = '%i, %s, %s, %f, %f, %i' % (d.id, d.rui_proxy_name, event_type, event.pos[0], event.pos[1], event.cursorid)
        self.__devices_canvas_event_log.info(msg)

    def write_device_canvas_event(self, d, event_type):
        msg = '%i, %s, %s, , , ' % (d.id, d.rui_proxy_name, event_type)
        self.__devices_canvas_event_log.info(msg)

    def write_touch(self, pos_x, pos_y, user_id="-1", event_type="-1", to_injection=False):
        if user_id is None:
            user_id = "-1"

        msg = '%d, %d, %s, %s' % (pos_x, pos_y, user_id, event_type)
        if not to_injection:
            self.__touch_log.info(msg)
        else:
            self.__touch_injection_log.info(msg)
