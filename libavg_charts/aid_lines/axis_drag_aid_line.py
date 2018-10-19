from libavg_charts.aid_lines.helper.intersection_method_holder import IntersectionMethodHolder
from libavg_charts.aid_lines.orthogonal_aid_line import OrthogonalAidLine
from libavg_charts.axis.chart_axis_enums import Orientation
from libavg_charts.axis.interactive_div_node import InteractiveDivNode
from libavg_charts.charts.line_chart import LineChart
from libavg_charts.utils.default_values import AidLineDefaults
from logging_base.study_logging import StudyLog


class AxisDragAidLine(OrthogonalAidLine):
    DELETE_AID_LINE = "deleteAidLine"

    def __init__(self, orientation, **kwargs):
        """
        :param orientation: The orientation that this controller should watching for.
        :type orientation: Orientation
        :param kwargs: Other parameters for the base.
        """
        super(AxisDragAidLine, self).__init__(**kwargs)

        self.__orientation = orientation

        # key -> axis:ChartAxis     value -> the newly created aid line:InteractiveDivNode
        self.__newly_added_aid_lines = {}
        # key -> axis:aid line     value -> pos of the aid line at the beginning
        self.__newly_added_aid_line_pos = {}
        # key -> aid line:InteractiveDivNode     value -> axis:ChartAxis
        self.__aid_lines = {}

        axis_list = self._chart.horizontal_axis_views if self.__orientation is Orientation.Horizontal else self._chart.vertical_axis_views
        for axis in axis_list.itervalues():
            axis.start_listening(
                axis_or_tick_drag_start=self._on_axis_drag_started,
                axis_or_tick_drag=self._on_dragged,
                axis_or_tick_drag_end=self._on_drag_ended
            )

        self.bind(self.DELETE_AID_LINE, self._on_delete_aid_line)

    @property
    def orientation(self):
        """
        :rtype: Orientation
        """
        return self.__orientation

    @orientation.setter
    def orientation(self, orientation):
        """
        :type orientation: Orientation
        """
        self.__orientation = orientation

    def delete(self):
        """
        Delete this controller and removes all events from the chart.
        """
        axis_list = self._chart.horizontal_axis_views if self.__orientation is Orientation.Horizontal else self._chart.vertical_axis_views
        for axis in axis_list.itervalues():
                axis.stop_listening(
                    axis_or_tick_drag_start=self._on_axis_drag_started,
                    axis_or_tick_drag=self._on_dragged,
                    axis_or_tick_drag_end=self._on_drag_ended
                )
        super(AxisDragAidLine, self).delete()

    def _draw_horizontal_aid_line(self, pos, with_outer=True):
        """
        Draws a horizontal aid line.

        :param pos: The position of the cursor.
        :type pos: tuple[float, float]
        :param with_outer: If the outer part of the line should be drawn.
        :type with_outer: bool
        :return: The created aid line.
        :rtype: InteractiveDivNode
        """
        aid_line = super(AxisDragAidLine, self)._draw_horizontal_aid_line(pos, with_outer)
        aid_line.start_listening(
            dragged=self._on_dragged,
            drag_ended=self._on_drag_ended
        )
        return aid_line

    def _draw_vertical_aid_line(self, pos, with_outer=True):
        """
        Draws a vertical aid line.

        :param pos: The position of the cursor.
        :type pos: tuple[float, float]
        :param with_outer: If the outer part of the line should be drawn.
        :type with_outer: bool
        :return: The created aid line.
        :rtype: InteractiveDivNode
        """
        aid_line = super(AxisDragAidLine, self)._draw_vertical_aid_line(pos, with_outer)
        aid_line.start_listening(
            dragged=self._on_dragged,
            drag_ended=self._on_drag_ended
        )
        return aid_line

    def _on_delete_aid_line(self, pos):
        """
        Deletes an aid line at the pos, if an aid line lies there.

        :param pos: The pos to create a aid line on.
        :type pos: tuple[float, float]
        """
        if not (self._aid_line_area[0] <= pos[0] <= self._aid_line_area[2] and
                self._aid_line_area[1] <= pos[1] <= self._aid_line_area[3]):
            return

        aid_lines_to_remove = []
        # Get all aid lines that need to be removed through this event.
        for aid_line in self.__aid_lines.iterkeys():
            line_node = aid_line.getChild(0)

            if self.__orientation is Orientation.Horizontal:
                aid_line_size = (
                    line_node.pos1[0],
                    aid_line.pos[1] - line_node.strokewidth / 2,
                    line_node.pos2[0],
                    aid_line.pos[1] + line_node.strokewidth / 2
                )
            else:
                aid_line_size = (
                    aid_line.pos[0] - line_node.strokewidth / 2,
                    line_node.pos1[1],
                    aid_line.pos[0] + line_node.strokewidth / 2,
                    line_node.pos2[1]
                )

            if aid_line_size[0] <= pos[0] <= aid_line_size[2] and aid_line_size[1] <= pos[1] <= aid_line_size[3]:
                aid_lines_to_remove.append(aid_line)

        # Remove all aid lines that must be removed and all their corresponding data.
        for aid_line in aid_lines_to_remove:
            axis = self.__aid_lines.pop(aid_line)
            if axis in self.__newly_added_aid_lines and self.__newly_added_aid_lines[axis] is aid_line:
                self.__newly_added_aid_lines.pop(axis)
            if aid_line in self.__newly_added_aid_line_pos:
                self.__newly_added_aid_line_pos.pop(aid_line)
            aid_line.unlink(True)

        if self._intersection_config.show_intersections:
            self._remove_intersections()
            self._draw_intersections(intersections=self._get_intersections(
                aid_line_orientations=[self.__orientation] * len(self.__aid_lines),
                aid_line_positions=[a.pos for a in self.__aid_lines.keys()]
            ))

    def _on_axis_drag_started(self, sender):
        """
        Called when a drag on an axis has started.

        :type sender: ChartAxis
        """
        axis = sender
        # Only allow one aid line to be created from one axis at a time.
        if axis in self.__newly_added_aid_lines:
            return
        # Check which axis this is:
        # Set the size of the line node.
        if self.__orientation is Orientation.Horizontal:
            aid_line = self._draw_horizontal_aid_line(pos=axis.pos)
            StudyLog.get_instance().write_event_log('An horizontal axis drag aid line in chart {} was created.'.format(self._chart.view_id))
        else:
            aid_line = self._draw_vertical_aid_line(pos=axis.pos)
            StudyLog.get_instance().write_event_log('An vertical axis drag aid line in chart {} was created.'.format(self._chart.view_id))

        self.__newly_added_aid_lines[axis] = aid_line
        self.__newly_added_aid_line_pos[aid_line] = aid_line.pos
        # Check which axis this is.
        self.__aid_lines[aid_line] = axis

        # Draw the intersections and the labels.
        if self._intersection_config.show_intersections:
            self._remove_intersections()
            self._draw_intersections(intersections=self._get_intersections(
                aid_line_orientations=[self.__orientation] * len(self.__aid_lines),
                aid_line_positions=[a.pos for a in self.__aid_lines.keys()]
            ))
        if self._aid_line_config.show_label:
            self._draw_label(aid_line_div=aid_line, orientation=self.__orientation)

    def _on_dragged(self, sender, pos_change):
        """
        Called when the an axis was dragged.

        :type sender: object
        :type pos_change: tuple[float, float]
        :return: The pos that the dragged aid line would have without the tick snapping.
        :rtype: tuple[float, float]
        """
        # TODO: If tick snapping is on: The pos_change can be to small to reach the threshold to come to the next tick. This should be fixed.
        # Check if the axis or the aid line got this event.
        if not isinstance(sender, InteractiveDivNode):
            axis = sender
            if axis not in self.__newly_added_aid_lines:
                return
            aid_line = self.__newly_added_aid_lines[axis]
        else:
            aid_line = sender

        # Check on which axis the add line is:
        # Add the position change according to the type of aid line.
        if self.__orientation is Orientation.Horizontal:
            temp_pos = aid_line.pos[0], aid_line.pos[1] + pos_change[1]
            if aid_line in self.__newly_added_aid_line_pos:
                self.__newly_added_aid_line_pos[aid_line] = self.__newly_added_aid_line_pos[aid_line][0], self.__newly_added_aid_line_pos[aid_line][1] + pos_change[1]
                y = self.__newly_added_aid_line_pos[aid_line][1]
            else:
                y = aid_line.drag_start_pos[1] + aid_line.last_absolute_drag_offset[1]
            aid_line_pos = self._check_for_snapping(
                pos=(aid_line.pos[0], y),
                orientation=self.__orientation
            )
        else:
            temp_pos = aid_line.pos[0] + pos_change[0], aid_line.pos[1]
            if aid_line in self.__newly_added_aid_line_pos:
                self.__newly_added_aid_line_pos[aid_line] = self.__newly_added_aid_line_pos[aid_line][0] + pos_change[0], self.__newly_added_aid_line_pos[aid_line][1]
                x = self.__newly_added_aid_line_pos[aid_line][0]
            else:
                x = aid_line.drag_start_pos[0] + aid_line.last_absolute_drag_offset[0]
            aid_line_pos = self._check_for_snapping(
                pos=(x, aid_line.pos[1]),
                orientation=self.__orientation
            )

        new_pos, in_border_area = self._check_aid_line_pos(aid_line_pos, self.__orientation)
        aid_line.pos = new_pos if new_pos else aid_line_pos

        if self._intersection_config.show_intersections:
            self._remove_intersections()
            self._draw_intersections(intersections=self._get_intersections(
                aid_line_orientations=[self.__orientation] * len(self.__aid_lines),
                aid_line_positions=[a.pos for a in self.__aid_lines.keys()]
            ))
        if self._aid_line_config.show_label:
            self._draw_label(aid_line_div=aid_line, orientation=self.__orientation)

        return temp_pos

    def _on_drag_ended(self, sender, pos_change):
        """
        Called when a drag on an axis has ended.

        :type sender: ChartAxis
        :type pos_change: tuple[float, float]
        """
        drag_pos = self._on_dragged(sender=sender, pos_change=pos_change)
        # Check if the axis or the aid line got this event.
        if not isinstance(sender, InteractiveDivNode):
            axis = sender
            aid_line = self.__newly_added_aid_lines.pop(axis)
            self.__newly_added_aid_line_pos.pop(aid_line)
        else:
            aid_line = sender

        new_pos, in_border_area = self._check_aid_line_pos(drag_pos, self.__orientation)
        if in_border_area:
            self.__aid_lines.pop(aid_line, None)
            aid_line.unlink(True)
            if self._intersection_config.show_intersections:
                self._remove_intersections()
                self._draw_intersections(intersections=self._get_intersections(
                    aid_line_orientations=[self.__orientation] * len(self.__aid_lines),
                    aid_line_positions=[a.pos for a in self.__aid_lines.keys()]
                ))

            StudyLog.get_instance().write_event_log('An {} axis drag aid line in chart {} was deleted.'.format(
                'horizontal' if self.__orientation is Orientation.Horizontal else 'vertical', self._chart.view_id))

    def _on_step(self, direction, steps=1, axis_index=0, aid_line_index=0):
        """
        Moves the aid line a number of steps (to the ticks of the axis) in a given direction.

        :param direction: The direction in which the steps should be taken. -1 for backward and 1 for forward.
        :type direction: int
        :param steps: The number of steps the aid line should be move forward.
        :type steps: int
        :param axis_index: The index of the axis that the step should be calculated with.
        :type axis_index: int
        :param aid_line_index: The index of the aid line the stepping should effect.
        :type aid_line_index: int
        """
        if len(self.__aid_lines) == 0:
            return
        aid_line = self.__aid_lines.keys()[aid_line_index]

        min_offset = steps if direction == -1 else 0
        max_offset = 0 if direction == -1 else -steps

        if self.__orientation is Orientation.Horizontal:
            coordinate = 1
            axis = self._chart.vertical_axis_views.values()[axis_index]
        else:
            coordinate = 0
            axis = self._chart.horizontal_axis_views.values()[axis_index]

        index = self._get_next_tick_index(tick_positions=axis.tick_positions, aid_line_pos=aid_line.pos, coordinate=coordinate)

        if 0 + min_offset <= index < len(axis.tick_positions) + max_offset:
            if self.__orientation is Orientation.Horizontal:
                aid_line.pos = aid_line.pos[0], axis.tick_positions[index + direction * steps]
            else:
                aid_line.pos = axis.tick_positions[index + direction * steps], aid_line.pos[1]

        if self._intersection_config.show_intersections:
            self._remove_intersections()
            self._draw_intersections(intersections=self._get_intersections(
                aid_line_orientations=[self.__orientation] * len(self.__aid_lines),
                aid_line_positions=[a.pos for a in self.__aid_lines.keys()]
            ))
        if self._aid_line_config.show_label:
            self._draw_label(aid_line_div=aid_line, orientation=self.__orientation)

    def reset(self):
        """
        Resets this aid line controller.
        """
        for aid_line in self.__aid_lines.iterkeys():
            aid_line.unlink(True)
        self.__aid_lines.clear()
        self.__newly_added_aid_lines.clear()
        self.__newly_added_aid_line_pos.clear()
        self._remove_intersections()

    def _on_step_forward(self, steps=1, axis_index=0, aid_line_index=0):
        """
        Moves the aid line a number of steps (to the ticks of the axis) forward.

        :param steps: The number of steps the aid line should be move forward.
        :type steps: int
        :param axis_index: The index of the axis that the step should be calculated with.
        :type axis_index: int
        :param aid_line_index: The index of the aid line the stepping should effect.
        :type aid_line_index: int
        """
        self._on_step(direction=1, steps=steps, axis_index=axis_index, aid_line_index=aid_line_index)

    def _on_step_backward(self, steps=1, axis_index=0, aid_line_index=0):
        """
        Moves the aid line a number of steps (to the ticks of the axis) backward.

        :param steps: The number of steps the aid line should be move backward.
        :type steps: int
        :param axis_index: The index of the axis that the step should be calculated with.
        :type axis_index: int
        :param aid_line_index: The index of the aid line the stepping should effect.
        :type aid_line_index: int
        """
        self._on_step(direction=-1, steps=steps, axis_index=axis_index, aid_line_index=aid_line_index)

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
        removed, data_objects = super(AxisDragAidLine, self)._on_selection_set_changed(sender, selection_set_id, selection_diff)
        if not removed:
            return

        self._draw_intersections(intersections=self._get_intersections(
            aid_line_orientations=[self.__orientation] * len(self.__aid_lines),
            aid_line_positions=[a.pos for a in self.__aid_lines.keys()],
            data_object_nodes={k: self._chart.data_object_nodes[k] for k, do in self._chart.data_objects.iteritems() if k in data_objects}
        ))
