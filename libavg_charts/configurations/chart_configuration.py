from libavg_charts.utils.default_values import ChartDefaults
from libavg_charts.charts.chart_enums import LabelPosition
from libavg_charts.configurations.text_label_configuration import TextChartLabelConfiguration


class ChartConfiguration(object):
    def __init__(self, show_label=ChartDefaults.SHOW_LABEL, label_pos=ChartDefaults.LABEL_POS,
                 padding_left=ChartDefaults.PADDING_LEFT, padding_top=ChartDefaults.PADDING_TOP,
                 padding_right=ChartDefaults.PADDING_RIGHT, padding_bottom=ChartDefaults.PADDING_BOTTOM,
                 label_text_config=None):
        """
        :param show_label: Should the label be displayed?
        :type show_label: bool
        :param label_pos: The position of the label.
        :type label_pos: LabelPosition
        :param padding_left: The left padding for this chart. It should only be positive.
        :type padding_left: float
        :param padding_top: The top padding for this chart. It should only be positive.
        :type padding_top: float
        :param padding_right: The right padding for this chart. It should only be positive.
        :type padding_right: float
        :param padding_bottom: The bottom padding for this chart. It should only be positive.
        :type padding_bottom: float
        :param label_text_config: The configuration for all text for marking on this axis.
        :type label_text_config: TextLabelConfiguration
        """
        self.show_label = show_label
        self.label_pos = label_pos
        self.padding_left = padding_left
        self.padding_top = padding_top
        self.padding_right = padding_right
        self.padding_bottom = padding_bottom
        self.label_text_config = label_text_config if label_text_config else TextChartLabelConfiguration()
