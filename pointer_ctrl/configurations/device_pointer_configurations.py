from configs.config_recognizer import PointerCanvasRecognizerDefaults
from libavg_charts.configurations.text_label_configuration import TextLabelConfiguration
from pointer_ctrl.utils.default_values import PointerModeDefaults


class DevicePointerConfigurations(object):
    def __init__(self, pointer_mode=PointerModeDefaults.POINTER_MODE, pointer_div_node_class=PointerModeDefaults.POINTER_DIV_NODE_CLASS,
                 device_canvas_color=PointerModeDefaults.DEVICE_CANVAS_COLOR, device_canvas_text=PointerModeDefaults.DEVICE_CANVAS_TEXT,
                 text_configuration=PointerModeDefaults.TEXT_CONFIGURATION, swipe_direction_tolerance=PointerCanvasRecognizerDefaults.SWIPE_DIRECTION_TOLERANCE,
                 hold_delay=PointerCanvasRecognizerDefaults.HOLD_DELAY, tap_max_time=PointerCanvasRecognizerDefaults.TAP_MAX_TIME,
                 double_tap_hold_max_time=PointerCanvasRecognizerDefaults.DOUBLE_TAP_HOLD_MAX_TIME, swipe_max_time=PointerCanvasRecognizerDefaults.SWIPE_MAX_TIME,
                 hold_max_dist=PointerCanvasRecognizerDefaults.HOLD_MAX_DIST, tap_max_dist=PointerCanvasRecognizerDefaults.TAP_MAX_DIST,
                 min_drag_dist=PointerCanvasRecognizerDefaults.DRAG_MIN_DIST, swipe_min_dist=PointerCanvasRecognizerDefaults.SWIPE_MIN_DIST):
        """
        :param pointer_mode: The mode for this pointer mode.
        :type pointer_mode: PointerModes
        :param pointer_div_node_class: A class of a div node that should be used for this pointer configuration.
        :type pointer_div_node_class: avg.DivNode
        :param device_canvas_color: The background color of the device.
        :type device_canvas_color: Color
        :param device_canvas_text: The text that should be displayed on the device.
        :type device_canvas_text: str
        :param text_configuration: The configuration for the text on the device canvas.
        :type text_configuration: TextLabelConfiguration
        :param swipe_direction_tolerance: The directional tolerance of a swipe on the canvas.
        :type swipe_direction_tolerance: float
        :param hold_delay: The delay of a hold on the canvas.
        :type hold_delay: int
        :param hold_max_dist: The max dist for a hold on the canvas.
        :type hold_max_dist: int
        """
        self.pointer_mode = pointer_mode
        self.pointer_div_node_class = pointer_div_node_class
        self.device_canvas_color = device_canvas_color
        self.device_canvas_text = device_canvas_text
        self.text_configuration = text_configuration
        self.swipe_direction_tolerance = swipe_direction_tolerance
        self.hold_delay = hold_delay
        self.tap_max_time = tap_max_time
        self.double_tap_hold_max_time = double_tap_hold_max_time
        self.swipe_max_time = swipe_max_time
        self.hold_max_dist = hold_max_dist
        self.tap_max_dist = tap_max_dist
        self.min_drag_dist = min_drag_dist
        self.swipe_min_dist = swipe_min_dist
