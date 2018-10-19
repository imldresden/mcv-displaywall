from multi_view_ctrl.utils.default_values import GridElementDivDefaults
from libavg.avg import Color


class GridElementDivConfigurations(object):
    def __init__(self, background_color=GridElementDivDefaults.BACKGROUND_COLOR, border_width=GridElementDivDefaults.BORDER_WIDTH,
                 border_color=GridElementDivDefaults.BORDER_COLOR, margin=GridElementDivDefaults.MARGIN):
        """
        :param background_color: The color of the background of this div.
        :type background_color: Color
        :param border_width: The color of the border for this grid div.
        :type border_width: float
        :param border_color: The color of the border of this grid div.
        :type border_color: Color
        :param margin: The margin between the display of the real content of this ground and the complete size.
        :type margin: float
        """
        self.background_color = background_color
        self.border_width = border_width
        self.border_color = border_color
        self.margin = margin
