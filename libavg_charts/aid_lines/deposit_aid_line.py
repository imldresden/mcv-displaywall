from libavg import avg
from libavg.avg import CursorEvent
from libavg_charts.aid_lines.orthogonal_aid_line import OrthogonalAidLine
from libavg_charts.axis.chart_axis_enums import Orientation
from logging_base.study_logging import StudyLog


class DepositAidLine(OrthogonalAidLine):
    ADD_AID_LINE = "addAidLine"
    DELETE_AID_LINE = "deleteAidLine"

    def __init__(self, **kwargs):
        """
        :param kwargs: Other parameters for the base.
        """
        super(DepositAidLine, self).__init__(**kwargs)

        # list of tuples: tuple[horizontal_aid_line, vertical_aid_line]
        self._aid_lines = []

        self._horizontal_aid_lines = []
        self._vertical_aid_lines = []

        self._horizontal_aid_line_drag_start_pos = {}
        self._vertical_aid_line_drag_start_pos = {}

        self.bind(self.ADD_AID_LINE, self._on_add_aid_line)
        self.bind(self.DELETE_AID_LINE, self._on_delete_aid_line)

    def _on_step_forward(self, steps=1, axis_index=0):
        """
        Moves the aid line a number of steps (to the ticks of the axis) forward.

        :param steps: The number of steps the aid line should be move forward.
        :type steps: int
        :param axis_index: The index of the axis that the step should be calculated with.
        :type axis_index: int
        """
        pass

    def _on_step_backward(self, steps=1, axis_index=0):
        """
        Moves the aid line a number of steps (to the ticks of the axis) backward.

        :param steps: The number of steps the aid line should be move backward.
        :type steps: int
        :param axis_index: The index of the axis that the step should be calculated with.
        :type axis_index: int
        """
        pass

    def _on_add_aid_line(self, pos):
        """
        Creates an aid line at the given pos.

        :param pos: The pos to create a aid line on.
        :type pos: tuple[float, float]
        """
        if not (self._aid_line_area[0] <= pos[0] <= self._aid_line_area[2] and
                self._aid_line_area[1] <= pos[1] <= self._aid_line_area[3]):
            return

        h_aid_line = self._draw_horizontal_aid_line(pos=pos)
        v_aid_line = self._draw_vertical_aid_line(pos=pos)

        if h_aid_line:
            self._horizontal_aid_lines.append(h_aid_line)
        if v_aid_line:
            self._vertical_aid_lines.append(v_aid_line)

        # Draw the intersections and the labels.
        if self._intersection_config.show_intersections:
            aid_line_values = {a.pos: Orientation.Horizontal for a in self._horizontal_aid_lines}
            aid_line_values.update({a.pos : Orientation.Vertical for a in self._vertical_aid_lines})
            intersections = self._get_intersections(
                aid_line_orientations=aid_line_values.values(),
                aid_line_positions=aid_line_values.keys()
            )
            self._remove_intersections()
            self._draw_intersections(intersections=intersections)
        if self._aid_line_config.show_label:
            if h_aid_line:
                self._draw_label(aid_line_div=h_aid_line, orientation=Orientation.Horizontal)
            if v_aid_line:
                self._draw_label(aid_line_div=v_aid_line, orientation=Orientation.Vertical)

        StudyLog.get_instance().write_event_log('An desposite aid line was created.')

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
        for i in range(len(self._horizontal_aid_lines)):
            horizontal_aid_line = self._horizontal_aid_lines[i]
            line_node = horizontal_aid_line.getChild(0)
            aid_line_size = (
                line_node.pos1[0],
                horizontal_aid_line.pos[1] - line_node.strokewidth / 2,
                line_node.pos2[0],
                horizontal_aid_line.pos[1] + line_node.strokewidth / 2
            )
            if aid_line_size[0] <= pos[0] <= aid_line_size[2] and aid_line_size[1] <= pos[1] <= aid_line_size[3]:
                if i not in aid_lines_to_remove:
                    aid_lines_to_remove.append(i)

        for i in range(len(self._vertical_aid_lines)):
            vertical_aid_line = self._vertical_aid_lines[i]
            line_node = vertical_aid_line.getChild(0)
            aid_line_size = (
                vertical_aid_line.pos[0] - line_node.strokewidth / 2,
                line_node.pos1[1],
                vertical_aid_line.pos[0] + line_node.strokewidth / 2,
                line_node.pos2[1]
            )
            if aid_line_size[0] <= pos[0] <= aid_line_size[2] and aid_line_size[1] <= pos[1] <= aid_line_size[3]:
                if i not in aid_lines_to_remove:
                    aid_lines_to_remove.append(i)

        removed = 0
        for i in aid_lines_to_remove:
            i -= removed
            yet_removed = 0

            if 0 <= i < len(self._horizontal_aid_lines):
                yet_removed = 1
                self._horizontal_aid_lines.pop(i).unlink(True)
            if i < len(self._vertical_aid_lines):
                yet_removed = 1
                self._vertical_aid_lines.pop(i).unlink(True)

            removed -= yet_removed

        if self._intersection_config.show_intersections:
            self._remove_intersections()
            aid_line_values = {a.pos: Orientation.Horizontal for a in self._horizontal_aid_lines}
            aid_line_values.update({a.pos : Orientation.Vertical for a in self._vertical_aid_lines})
            self._draw_intersections(self._get_intersections(
                aid_line_orientations=aid_line_values.values(),
                aid_line_positions=aid_line_values.keys()
            ))

        StudyLog.get_instance().write_event_log('An desposite aid line was deleted.')

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
        aid_line = super(DepositAidLine, self)._draw_horizontal_aid_line(pos, with_outer)
        aid_line.subscribe(avg.Node.CURSOR_DOWN, self._on_aid_line_cursor_down)
        aid_line.start_listening(
            drag_started=self._on_aid_line_drag_started,
            dragged=self._on_aid_line_drag,
            drag_ended=self._on_aid_line_drag_end
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
        aid_line = super(DepositAidLine, self)._draw_vertical_aid_line(pos, with_outer)
        aid_line.subscribe(avg.Node.CURSOR_DOWN, self._on_aid_line_cursor_down)
        aid_line.start_listening(
            drag_started=self._on_aid_line_drag_started,
            dragged=self._on_aid_line_drag,
            drag_ended=self._on_aid_line_drag_end
        )

        return aid_line

    def _on_aid_line_cursor_down(self, event):
        """
        Called if a drag on an aid line has started.

        :type event: CursorEvent
        """
        sender = event.node
        if sender in self._horizontal_aid_lines:
            index = self._horizontal_aid_lines.index(sender)
        else:  # sender in self._vertical_aid_lines:
            index = self._vertical_aid_lines.index(sender)

        rel_event_pos = self._chart.getRelPos(event.pos)
        if index < len(self._horizontal_aid_lines) and index not in self._horizontal_aid_line_drag_start_pos:
            self._horizontal_aid_line_drag_start_pos[index] = 0, rel_event_pos[1]
        if index < len(self._vertical_aid_lines) and index not in self._vertical_aid_line_drag_start_pos:
            self._vertical_aid_line_drag_start_pos[index] = rel_event_pos[0], 0

    def _on_aid_line_drag_started(self, sender):
        """
        Called when a drag on an axis has started.

        :type sender: InteractiveDivNode
        """
        if sender in self._horizontal_aid_lines:
            index = self._horizontal_aid_lines.index(sender)
        else:  # sender in self._vertical_aid_lines:
            index = self._vertical_aid_lines.index(sender)

        if index < len(self._horizontal_aid_lines) and index in self._horizontal_aid_line_drag_start_pos:
            self._horizontal_aid_lines[index].pos = self._horizontal_aid_line_drag_start_pos[index]
            self._horizontal_aid_lines[index].drag_start_pos = self._horizontal_aid_line_drag_start_pos[index]
        if index < len(self._vertical_aid_lines) and index in self._vertical_aid_line_drag_start_pos:
            self._vertical_aid_lines[index].pos = self._vertical_aid_line_drag_start_pos[index]
            self._vertical_aid_lines[index].drag_start_pos = self._vertical_aid_line_drag_start_pos[index]

    def _on_aid_line_drag(self, sender, pos_change):
        """
        Called if an aid line was dragged.

        :param pos_change: The offset from the last pos.
        :type pos_change: tuple[float, float]
        """
        if sender in self._horizontal_aid_lines:
            index = self._horizontal_aid_lines.index(sender)
            pos_change = self._horizontal_aid_lines[index].last_absolute_drag_offset
        else:  # sender in self._vertical_aid_lines:
            index = self._vertical_aid_lines.index(sender)
            pos_change = self._vertical_aid_lines[index].last_absolute_drag_offset

        if index < len(self._horizontal_aid_lines):
            new_pos = self._check_for_snapping(
                pos=(self._horizontal_aid_lines[index].pos[0], self._horizontal_aid_lines[index].drag_start_pos[1] + pos_change[1]),
                orientation=Orientation.Horizontal
            )
            pos, _ = self._check_aid_line_pos(aid_line_pos=new_pos, orientation=Orientation.Horizontal)
            self._horizontal_aid_lines[index].pos = pos or new_pos

            if self._aid_line_config.show_label:
                self._draw_label(aid_line_div=self._horizontal_aid_lines[index], orientation=Orientation.Horizontal)
        if index < len(self._vertical_aid_lines):
            new_pos = self._check_for_snapping(
                pos=(self._vertical_aid_lines[index].drag_start_pos[0] + pos_change[0], self._vertical_aid_lines[index].pos[1]),
                orientation=Orientation.Vertical
            )
            pos, _ = self._check_aid_line_pos(aid_line_pos=new_pos, orientation=Orientation.Vertical)
            self._vertical_aid_lines[index].pos = pos or new_pos

            if self._aid_line_config.show_label:
                self._draw_label(aid_line_div=self._vertical_aid_lines[index], orientation=Orientation.Vertical)

        aid_line_values = {a.pos: Orientation.Horizontal for a in self._horizontal_aid_lines}
        aid_line_values.update({a.pos : Orientation.Vertical for a in self._vertical_aid_lines})
        intersections = self._get_intersections(
            aid_line_orientations=aid_line_values.values(),
            aid_line_positions=aid_line_values.keys()
        )
        self._remove_intersections()
        self._draw_intersections(intersections=intersections)

    def _on_aid_line_drag_end(self, sender, pos_change):
        """
        Called when a drag on an axis has ended.

        :type sender: InteractiveDivNode
        :type pos_change: tuple[float, float]
        """
        self._on_aid_line_drag(sender=sender, pos_change=pos_change)

        if sender in self._horizontal_aid_lines:
            index = self._horizontal_aid_lines.index(sender)
        else:  # sender in self._vertical_aid_lines:
            index = self._vertical_aid_lines.index(sender)

        if index < len(self._horizontal_aid_lines) and index in self._horizontal_aid_line_drag_start_pos:
            self._horizontal_aid_line_drag_start_pos.pop(index)
        if index < len(self._vertical_aid_lines) and index in self._vertical_aid_line_drag_start_pos:
            self._vertical_aid_line_drag_start_pos.pop(index)

        orientation = Orientation.Horizontal if sender in self._horizontal_aid_lines else Orientation.Vertical
        new_pos, in_border_area = self._check_aid_line_pos(sender.pos, orientation)
        if in_border_area:
            if orientation is Orientation.Horizontal:
                self._on_delete_aid_line((self._aid_line_area[0] + (self._aid_line_area[2] - self._aid_line_area[0]) / 2, sender.pos[1]))
            else:
                self._on_delete_aid_line((sender.pos[0], self._aid_line_area[1] + (self._aid_line_area[3] - self._aid_line_area[1]) / 2))

    def reset(self):
        """
        Resets this aid line controller.
        """
        for aid_line in self._horizontal_aid_lines:
            aid_line.unlink(True)
        for aid_line in self._vertical_aid_lines:
            aid_line.unlink(True)
        self._horizontal_aid_lines = []
        self._vertical_aid_lines = []
        self._remove_intersections()

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
        removed, data_objects = super(DepositAidLine, self)._on_selection_set_changed(sender, selection_set_id, selection_diff)
        if not removed:
            return

        aid_line_values = {a.pos: Orientation.Horizontal for a in self._horizontal_aid_lines}
        aid_line_values.update({a.pos : Orientation.Vertical for a in self._vertical_aid_lines})
        intersections = self._get_intersections(
            aid_line_orientations=aid_line_values.values(),
            aid_line_positions=aid_line_values.keys(),
            data_object_nodes={k: self._chart.data_object_nodes[k] for k, do in self._chart.data_objects.iteritems() if k in data_objects}
        )
        self._draw_intersections(intersections=intersections)
