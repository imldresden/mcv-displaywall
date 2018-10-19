from libavg_charts.configurations.text_label_configuration import TextMarkingConfiguration
from libavg_charts.utils.default_values import AidLineDefaults


class AidLineConfiguration(object):
    """
    A container that holds all values necessary for aid lines
    """
    def __init__(self, extra_length=AidLineDefaults.EXTRA_LENGTH, inner_line_width=AidLineDefaults.INNER_LINE_WIDTH,
                 outer_line_width=AidLineDefaults.OUTER_LINE_WIDTH, outer_line_opacity=AidLineDefaults.OUTER_LINE_OPACITY,
                 color=AidLineDefaults.LINE_COLOR, circle_radius=AidLineDefaults.CIRCLE_RADIUS,
                 show_label=AidLineDefaults.SHOW_LABEL, label_pos=AidLineDefaults.LABEL_POS,
                 label_content_axis_index=AidLineDefaults.LABEL_CONTENT_AXIS_INDEX, label_text_config=None):
        """
        :param extra_length: If the aid line should overhang over the main area of a chart, this value should be set.
        :type extra_length: int
        :param inner_line_width: The width of the main aid line in the middle.
        :type inner_line_width: int
        :param outer_line_width: The width of the outer/background line.
        :type outer_line_width: int
        :param outer_line_opacity: The opacity of the outer/background line.
        :type outer_line_opacity: float
        :param color: The color for the aid line.
        :type color: avg.Color
        :param circle_radius: Only used for CircleAidLine. The radius of the circle it should display.
        :type circle_radius: float
        :param show_label: Should a label at the side of the aid line be shown? The label shows the current value of the axis it should show.
        :type show_label: bool
        :param label_pos: On which side should the label be shown.
        :type label_pos: AidLineLabelPos
        :param label_content_axis_index: Which axis should be taken to use it as a value for the label.
        :type label_content_axis_index: int
        :param label_text_config: The text configuration for the label itself.
        :type label_text_config: TextMarkingConfiguration
        """
        self.extra_length = extra_length
        self.inner_line_width = inner_line_width
        self.outer_line_width = outer_line_width
        self.outer_line_opacity = outer_line_opacity
        self.color = color
        self.circle_radius = circle_radius
        self.show_label = show_label
        self.label_pos = label_pos
        self.label_content_axis_index = label_content_axis_index
        self.label_text_config = label_text_config if label_text_config else TextMarkingConfiguration()
