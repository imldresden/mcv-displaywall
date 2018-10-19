from libavg import avg

from data_models.data_desciption import DataDescription
from data_models.data_enums import DataSelectionState
from data_models.data_object import DataObject
from libavg_charts.aid_lines.aid_line_controller_base import AidLineControllerBase
from libavg_charts.axis.chart_axis_enums import Orientation
from libavg_charts.charts.chart_basis.bar_chart_base import BarChartBase


class BarChart(BarChartBase):
    def __init__(self, **kwargs):
        super(BarChart, self).__init__(**kwargs)

    def _create_data_objects(self, x_axis_data, y_axis_data):
        """
        Creates all bars for all data objects in this chart.

        :type x_axis_data: DataDescription
        :type y_axis_data: DataDescription
        """
        bar_width = self._calc_bar_width(x_key_name=x_axis_data.key_name, y_key_name=y_axis_data.key_name)

        for data_object in self._data_objects.itervalues():
            # Get all the values.
            x_values = data_object.attributes[x_axis_data.key_name].values
            y_values = data_object.attributes[y_axis_data.key_name].values
            for i in range(len(x_values)):
                self._data_object_nodes[data_object.obj_id] = self._create_new_bar(
                    x_key_name=x_axis_data.key_name,  y_key_name=y_axis_data.key_name,
                    x_value=x_values[i], y_value=y_values[i],
                    bar_width=bar_width, color=data_object.color
                )

        super(BarChart, self)._create_data_objects_for_base()

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

            active = True
            if new_state is DataSelectionState.Highlighted and AidLineControllerBase.has_data_object_in_chart_an_intersection(self._view_id, sender.obj_id):
                active = False

            self._data_object_label_nodes[sender.obj_id].active = active
            self._data_object_label_nodes[sender.obj_id].color = sender.color
        else:
            if sender.obj_id in self._data_object_label_nodes:
                self._data_object_label_nodes[sender.obj_id].active = False

        # Get the markings of the data object.
        marking = None
        if self._orientation is Orientation.Horizontal:
            axis_key = self.vertical_axis_data.keys()[0]
            sender_value = sender.attributes[axis_key].values[0]
            if sender_value in self.vertical_axis_views[axis_key].markings:
                marking = self.vertical_axis_views[axis_key].markings[sender_value]
        else:
            axis_key = self.horizontal_axis_data.keys()[0]
            sender_value = sender.attributes[axis_key].values[0]
            if sender_value in self.horizontal_axis_views[axis_key].markings:
                marking = self.horizontal_axis_views[axis_key].markings[sender_value]

        # Set the color for highlighted data objects.
        if new_state is DataSelectionState.Highlighted:
            if sender.obj_id in self._data_object_label_nodes:
                self._data_object_label_nodes[sender.obj_id].color = sender.color
        # Make the markings bold .
        elif new_state is DataSelectionState.Selected:
            if marking:
                marking.variant = "bold"
        # Make the markings normal.
        elif new_state is DataSelectionState.Nothing:
            if marking:
                marking.variant = "Regular"

    def _draw_data_object_label(self, data_object):
        """
        Draws a label for the given data object.

        :param data_object: The data object to draw the label for.
        :type data_object: DataObject
        :return: The new label node.
        :rtype: avg.WordsNode
        """
        bar = self._data_object_nodes[data_object.obj_id]
        if self._orientation is Orientation.Vertical:
            pos = bar.pos[0] + bar.size[0] / 2, bar.pos[1]
            text = self.vertical_axis_views.values()[0].get_data_value_from_pos(pos=pos[1])
            alignment = "center"
        else:
            pos = bar.pos[0] + bar.size[0], bar.pos[1] + bar.size[1] / 2
            text = self.horizontal_axis_views.values()[0].get_data_value_from_pos(pos=pos[0])
            alignment = "left"

        label = avg.WordsNode(
            parent=self._selection_label_div,
            text=str(text),
            alignment=alignment,
            fontsize=self._selection_label_text_config.font_size,
            color=data_object.color,
            rawtextmode=True
        )

        if self._orientation is Orientation.Vertical:
            label.pos = pos[0], pos[1] - self._selection_label_text_config.offset_to_other_element - label.size[1]
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
        self._data_object_nodes[sender.obj_id].fillcolor = new_color
        self._data_object_nodes[sender.obj_id].color = new_color
