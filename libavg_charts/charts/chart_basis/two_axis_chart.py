from libavg import avg

from data_models.data_enums import DataType
from libavg_charts.aid_lines.aid_line_enums import AidLineType
from libavg_charts.aid_lines.factory.aid_line_controller_factory import AidLineControllerFactory
from libavg_charts.axis.chart_axis import ChartAxis
from libavg_charts.axis.chart_axis_enums import *
from libavg_charts.charts.chart_basis.chart_base import ChartBase
from libavg_charts.configurations.chart_axis_configuration import ChartAxisConfiguration
from libavg_charts.utils.default_values import TwoAxisChartDefaults


class TwoAxisChart(ChartBase):
    """
    Represents a chart with two axis: x and y. y is always left and x always on the bottom.
    """
    def __init__(self, x_axis_data, y_axis_data, x_axis_config=None, y_axis_config=None,
                 axis_cross_offset=TwoAxisChartDefaults.AXIS_CROSS_OFFSET, **kwargs):
        """
        The axis configuration can be customized as wished. But the marking side and the orientation will be set through this class.

        :param x_axis_data: The data object for the x axis.
        :type x_axis_data: DataDescription
        :param y_axis_data: The data object for the y axis.
        :type y_axis_data: DataDescription
        :param x_axis_config: The configuration for the x axis of this chart.
        :type x_axis_config: ChartAxisConfiguration
        :param y_axis_config: The configuration for the y axis of this chart.
        :type y_axis_config: ChartAxisConfiguration
        :param kwargs: All other parameter for the div node and the chart base.
        """
        super(TwoAxisChart, self).__init__(**kwargs)
        self._horizontal_axis_data = {x_axis_data.key_name: x_axis_data}
        self._vertical_axis_data = {y_axis_data.key_name: y_axis_data}
        self._x_axis_config, self._y_axis_config = self._generate_axis_configurations(x_axis_config=x_axis_config, y_axis_config=y_axis_config)
        self._axis_cross_offset = axis_cross_offset

    @property
    def horizontal_axis_data(self):
        """
        :rtype: dict[str, DataDescription]
        """
        return self._horizontal_axis_data

    @property
    def vertical_axis_data(self):
        """
        :rtype: dict[str, DataDescription]
        """
        return self._vertical_axis_data

    @property
    def horizontal_axis_views(self):
        """
        :rtype: dict[str, ChartAxis]
        """
        return {k: av for k, av in self._axis_views.iteritems() if av.orientation is Orientation.Horizontal}

    @property
    def vertical_axis_views(self):
        """
        :rtype: dict[str, ChartAxis]
        """
        return {k: av for k, av in self._axis_views.iteritems() if av.orientation is Orientation.Vertical}

    @property
    def x_axis_config(self):
        """
        :rtype: ChartAxisConfiguration
        """
        return self._x_axis_config

    @property
    def y_axis_config(self):
        """
        :rtype: ChartAxisConfiguration
        """
        return self._y_axis_config

    def draw_chart(self):
        """
        Draws/Redraws this whole chart. It will not be drawn if this methods wasn't called.
        """
        # Remove all old divs.
        if len(self.horizontal_axis_views) > 0:
            self.horizontal_axis_views.values()[0].unlink(True)
        self.horizontal_axis_views.clear()
        if len(self.vertical_axis_views) > 0:
            self.vertical_axis_views.values()[0].unlink(True)
        self.vertical_axis_views.clear()
        for data_object in self._data_object_nodes.itervalues():
            data_object.unlink(True)
        self._data_object_nodes.clear()
        for grid_line in list([self._grid_lines_div.getChild(i) for i in range(self._grid_lines_div.getNumChildren())]):
            grid_line.unlink(True)

        # Draw the new content for the chart.
        self._padding_size = (self.size[0] - self._chart_config.padding_left - self._chart_config.padding_right,
                              self.size[1] - self._chart_config.padding_top - self._chart_config.padding_bottom)
        x_axis = ChartAxis(
            parent=self._axis_div,
            data_desc=self._horizontal_axis_data.values()[0],
            axis_length=self._padding_size[0],
            axis_config=self._x_axis_config
        )
        x_axis.pos = (self._chart_config.padding_left, self._chart_config.padding_top + self._padding_size[1] - self._axis_cross_offset)
        x_axis.start_listening(marking_tap=self._on_axis_marking_tap)
        self._axis_views[self._horizontal_axis_data.values()[0].key_name] = x_axis

        y_axis = ChartAxis(
            parent=self._axis_div,
            data_desc=self._vertical_axis_data.values()[0],
            axis_length=self._padding_size[1],
            axis_config=self._y_axis_config
        )
        y_axis.pos = (self._chart_config.padding_left + self._axis_cross_offset, self._chart_config.padding_top)
        y_axis.start_listening(marking_tap=self._on_axis_marking_tap)
        self._axis_views[self._vertical_axis_data.values()[0].key_name] = y_axis

        # self._data_div.size = self.size
        self._background_div.size = self.size

        self._draw_grid_lines(x_axis)
        self._draw_grid_lines(y_axis)

        self._draw_label()
        self._create_data_objects(self._horizontal_axis_data.values()[0], self._vertical_axis_data.values()[0])

    def _draw_grid_lines(self, axis):
        """
        Draws the grid lines in this chart.

        :param axis: The axis the grid lines are connected with.
        :type axis: ChartAxis
        """
        if axis.show_grid_lines is GridLines.Nothing:
            return

        positions = axis.tick_positions if axis.show_grid_lines is GridLines.Ticks else axis.marking_positions
        for pos in positions:
            if axis.orientation is Orientation.Horizontal:
                y_axis = self.vertical_axis_views.values()[0]
                pos1 = pos + self._chart_config.padding_left, y_axis.pos[1]
                pos2 = pos + self._chart_config.padding_left, axis.pos[1] - self._axis_cross_offset
            else:
                x_axis = self.horizontal_axis_views.values()[0]
                pos1 = x_axis.pos[0] + self._axis_cross_offset, pos + self._chart_config.padding_top
                pos2 = x_axis.pos[0] + x_axis.axis_length - self._axis_cross_offset, pos + self._chart_config.padding_top

            avg.LineNode(
                parent=self._grid_lines_div,
                strokewidth=TwoAxisChartDefaults.GRID_LINE_WIDTH,
                color=TwoAxisChartDefaults.GRID_LINE_COLOR,
                opacity=TwoAxisChartDefaults.GRID_LINE_OPACITY,
                pos1=pos1,
                pos2=pos2
            )

    def _create_data_objects(self, x_axis_data, y_axis_data):
        """
        Creates data objects visualisations for all data objects in this chart. The overridden methods should call the
        '_create_data_objects' method from the parent.

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
        x_axis_config = x_axis_config if x_axis_config else ChartAxisConfiguration()
        x_axis_config.axis_orientation = Orientation.Horizontal
        x_axis_config.marking_side = MarkingSide.Right
        x_axis_config.tick_side = TickSide.Right
        x_axis_config.axis_background_side = TickSide.Right
        if DataType.is_string(self._horizontal_axis_data.values()[0].data_type):
            x_axis_config.data_steps = len(self._horizontal_axis_data.values()[0].data)
        elif self._horizontal_axis_data.values()[0].data[0] == self._horizontal_axis_data.values()[0].data[1]:
            x_axis_config.data_steps = 1

        y_axis_config = y_axis_config if y_axis_config else ChartAxisConfiguration()
        y_axis_config.axis_orientation = Orientation.Vertical
        y_axis_config.marking_side = MarkingSide.Left
        y_axis_config.tick_side = TickSide.Left
        y_axis_config.axis_background_side = TickSide.Left
        if DataType.is_string(self._vertical_axis_data.values()[0].data_type):
            y_axis_config.data_steps = len(self._vertical_axis_data.values()[0].data)
        elif self._vertical_axis_data.values()[0].data[0] == self._vertical_axis_data.values()[0].data[1]:
            y_axis_config.data_steps = 1

        return x_axis_config, y_axis_config

    def add_aid_line_controller(self, aid_line_controller_type, **kwargs):
        """
        Adds a new aid line controller to this chart.

        :param aid_line_controller_type: The controller that should be added.
        :type aid_line_controller_type: AidLineType
        :param kwargs: Other parameters for the aid line controller.
        """
        if aid_line_controller_type in self._aid_line_controllers:
            return

        x_axis = self.horizontal_axis_views.values()[0]
        y_axis = self.vertical_axis_views.values()[0]
        aid_line_area = (y_axis.pos[0], self._chart_config.padding_top, x_axis.pos[0] + x_axis.axis_size[0], x_axis.pos[1])

        self._aid_line_controllers[aid_line_controller_type] = AidLineControllerFactory.create_aid_line_controller(aid_line_controller_type, self, aid_line_area, **kwargs)
        self._add_aid_line_controller(aid_line_controller_type=aid_line_controller_type)
