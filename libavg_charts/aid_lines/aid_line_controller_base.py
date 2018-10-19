from math import pi
from libavg import avg
from libavg.avg import DivNode

from data_models.data_enums import DataSelectionState
from events.event_dispatcher import EventDispatcher
from libavg_charts.aid_lines.aid_line_enums import AidLineLabelPos
from libavg_charts.axis.chart_axis_enums import Orientation
from libavg_charts.configurations.aid_line_configuration import AidLineConfiguration
from libavg_charts.configurations.intersection_configuration import IntersectionConfiguration
from libavg_charts.configurations.text_label_configuration import TextMarkingConfiguration
from libavg_charts.charts.chart_basis.chart_base import ChartBase


class AidLineControllerBase(EventDispatcher):
    # key -> chart id     value -> list of aid line controllers
    __aid_line_controller_instances = {}

    STEP_FORWARD = "stepForward"
    STEP_BACKWARD = "stepBackward"

    def __init__(self, chart, aid_line_area, use_tick_snapping=False, use_data_point_snapping=False, remove_intersection_on_selection=True,
                 labels_only_at_data_points=False, aid_line_config=None, intersection_config=None):
        """
        :param chart: The chart that should be watched through this controller.
        :type chart: ChartBase
        :param aid_line_area: The area the axis is allowed to be in.
        :type aid_line_area: tuple
        :param use_tick_snapping: Should the aid line be snapping to the next tick? Only one snapping can be activated at a time.
        :type use_tick_snapping: bool
        :param use_data_point_snapping: Should the aid line be snapping to the next data point? Only one snapping can be activated at a time.
        :type use_data_point_snapping: bool
        :param remove_intersection_on_selection: Should the intersections be removed if the data object, the intersection are coupled with, is selected.
        :type remove_intersection_on_selection: bool
        :param aid_line_config: The container that holds all values necessary for aid lines.
        :type aid_line_config: AidLineConfiguration
        :param intersection_config: The container that holds all values necessary for intersections.
        :type intersection_config: IntersectionConfiguration
        """
        EventDispatcher.__init__(self)

        if chart.view_id not in AidLineControllerBase.__aid_line_controller_instances:
            AidLineControllerBase.__aid_line_controller_instances[chart.view_id] = []
        AidLineControllerBase.__aid_line_controller_instances[chart.view_id].append(self)

        self._chart = chart
        self._chart.selection_data_holder.start_listening(
            selection_set_added=self._on_selection_set_changed,
            selection_set_removed=self._on_selection_set_changed
        )
        for data_object in self._chart.data_objects.values():
            data_object.start_listening(color_changed=self._on_data_object_color_changed)

        self._internal_div = avg.DivNode(parent=self._chart)
        self._intersection_div = avg.DivNode(parent=self._internal_div)
        self._aid_lines_div = avg.DivNode(parent=self._internal_div)
        # key -> object ids     value -> dict: (key -> position of the intersection     value -> Node for the label)
        self._intersection_nodes = {}

        self._aid_line_area = aid_line_area
        self._use_tick_snapping = use_tick_snapping
        self._use_data_point_snapping = use_data_point_snapping if not use_tick_snapping else False
        self._remove_intersection_on_selection = remove_intersection_on_selection
        # TODO: Currently this only affects the line charts (through the intersections). The other possibilities could be added if wished.
        self._labels_only_at_data_points = labels_only_at_data_points
        self._aid_line_config = aid_line_config if aid_line_config else AidLineConfiguration()
        self._intersection_config = intersection_config if intersection_config else IntersectionConfiguration()
        if not intersection_config:
            self._intersection_config.marking_text_config = TextMarkingConfiguration(offset_to_other_element=self._intersection_config.radius)

        self.bind(self.STEP_FORWARD, self._on_step_forward)
        self.bind(self.STEP_BACKWARD, self._on_step_backward)

    @property
    def aid_line_area(self):
        """
        :rtype: tuple
        """
        return self._aid_line_area

    @aid_line_area.setter
    def aid_line_area(self, aid_line_area):
        """
        :type aid_line_area: tuple
        """
        self._aid_line_area = aid_line_area

    @property
    def show_intersections(self):
        """
        :rtype: bool
        """
        return self._intersection_config.show_intersections

    @show_intersections.setter
    def show_intersections(self, show_intersections):
        """
        :type show_intersections: bool
        """
        self._intersection_config.show_intersections = show_intersections
        if not show_intersections:
            self._remove_intersections()

    @property
    def show_intersection_labels(self):
        """
        :rtype: bool
        """
        return self._intersection_config.show_label

    @show_intersection_labels.setter
    def show_intersection_labels(self, show_intersection_label):
        """
        :type show_intersection_label: bool
        """
        self._intersection_config.show_label = show_intersection_label

    @property
    def show_aid_line_labels(self):
        """
        :rtype: bool
        """
        return self._aid_line_config.show_label

    @show_aid_line_labels.setter
    def show_aid_line_labels(self, show_aid_line_labels):
        """
        :type show_aid_line_labels: bool
        """
        self._aid_line_config.show_label = show_aid_line_labels

    @property
    def use_tick_snapping(self):
        """
        :rtype: bool
        """
        return self._use_tick_snapping

    @use_tick_snapping.setter
    def use_tick_snapping(self, value):
        """
        :type value: bool
        """
        if value == self._use_tick_snapping:
            return

        self._use_tick_snapping = value
        self._use_data_point_snapping = False if self._use_data_point_snapping and value else self._use_data_point_snapping

    @property
    def use_data_point_snapping(self):
        """
        :rtype: bool
        """
        return self._use_data_point_snapping

    @use_data_point_snapping.setter
    def use_data_point_snapping(self, value):
        """
        :type value: bool
        """
        if value == self._use_tick_snapping:
            return

        self._use_data_point_snapping = value
        self._use_tick_snapping = False if self._use_tick_snapping and value else self._use_tick_snapping

    @property
    def labels_only_at_data_points(self):
        """
        :rtype: bool
        """
        return self._labels_only_at_data_points

    @labels_only_at_data_points.setter
    def labels_only_at_data_points(self, value):
        """
        :type value: bool
        """
        self._labels_only_at_data_points = value

    @property
    def use_data_object_color_for_intersection_labels(self):
        """
        :rtype: bool
        """
        return self._intersection_config.use_data_object_color_for_intersection_labels

    @use_data_object_color_for_intersection_labels.setter
    def use_data_object_color_for_intersection_labels(self, value):
        """
        :type value: bool
        """
        self._intersection_config.use_data_object_color_for_intersection_labels = value

    @property
    def aid_line_config(self):
        """
        :rtype: AidLineConfiguration
        """
        return self._aid_line_config

    @aid_line_config.setter
    def aid_line_config(self, aid_line_values):
        """
        :type aid_line_values: AidLineConfiguration
        """
        self._aid_line_config = aid_line_values

    @property
    def intersection_config(self):
        """
        :rtype: IntersectionConfiguration
        """
        return self._intersection_config

    @intersection_config.setter
    def intersection_config(self, intersection_values):
        """
        :type intersection_values: IntersectionConfiguration
        """
        self._intersection_config = intersection_values

    def set_attributes(self, **kwargs):
        """
        Sets, if possible, different attributes of this aid line controller.

        :param kwargs: The different attributes.
        :type kwargs: dict[str, ]
        """
        # TODO: Check if the attribute got the right type.
        for attribute, value in kwargs.iteritems():
            if hasattr(self, attribute):
                setattr(self, attribute, value)

    def invoke_event(self, event_name, **kwargs):
        """
        Invokes an event for this aid line controller.

        :param event_name: The event name.
        :type event_name: str
        :param kwargs: The possible event parameters.
        """
        self.dispatch(event_name, **kwargs)

    def delete(self):
        """
        Delete this controller and removes all events from the chart.
        """
        AidLineControllerBase.__aid_line_controller_instances[self._chart.view_id].pop(self)
        if len(AidLineControllerBase.__aid_line_controller_instances[self._chart.view_id]) == 0:
            AidLineControllerBase.__aid_line_controller_instances.pop(self._chart.view_id)

        del self

    def _draw_intersections(self, intersections):
        """
        Draws intersection nodes for a given dict.

        :param intersections: The intersections that should be displayed.
        :type intersections: dict[Node, list[tuple[float, float]]]
        """
        if not self._intersection_config.show_intersections:
            return

        for key, positions in intersections.iteritems():
            for pos in positions:
                if key not in self._intersection_nodes:
                    self._intersection_nodes[key] = {}
                if pos in self._intersection_nodes[key]:
                    continue

                self._intersection_nodes[key][pos] = avg.DivNode(parent=self._intersection_div)
                avg.CircleNode(
                    parent=self._intersection_nodes[key][pos],
                    pos=pos,
                    r=self._intersection_config.radius,
                    color=self._intersection_config.color,
                    fillcolor=self._intersection_config.color,
                    fillopacity=1 if self._intersection_config.filled else 0,
                    strokewidth=self._intersection_config.stroke_width
                )
                if self._intersection_config.show_label:
                    if self._intersection_config.use_data_object_color_for_intersection_labels:
                        text_color = self._chart.data_objects[key].color
                    else:
                        text_color = self._intersection_config.marking_text_config.color

                    label_div = avg.DivNode(
                        parent=self._intersection_nodes[key][pos],
                        angle=-pi / 5,
                        pivot=(0, 0)
                    )
                    rect = avg.RectNode(
                        parent=label_div,
                        strokewidth=0,
                        fillopacity=0.75,
                        fillcolor="fff",
                        active=True if self._chart.data_objects[key].selection_state is DataSelectionState.Selected else False
                    )
                    label = avg.WordsNode(
                        parent=label_div,
                        text=self._get_intersection_label_text(node=self._chart.data_object_nodes[key], obj_id=key, pos=pos),
                        alignment="left",
                        variant="bold" if self._chart.data_objects[key].selection_state is DataSelectionState.Selected else "",
                        fontsize=self._intersection_config.marking_text_config.font_size,
                        color=text_color,
                        rawtextmode=True
                    )
                    # TODO: The position could be better calculated.
                    label_div.pos = (pos[0] + self._intersection_config.marking_text_config.offset_to_other_element / 2,
                                     pos[1] - (label.size[1] / 2 + self._intersection_config.marking_text_config.offset_to_other_element))
                    rect.pos = -label.size[0] * 0.05, -label.size[1] * 0.05
                    rect.size = label.size[0] * 1.1, label.size[1] * 1.1

        # If the intersection keys are in a current selection, move the intersection to the top.
        for key, nodes in self._intersection_nodes.iteritems():
            if len(self._chart.selection_data_holder.check_if_selection_in_set([[key]])) == 0:
                continue
            for node in nodes.itervalues():
                node.parent.reorderChild(node, node.parent.getNumChildren() - 1)

    def _draw_label(self, aid_line_div, orientation):
        """
        Draws a label on a given aid line.

        :param aid_line_div: The div with the aid line in it.
        :type aid_line_div: DivNode
        :param orientation: The orientation of the aid line.
        :type orientation: Orientation
        """
        if not self._aid_line_config.show_label:
            return

        aid_line = aid_line_div.getChild(0)
        if isinstance(aid_line_div.getChild(aid_line_div.getNumChildren() - 1), avg.DivNode):
            aid_line_div.removeChild(aid_line_div.getNumChildren() - 1)

        # Generate all necessary values for the label at the aid line.
        if orientation is Orientation.Horizontal:
            value = self._chart.vertical_axis_views.values()[self._aid_line_config.label_content_axis_index].get_data_value_from_pos(pos=aid_line_div.pos[1])
            if self._aid_line_config.label_pos is AidLineLabelPos.Top:
                alignment, pos, offset = "left", aid_line.pos2, 1
            else:
                alignment, pos, offset = "right", aid_line.pos1, -1
        else:
            value = self._chart.horizontal_axis_views.values()[self._aid_line_config.label_content_axis_index].get_data_value_from_pos(pos=aid_line_div.pos[0])
            if self._aid_line_config.label_pos is AidLineLabelPos.Top:
                alignment, pos, offset = "right", aid_line.pos1, -1
            else:
                alignment, pos, offset = "left", aid_line.pos2, 1

        label_div = avg.DivNode(parent=aid_line_div)
        rect = avg.RectNode(
            parent=label_div,
            strokewidth=0,
            fillopacity=0.75,
            fillcolor="fff"
        )
        label = avg.WordsNode(
            parent=label_div,
            pos=(0, 0),
            text=str(value),
            alignment=alignment,
            pivot=(0, 0),
            angle=0 if orientation is Orientation.Horizontal else pi / 2,
            fontsize=self._aid_line_config.label_text_config.font_size,
            color=self._aid_line_config.label_text_config.color,
            rawtextmode=True
        )

        # Set the position for the label.
        if orientation is Orientation.Horizontal:
            pos = (pos[0] + offset * self._aid_line_config.label_text_config.offset_to_other_element,
                   pos[1] - label.size[1] / 2)
        else:
            pos = (pos[0] + label.size[1] / 2,
                   pos[1] + offset * self._aid_line_config.label_text_config.offset_to_other_element)
        label_div.pos = pos

        size = (label.size[1], label.size[0]) if orientation is Orientation.Vertical else label.size
        rect.size = size[0] * 1.1, size[1] * 1.1
        rect.pos = -size[0] * 1.05, -size[1] * 0.05

    @staticmethod
    def _get_next_tick_index(tick_positions, aid_line_pos, coordinate):
        """
        Calculates the next tick from the pos of the aid line.

        :param tick_positions: All positions of the ticks on an axes.
        :type tick_positions: list[float]
        :param aid_line_pos: The aid line that should be checked for.
        :type aid_line_pos: tuple[float, float]
        :param coordinate: Which coordinate should be used. 0 for x, 1 for y
        :type coordinate: int
        :return: The index of the next tick.
        :rtype: int
        """
        index = None
        if aid_line_pos[coordinate] <= tick_positions[0]:
            index = 0
        elif aid_line_pos[coordinate] >= tick_positions[-1]:
            index = len(tick_positions) - 1
        else:
            for i in range(1, len(tick_positions)):
                if not tick_positions[i - 1] <= aid_line_pos[coordinate] <= tick_positions[i]:
                    continue

                index = i
                # TODO: Not use the nearest tick.
                if aid_line_pos[coordinate] - tick_positions[i - 1] < tick_positions[i] - aid_line_pos[coordinate]:
                    index = i - 1
                break

        return index

    def _get_intersection_label_text(self, node, obj_id, pos):
        """
        Calculates the text that the label on the intersection should show. If the content for the label is 'ObjName' the names of the data objects the intersection is with will be chosen.
        If the content is an axis the value of this axis will be displayed. If no axis was found it will show nothing.

        :param node: The node that was intersected.
        :type node: Node
        :param obj_id: The id of the object this label is for.
        :type obj_id: str
        :param pos: The position of the intersection.
        :type pos: tuple[float, float]
        :return: The text for the label.
        :rtype: str
        """
        text = None
        # Get the value from the axis if an axis exists with the right name.
        if self._intersection_config.label_content_type == 'axis':
            for key, axis_data in self._chart.horizontal_axis_views.iteritems():
                if key != self._intersection_config.label_content:
                    continue

                text = str(axis_data.get_data_value_from_pos(pos=pos[0]))
                break
            if text is None:
                for key, axis_data in self._chart.vertical_axis_views.iteritems():
                    if key != self._intersection_config.label_content:
                        continue

                    text = str(axis_data.get_data_value_from_pos(pos=pos[1]))
                    break
        # Get the value from the data object itself.
        elif self._intersection_config.label_content_type == 'data_object':
            if obj_id in self._chart.data_objects:
                data_object = self._chart.data_objects[obj_id]
                # Get the obj name.
                if self._intersection_config.label_content == 'obj_name':
                        text = str(data_object.obj_id)
                # Get a specific value from the data object itself.
                else:
                    if self._intersection_config.label_content in data_object.attributes:
                        text = str(data_object.attributes[self._intersection_config.label_content].values[0])

        return text if text else ""

    def _remove_intersections(self, obj_id=None, pos_list=None):
        """
        Removes all drawn intersections from the chart.

        :param obj_id: The id of an object that its intersections should be removed. If None all objects will their intersections be removed.
        :type obj_id: str
        :param pos_list: The position of interesections that should be removed from objects. If None all intersection of an object will be removed.
        :type pos_list: list[float]
        """
        if obj_id is not None and obj_id not in self._intersection_nodes:
            return

        if obj_id is not None:
            for pos, node in zip(self._intersection_nodes[obj_id].keys()[:], self._intersection_nodes[obj_id].values()[:]):
                if pos_list is None or (pos_list is not None and pos not in pos_list):
                    node.unlink(True)
                    return self._intersection_nodes[obj_id].pop(pos)
            if len(self._intersection_nodes[obj_id]) == 0:
                self._intersection_nodes.pop(obj_id)
        else:
            for key, pos_dict in self._intersection_nodes.iteritems():
                for pos, node in pos_dict.iteritems():
                    node.unlink(True)
            self._intersection_nodes.clear()

    def reset(self):
        """
        Resets this aid line controller.
        """
        raise NotImplementedError("The 'reset()' method needs to be implemented in the children of the 'AidLineControllerBase' class.")

    def _on_step_forward(self, steps=1, axis_index=0):
        """
        Moves the aid line a number of steps (to the ticks of the axis) forward.

        :param steps: The number of steps the aid line should be move forward.
        :type steps: int
        :param axis_index: The index of the axis that the step should be calculated with.
        :type axis_index: int
        """
        raise NotImplementedError("The '_on_step_forward()' method needs to be implemented in the children of the 'AidLineControllerBase' class.")

    def _on_step_backward(self, steps=1, axis_index=0):
        """
        Moves the aid line a number of steps (to the ticks of the axis) backward.

        :param steps: The number of steps the aid line should be move backward.
        :type steps: int
        :param axis_index: The index of the axis that the step should be calculated with.
        :type axis_index: int
        """
        raise NotImplementedError("The '_on_step_backward()' method needs to be implemented in the children of the 'AidLineControllerBase' class.")

    def _on_selection_set_changed(self, sender, selection_set_id, selection_diff):
        """
        Called when a selection in the chart has been changed.

        :type sender: SelectionDataHolder
        :param selection_set_id: The id of the selection set that was changed.
        :type selection_set_id: str
        :param selection_diff: The changed sub set.
        :type selection_diff: list
        :return: Was the given set removed? And all the data objects that are affected.
        :rtype: tuple[bool, dict[str, DataObjects]]
        """
        added = len(self._chart.selection_data_holder.check_if_selection_in_set(selection_diff)) != 0
        data_objects = self._chart.find_data_objects(
            data_objects=self._chart.data_objects,
            values_to_check=selection_diff,
            key=selection_set_id.split('|')[0]
        )

        for obj_id in data_objects.iterkeys():
            # Remove the intersections of an added object if it is wished.
            if added and self._remove_intersection_on_selection:
                self._remove_intersections(obj_id)

            if obj_id not in self._intersection_nodes:
                continue

            for node in self._intersection_nodes[obj_id].itervalues():
                node.parent.reorderChild(node, node.parent.getNumChildren() - 1)
                rect = node.getChild(1).getChild(0)
                label = node.getChild(1).getChild(1)
                label.variant = "bold" if added else "Regular"
                rect.active = True if added else False

        return not added, data_objects

    def _on_data_object_color_changed(self, sender, new_color):
        """
        Called when a data objects color has changed.

        :type sender: DataObject
        :param new_color: The new color of the data object.
        :type new_color: avg.Color
        """
        # Set the color of the intersection labels for this object.
        if not (self.intersection_config.use_data_object_color_for_intersection_labels and self._intersection_config.show_label):
            return
        if sender.obj_id not in self._intersection_nodes:
            return

        for node in self._intersection_nodes[sender.obj_id].values():
            label = node.getChild(1).getChild(1)
            label.color = new_color

    @staticmethod
    def has_data_object_in_chart_an_intersection(chart_id, data_object_id):
        """
        Checks if a data object in a given chart has an intersection through any aid line controller.

        :param chart_id: The id of the chart.
        :type chart_id: str
        :param data_object_id: The id of the data object.
        :type data_object_id: str
        :return: Has the data object an intersection.
        :rtype: bool
        """
        if chart_id not in AidLineControllerBase.__aid_line_controller_instances:
            return False

        has_intersection = False
        # Go through all aid line controllers for this chart and check if intersection should be shown and if there is
        # and intersection on the data object given.
        for controller in AidLineControllerBase.__aid_line_controller_instances[chart_id]:
            if not(controller.intersection_config.show_intersections and controller.intersection_config.show_label):
                continue

            if data_object_id in controller._intersection_nodes:
                has_intersection = True
                break

        return has_intersection
