from collections import OrderedDict

from libavg import avg

from data_models.data_enums import DataType
from libavg_charts.aid_lines.factory.aid_line_controller_factory import AidLineControllerFactory
from libavg_charts.axis.chart_axis import ChartAxis
from libavg_charts.axis.chart_axis_enums import *
from libavg_charts.charts.chart_basis.chart_base import ChartBase
from libavg_charts.configurations.chart_axis_configuration import ChartAxisConfiguration
from libavg_charts.utils.default_values import ChartDefaults


class ParallelCoordinatesPlot(ChartBase):
    def __init__(self, axis_data, axis_configs=None, data_line_width=ChartDefaults.LINE_CHART_DATA_LINE_WIDTH, **kwargs):
        """
        The axis configuration can be customized as wished. But the orientation will be set through this class.

        :param axis_data: All axis data that should be shown in this chart. The list should have minimal two elements.
        :type axis_data: list[DataDescription]
        :param axis_configs: The configuration for the axis. Its the same for all the axis in this plot.
        :type axis_configs: list[ChartAxisConfiguration]
        :param data_line_width: The width of the data line in this chart.
        :type data_line_width: float
        :param kwargs: All other parameter for the div node and the chart base.
        """
        super(ParallelCoordinatesPlot, self).__init__(**kwargs)

        self.__data_line_width = data_line_width
        self._vertical_axis_data = OrderedDict([(ad.key_name, ad) for ad in axis_data])
        self._axis_configs = self._generate_axis_configurations(axis_configs=axis_configs if axis_configs else [])

    def draw_chart(self):
        """
        Draws/Redraws this whole chart. It will not be drawn if this methods wasn't called.
        """
        # Remove all old divs.
        for axis in self._axis_views.itervalues():
            axis.unlink(True)
        self._axis_views.clear()
        for data_object in self._data_object_nodes.itervalues():
            data_object.unlink(True)
        self._data_object_nodes.clear()

        # Draw the new content for the chart.
        self._padding_size = (self.size[0] - self._chart_config.padding_left - self._chart_config.padding_right,
                              self.size[1] - self._chart_config.padding_top - self._chart_config.padding_bottom)
        axis_distance = self._padding_size[0] / (len(self._vertical_axis_data) - 1)
        for i, axis_d in enumerate(self._vertical_axis_data.itervalues()):
            new_axis = ChartAxis(
                parent=self._axis_div,
                data_desc=axis_d,
                axis_length=self._padding_size[1],
                axis_config=self._axis_configs[i]
            )
            new_axis.pos = i * axis_distance + self._chart_config.padding_left, self._chart_config.padding_top
            self._axis_views[axis_d.key_name] = new_axis

        self._draw_label()
        self._create_data_objects()

    def _create_data_objects(self):
        """
        Creates data objects visualisations for all data objects in this chart.
        """
        for data_object in self._data_objects.itervalues():
            point_list = []
            # Get all the values.
            for key, axis_view in self._axis_views.iteritems():
                # Convert the value in coordinates.
                pos_y = axis_view.get_pos_from_data_value(data_object.attributes[key].values[0])
                point_list.append((axis_view.pos[0], pos_y))

            # Create the new data line.
            new_line = avg.PolyLineNode(
                parent=self._data_div,
                strokewidth=self.__data_line_width,
                pos=point_list,
                color=data_object.color
            )
            self._data_object_nodes[data_object.obj_id] = new_line

        super(ParallelCoordinatesPlot, self)._create_data_objects_for_base()

    def add_aid_line_controller(self, aid_line_controller_type):
        """
        Adds a new aid line controller to this chart.

        :param aid_line_controller_type: The controller that should be added.
        :type aid_line_controller_type: AidLineType
        """
        if aid_line_controller_type in self._aid_line_controllers:
            return

        min_x = min((av.pos[0] for av in self._axis_views.values()))
        max_x = max((av.pos[0] for av in self._axis_views.values()))
        aid_line_area = min_x, self._chart_config.padding_top, max_x, self.size[1] - self._chart_config.padding_right

        self._aid_line_controllers[aid_line_controller_type] = AidLineControllerFactory.create_aid_line_controller(aid_line_controller_type, self, aid_line_area)
        self._add_aid_line_controller(aid_line_controller_type=aid_line_controller_type)

    def _generate_axis_configurations(self, axis_configs):
        """
        Sets the axis configuration for this chart.
        It should be overwritten but also be used from the children classes if necessary.

        :param axis_configs: The input configuration for the all the axis of this chart.
        :type axis_configs: list[ChartAxisConfiguration]
        :return: The created or changed configurations for the axis. First is the x axis, second the y axis.
        :rtype: list[ChartAxisConfiguration]
        """
        new_axis_configs = []
        for i, axis_data in enumerate(self._vertical_axis_data.itervalues()):
            axis_config = axis_configs[i] if i < len(axis_configs) else ChartAxisConfiguration()
            axis_config.axis_orientation = Orientation.Vertical
            if DataType.is_string(axis_data.data_type):
                axis_config.data_steps = len(axis_data.data)
                axis_config.marking_steps = 1
            elif axis_data.data[0] == axis_data.data[1]:
                axis_config.data_steps = 1
            new_axis_configs.append(axis_config)

        return new_axis_configs
