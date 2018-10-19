from libavg import avg
from libavg.avg import Color, RectNode

from libavg_charts.axis.chart_axis_enums import *
from libavg_charts.axis.chart_axis_enums import Orientation
from libavg_charts.charts.chart_basis.two_axis_chart import TwoAxisChart
from libavg_charts.configurations.chart_axis_configuration import ChartAxisConfiguration
from libavg_charts.utils.default_values import ChartDefaults
from configs.visual_data import VisDefaults as defaults


class BarChartBase(TwoAxisChart):
    """
    The base for all bar charts.
    """
    def __init__(self, orientation=Orientation.Vertical,
                 bar_line_width=ChartDefaults.BAR_CHART_BAR_LINE_WIDTH, bar_spacing=ChartDefaults.BAR_CHART_BAR_SPACING,
                 bar_width=ChartDefaults.BAR_CHART_BAR_WIDTH, **kwargs):
        """
        The parameter 'data' will not be used with this class.
        The axis configuration can be customized as wished. But the marking side, orientation, tick side and the bottom offset of the x axis will be set through this class.

        :param orientation: The orientation of the bars in the bar chart.
        :type orientation: Orientation
        :param bar_line_width: The width of the border line of bars in this chart.
        :type bar_line_width: float
        :param bar_spacing: The minimum spacing between two bars in this chart.
        :type bar_spacing: float
        :param kwargs: All other parameter for the div node and the two axis chart.
        """
        self._orientation = orientation
        self._bar_line_width = bar_line_width
        self._bar_spacing = bar_spacing
        self._bar_width = bar_width

        super(BarChartBase, self).__init__(**kwargs)
        # Move the data in the background to prevent overlapping with thw axis.
        self.reorderChild(self._axis_div, self.getNumChildren() - 1)

    @property
    def orientation(self):
        """
        :rtype: Orientation
        """
        return self._orientation

    def _create_data_objects(self, x_axis_data, y_axis_data):
        """
        Creates data objects visualisations for all data objects in this chart.

        :type x_axis_data: DataDescription
        :type y_axis_data: DataDescription
        """
        raise NotImplementedError("The method 'TwoAxisCharts._create_data_objects' needs to be overwritten from child classes!")

    def _generate_axis_configurations(self, x_axis_config, y_axis_config):
        """
        Sets the axis configuration for this chart.
        It should be overwritten but also be used from the children classes if necessary.

        :param x_axis_config: The input configuration for the x axis of this chart.
        :type x_axis_config: ChartAxisConfiguration
        :param y_axis_config: The input configuration for the y axis of this chart.
        :type y_axis_config: ChartAxisConfiguration
        :return: The created or changed configurations for the axis. First is the x axis, second the y axis.
        :rtype: tuple[ChartAxisConfiguration, ChartAxisConfiguration]
        """
        x_axis_config, y_axis_config = super(BarChartBase, self)._generate_axis_configurations(x_axis_config=x_axis_config, y_axis_config=y_axis_config)

        x_axis_config.tick_side = TickSide.Right
        y_axis_config.tick_side = TickSide.Left

        return x_axis_config, y_axis_config

    def _calc_bar_width(self, x_key_name, y_key_name):
        """
        Calculates the width of the bars.

        :param x_key_name: The key name for the x axis.
        :type x_key_name: str
        :param y_key_name: The key name for the y axis.
        :type y_key_name: str
        :return: The width of the bars.
        :rtype: float
        """
        if self._bar_width:
            return self._bar_width

        bar_pos_dist = self.horizontal_axis_views[x_key_name].tick_distance if self._orientation is Orientation.Vertical else self.vertical_axis_views[y_key_name].tick_distance
        bar_width = bar_pos_dist - 2 * self._bar_spacing

        # TODO: Maybe change the min_bar_width calculation.
        # Get the distance between the first tick and the other axis.
        if self._orientation is Orientation.Vertical:
            min_bar_width = self._x_axis_config.bottom_offset - self._axis_cross_offset + 2 * self._bar_spacing
        else:
            min_bar_width = self._y_axis_config.top_offset + 2 * self._bar_spacing

        if bar_width > min_bar_width:
            bar_width = min_bar_width

        return bar_width

    def _create_new_bar(self, x_key_name, y_key_name, x_value, y_value, bar_width, color):
        """
        Creates a new bar with the given parameters.

        :param x_key_name: The key_name for the x axis.
        :type x_key_name: str
        :param y_key_name: The key_name for the y axis.
        :type y_key_name: str
        :param x_value: The value on the x axis for this bar.
        :type x_value: object
        :param y_value: The value on the y axis for this bar.
        :type y_value: object
        :param bar_width: The width of the bar.
        :type bar_width: float
        :param color: The color for this bar.
        :type color: Color
        :return: The newly created bar.
        :rtype: RectNode
        """
        # Convert the value in coordinates.
        pos_x = self.horizontal_axis_views[x_key_name].get_pos_from_data_value(x_value)
        pos_y = self.vertical_axis_views[y_key_name].get_pos_from_data_value(y_value)

        # Calculate the size and position of the bar.
        # Use the x axis position for the bottom end.
        if self._orientation is Orientation.Vertical:
            pos = pos_x - bar_width / 2, self.horizontal_axis_views[x_key_name].pos[1]
            size = bar_width, pos_y - self.horizontal_axis_views[x_key_name].pos[1]
            pos = pos[0], pos[1] + size[1]
            size = size[0], -size[1]
        else:
            pos = self.vertical_axis_views[y_key_name].pos[0], pos_y - bar_width / 2
            size = pos_x - self.vertical_axis_views[y_key_name].pos[0], bar_width

        new_bar = avg.RectNode(
            parent=self._data_div,
            strokewidth=self._bar_line_width,
            pos=pos,
            size=size,
            fillopacity=defaults.ITEM_OPACITY,
            fillcolor=defaults.ITEM_COLOR,
            color=defaults.ITEM_COLOR
        )

        return new_bar
