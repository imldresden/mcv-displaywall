from libavg import avg

from configs.visual_data import VisDefaults as defaults
from data_models.data_enums import DataSelectionState
from data_models.data_enums import DataType
from data_models.data_object import DataObject
from libavg_charts.aid_lines.aid_line_controller_base import AidLineControllerBase
from libavg_charts.charts.chart_basis.two_axis_chart import TwoAxisChart
from libavg_charts.utils.default_values import ChartDefaults, DataDefaults
from utils.canvas_manager import CanvasManager


class ScatterPlot(TwoAxisChart):
    # TODO: Check if its possible that circle lie outside of the chart (behind an axis).
    def __init__(self, size_key=None, selection_key="obj_id", **kwargs):
        """
        :param size_key: The key that lies in the data object attributes that defines the size of the circles. If
                           None is given, a default value will be used.
        :type size_key: str
        :type selection_key: str
        :param kwargs: All other parameter for the div node and the two axis chart.
        """
        self._size_key = size_key
        self._selection_key = selection_key
        super(ScatterPlot, self).__init__(**kwargs)

        self._selection_data_holder.start_listening(
            selection_set_added=self._on_selection_set_changed,
            selection_set_removed=self._on_selection_set_changed
        )

    def _on_data_object_color_changed(self, sender, new_color):
        """
        Called when the color of a data object has changed.

        :type sender: DataObject
        :param new_color: The new color.
        :type new_color: Color
        """
        self._data_object_nodes[sender.obj_id].href = CanvasManager.get_circle_canvas_from_color(new_color)

    def _create_data_objects(self, x_axis_data, y_axis_data):
        """
        Creates data object representations for all data objects in this chart.
        
        :type x_axis_data: DataDescription
        :type y_axis_data: DataDescription
        """
        min_size = 10
        max_size = min(self.vertical_axis_views.values()[-1].tick_distance, self.horizontal_axis_views.values()[-1].tick_distance) - 1
        min_value, max_value = float("inf"), float("-inf")
        # Get min and max value from the attribute value that influences the circle size.
        if self._size_key:
            for data_object in self._data_objects.itervalues():
                if self._size_key not in data_object.attributes:
                    continue

                value = data_object.attributes[self._size_key].values[0]
                min_value = value if value < min_value else min_value
                max_value = value if value > max_value else max_value

        for data_object in self._data_objects.itervalues():
            if self._size_key and self._size_key in data_object.attributes:
                value_diff = max_value - min_value
                factor = float(data_object.attributes[self._size_key].values[0]) / value_diff
                size = min_size + ((max_size - min_size) * factor)
            else:
                size = max(min_size, min(ChartDefaults.SCATTER_PLOT_DATA_OBJECT_RADIUS * 2.0, max_size))
            if size < 0:
                size = 0

            # Get all the values.
            x_values = data_object.attributes[x_axis_data.key_name].values
            y_values = data_object.attributes[y_axis_data.key_name].values

            # Check if the data type was a sum:
            # Convert the value in coordinates, if its no sum use the first value in the list.
            if DataType.is_sum(self.horizontal_axis_views[x_axis_data.key_name].data_desc.data_type):
                pos_x = self.horizontal_axis_views[x_axis_data.key_name].get_pos_from_data_value(sum(x_values))
            else:
                pos_x = self.horizontal_axis_views[x_axis_data.key_name].get_pos_from_data_value(x_values[0])
            if DataType.is_sum(self.vertical_axis_views[y_axis_data.key_name].data_desc.data_type):
                pos_y = self.vertical_axis_views[y_axis_data.key_name].get_pos_from_data_value(sum(y_values[0]))
            else:
                pos_y = self.vertical_axis_views[y_axis_data.key_name].get_pos_from_data_value(y_values[0])

            new_circle = avg.ImageNode(
                parent=self._data_div,
                href=CanvasManager.get_circle_canvas_from_color(defaults.ITEM_COLOR),
                pos=(pos_x - size / 2, pos_y - size / 2),
                size=(size, size),
                opacity=defaults.ITEM_OPACITY
            )
            self._data_object_nodes[data_object.obj_id] = new_circle

        super(ScatterPlot, self)._create_data_objects_for_base()

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

        # Set the color for highlighted data objects.
        if new_state is DataSelectionState.Highlighted:
            if sender.obj_id in self._data_object_label_nodes:
                self._data_object_label_nodes[sender.obj_id].color = sender.color

    def _on_selection_set_changed(self, sender, selection_set_id, selection_diff):
        """
        Called when a selection in the chart has been changed.
        This will handle the markings of the newly selected or deleted objects.

        :type sender: SelectionDataHolder
        :param selection_set_id: The id of the selection set that was changed.
        :type selection_set_id: str
        :param selection_diff: The changed sub set.
        :type selection_diff: list
        """
        x_axis_key, y_axis_key = self.horizontal_axis_data.keys()[0], self.vertical_axis_data.keys()[0]
        markings = self.horizontal_axis_views[x_axis_key].markings
        markings.update(self.vertical_axis_views[y_axis_key].markings)

        for key, marking in markings.iteritems():
            if len(self._selection_data_holder.check_if_selection_in_set([[key]])) != 0:
                marking.variant = "bold"
            else:
                marking.variant = "Regular"

    def _draw_data_object_label(self, data_object):
        """
        Draws a label for the given data object.

        :param data_object: The data object to draw the label for.
        :type data_object: DataObject
        :return: The new label node.
        :rtype: avg.WordsNode
        """
        data_circle = self._data_object_nodes[data_object.obj_id]

        text = str(data_object.obj_id)
        if self._selection_key in data_object.attributes:
            text = str(data_object.attributes[self._selection_key].values[0])

        label = avg.WordsNode(
            parent=self._selection_label_div,
            text=text,
            fontsize=self._selection_label_text_config.font_size,
            color=data_object.color,
            rawtextmode=True
        )
        label.pos = (data_circle.pos[0] + data_circle.size[0] + self._selection_label_text_config.offset_to_other_element,
                     data_circle.pos[1] + (data_circle.size[1] - label.size[1]) / 2)

        return label

    def _on_data_objects_selected_tap(self, sender_id):
        """
        Called when on a data object in the view was tapped.

        :param sender_id: The id of the tapped node.
        :type sender_id: object
        """
        pre_selection_state = self._data_objects[sender_id].selection_state

        selection_sets = {}
        for key in self._data_keys_for_selection:
            if key not in self._data_objects[sender_id].attributes:
                continue

            if key not in selection_sets:
                selection_sets[key] = []
            selection_sets[key].append(self._data_objects[sender_id].attributes[key].values)

        for selection_key, selection_set in selection_sets.iteritems():
            selection_ids = self._selection_data_holder.check_if_selection_in_set(selection_set)
            selection_diffs = {}
            # If the selection is in a selection set, delete it from it.
            if pre_selection_state is DataSelectionState.Selected or len(selection_ids) > 0:
                for selection_id in selection_ids:
                    selection_diffs[selection_id] = self._selection_data_holder.remove_selection_from_set(
                        selection_set_id=selection_id,
                        selection_set=selection_set
                    )

                self.change_color_for_data_objects([sender_id], color=defaults.ITEM_COLOR, opacity=defaults.ITEM_OPACITY)
                self.change_selection_state_for_data_objects([sender_id], state=DataSelectionState.Nothing)
            else:
                # If the selection wasn't found, create a new set with it.
                selection_id = self._selection_data_holder.get_next_id(selection_key)
                selection_id, selection_diff = self._selection_data_holder.add_new_selection_set(
                    selection_set=selection_set,
                    selection_set_id=selection_id,
                    single_selection=False
                )
                selection_diffs[selection_id] = selection_diff

                self.change_color_for_data_objects([sender_id], color=DataDefaults.COLOR_SELECTED, opacity=defaults.ITEM_OPACITY_SELECTED)
                self.change_selection_state_for_data_objects([sender_id], state=DataSelectionState.Selected)
            for selection_id, selection_diff in selection_diffs.iteritems():
                self.dispatch(
                    self._DATA_OBJECT_SELECTION_CHANGED,
                    sender=self,
                    selection_data_holder=self._selection_data_holder,
                    selection_set_id=selection_id,
                    selection_diff=selection_diff
                )
