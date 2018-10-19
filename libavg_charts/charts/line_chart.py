from libavg import avg

from configs.visual_data import VisDefaults as defaults
from data_models.data_enums import DataSelectionState
from data_models.data_object import DataObject
from libavg_charts.axis.chart_axis_enums import Orientation
from libavg_charts.charts.chart_basis.two_axis_chart import TwoAxisChart
from libavg_charts.utils.default_values import ChartDefaults


class LineChart(TwoAxisChart):
    """
    An easy line chart.
    It's not possible to use a sum for the y axis.
    """
    def __init__(self, orientation=Orientation.Horizontal, data_line_width=ChartDefaults.LINE_CHART_DATA_LINE_WIDTH,
                 **kwargs):
        """
        :param data_line_width: The width of the data line in this chart.
        :type data_line_width: float
        :param kwargs: All other parameter for the div node and the two axis chart.
        """
        self.__data_line_width = data_line_width
        self.__orientation = orientation

        super(LineChart, self).__init__(**kwargs)

    def _create_data_objects(self, x_axis_data, y_axis_data):
        """
        Creates data lines for all data objects in this chart.

        :type x_axis_data: DataDescription
        :type y_axis_data: DataDescription
        """
        for data_object in self._data_objects.itervalues():
            point_list = []
            # Get all the values.
            x_values = data_object.attributes[x_axis_data.key_name].values
            y_values = data_object.attributes[y_axis_data.key_name].values
            for i in range(len(x_values)):
                # Convert the value in coordinates.
                pos_x = self.horizontal_axis_views[x_axis_data.key_name].get_pos_from_data_value(x_values[i])
                pos_y = self.vertical_axis_views[y_axis_data.key_name].get_pos_from_data_value(y_values[i])
                point_list.append((pos_x, pos_y))

            # Create the new data line.
            new_line = avg.PolyLineNode(
                parent=self._data_div,
                strokewidth=self.__data_line_width,
                pos=point_list,
                color=defaults.ITEM_COLOR,
                opacity=defaults.ITEM_OPACITY
            )
            self._data_object_nodes[data_object.obj_id] = new_line

        super(LineChart, self)._create_data_objects_for_base()

    def _on_data_object_selection_state_changed(self, sender, new_state, old_state):
        """
        Called when the selection state of a data object has changed.

        :type sender: DataObject
        :param new_state: The new state.
        :type new_state: DataSelectionState
        :param old_state: The old state.
        :type old_state: DataSelectionState
        """
        # Create a new label and set it to the correct color and active.
        if new_state is not DataSelectionState.Nothing:
            if sender.obj_id not in self._data_object_label_nodes:
                self._data_object_label_nodes[sender.obj_id] = self._draw_data_object_label(data_object=sender)
            self._data_object_label_nodes[sender.obj_id].active = True
            self._data_object_label_nodes[sender.obj_id].color = sender.color
        else:
            if sender.obj_id in self._data_object_label_nodes:
                self._data_object_label_nodes[sender.obj_id].active = False

    def _draw_data_object_label(self, data_object):
        """
        Draws a label for the given data object.

        :param data_object: The data object to draw the label for.
        :type data_object: DataObject
        :return: The new label node.
        :rtype: avg.WordsNode
        """
        data_line = self._data_object_nodes[data_object.obj_id]
        if self.__orientation is Orientation.Horizontal:
            pos = sorted(data_line.pos, key=lambda p: p[1])[0]
            alignment = "center"
        else:
            pos = sorted(data_line.pos, key=lambda p: -p[0])[0]
            alignment = "left"

        label = avg.WordsNode(
            parent=self._selection_label_div,
            text=str(data_object.obj_id),
            alignment=alignment,
            fontsize=self._selection_label_text_config.font_size,
            color=data_object.color,
            rawtextmode=True
        )

        if self.__orientation is Orientation.Horizontal:
            label.pos = pos[0], pos[1] - label.size[1] - self._selection_label_text_config.offset_to_other_element
        else:
            label.pos = pos[0] + self._selection_label_text_config.offset_to_other_element, pos[1] - label.size[1] / 2

        return label

    def _on_data_object_color_changed(self, sender, new_color):
        """
        Called when the color of a data object has changed.

        :type sender: DataObject
        :param new_color: The new color.
        :type new_color: Color
        """
        self._data_object_nodes[sender.obj_id].color = new_color

    def add_aid_line_controller(self, aid_line_controller_type, **kwargs):
        """
        Adds a new aid line controller to this chart.

        :param aid_line_controller_type: The controller that should be added.
        :type aid_line_controller_type: AidLineType
        :param kwargs: Other parameters for the aid line controller.
        """
        kwargs["remove_intersection_on_selection"] = False
        super(LineChart, self).add_aid_line_controller(aid_line_controller_type, **kwargs)

