from pointer_ctrl.pointer_example import PointerExample
from pointer_ctrl.pointer_enums import PointerModes
from libavg_charts.configurations.text_label_configuration import TextLabelConfiguration
from utils import colors


class PointerModeDefaults(object):
    POINTER_MODE = PointerModes.OuterView
    POINTER_DIV_NODE_CLASS = PointerExample
    DEVICE_CANVAS_COLOR = colors.GREY_DARKEN_3
    DEVICE_CANVAS_TEXT = ""
    TEXT_CONFIGURATION = TextLabelConfiguration(font_size=30, color=colors.WHITE_DARKEN_1, offset_to_other_element=0)
