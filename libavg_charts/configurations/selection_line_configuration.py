from libavg_charts.utils.default_values import SelectionLineDefaults


class SelectionLineConfiguration(object):
    """
    A container that holds all values necessary for selections.
    """
    def __init__(self, extra_length=SelectionLineDefaults.EXTRA_LENGTH, width=SelectionLineDefaults.LINE_WIDTH,
                 color=SelectionLineDefaults.LINE_COLOR):
        """
        :param extra_length: The length the extra line should be overhang over the given chart area.
        :type extra_length: int
        :param width: The width of the extra line.
        :type width: int
        :param color: The color of the extra aid line that will be drawn if a selection is started.
        :type color: avg.Color
        """
        self.extra_length = extra_length
        self.width = width
        self.color = color
