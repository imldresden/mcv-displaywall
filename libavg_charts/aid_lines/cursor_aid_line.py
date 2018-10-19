from libavg import avg
from libavg.avg import CursorEvent, DivNode
from libavg_charts.aid_lines.helper.intersection_method_holder import IntersectionMethodHolder
from libavg_charts.aid_lines.orthogonal_aid_line import OrthogonalAidLine
from libavg_charts.axis.chart_axis_enums import Orientation


class CursorAidLine(OrthogonalAidLine):
    STEP_FORWARD_HORIZONTAL = "stepForwardHorizontal"
    STEP_BACKWARD_HORIZONTAL = "stepBackwardHorizontal"
    STEP_FORWARD_VERTICAL = "stepForwardVertical"
    STEP_BACKWARD_VERTICAL = "stepBackwardVertical"

    def __init__(self, **kwargs):
        """
        :param kwargs: Other parameters for the base.
        """
        super(CursorAidLine, self).__init__(**kwargs)

        size = self._aid_line_area[2] - self._aid_line_area[0], self._aid_line_area[3] - self._aid_line_area[1]
        self._recognition_div = avg.DivNode(
            parent=self._internal_div,
            pos=(self._aid_line_area[0], self._aid_line_area[1]),
            size=size
        )
        self._recognition_div.subscribe(avg.Node.CURSOR_OVER, self._on_mouse_enter)
        self._recognition_div.subscribe(avg.Node.CURSOR_OUT, self._on_mouse_leave)
        self._recognition_div.subscribe(avg.Node.CURSOR_MOTION, self._on_mouse_move)
        self._recognition_div.subscribe(avg.Node.CURSOR_UP, self._on_mouse_up)

        self._vertical_aid_line = None
        self._horizontal_aid_line = None

        self._aid_line_movement_block = False
        self.bind(self.STEP_FORWARD_HORIZONTAL, lambda steps=1, axis_index=0: self._on_step(direction=1, steps=steps, axis_index=axis_index, horizontal=True, vertical=False))
        self.bind(self.STEP_BACKWARD_HORIZONTAL, lambda steps=1, axis_index=0: self._on_step(direction=-1, steps=steps, axis_index=axis_index, horizontal=True, vertical=False))
        self.bind(self.STEP_FORWARD_VERTICAL, lambda steps=1, axis_index=0: self._on_step(direction=1, steps=steps, axis_index=axis_index, horizontal=False, vertical=True))
        self.bind(self.STEP_BACKWARD_VERTICAL, lambda steps=1, axis_index=0: self._on_step(direction=-1, steps=steps, axis_index=axis_index, horizontal=False, vertical=True))

    def _on_mouse_enter(self, event):
        """
        Called if cursor enters the aid line area. It creates a new aid line.

        :type event: CursorEvent
        """
        rel_event_pos = self._chart.getRelPos(event.pos)

        self._horizontal_aid_line = self._draw_horizontal_aid_line(pos=rel_event_pos)
        self._vertical_aid_line = self._draw_vertical_aid_line(pos=rel_event_pos)

        # Draw the intersections and labels.
        if self._intersection_config.show_intersections:
            aid_lines = {Orientation.Horizontal: self._horizontal_aid_line, Orientation.Vertical: self._vertical_aid_line}
            intersections = self._get_intersections(
                aid_line_orientations=[o for o, a in aid_lines.items() if a is not None],
                aid_line_positions=[a.pos for a in aid_lines.values() if a is not None]
            )
            self._remove_intersections()
            self._draw_intersections(intersections=intersections)
        if self._aid_line_config.show_label:
            if self._horizontal_aid_line:
                self._draw_label(aid_line_div=self._horizontal_aid_line, orientation=Orientation.Horizontal)
            if self._vertical_aid_line:
                self._draw_label(aid_line_div=self._vertical_aid_line, orientation=Orientation.Vertical)

    def _on_mouse_leave(self, event):
        """
        Called when the cursor leaves the aid line area. It will delete the aid lines.

        :type event: CursorEvent
        """
        if self._horizontal_aid_line:
            self._horizontal_aid_line.unlink(True)
        self._horizontal_aid_line = None
        if self._vertical_aid_line:
            self._vertical_aid_line.unlink(True)
        self._vertical_aid_line = None

        if self._intersection_config.show_intersections:
            aid_lines = {Orientation.Horizontal: self._horizontal_aid_line, Orientation.Vertical: self._vertical_aid_line}
            self._draw_intersections(self._get_intersections(
                aid_line_orientations=[o for o, a in aid_lines.items() if a is not None],
                aid_line_positions=[a.pos for a in aid_lines.values() if a is not None]
            ))

    def _on_mouse_move(self, event):
        """
        Called when the cursor moves in the aid line area. It will move the aid lines.

        :type event: CursorEvent
        """
        if self._aid_line_movement_block:
            return

        rel_event_pos = self._chart.getRelPos(event.pos)

        has_changed = not self._use_tick_snapping
        if self._horizontal_aid_line:
            new_pos = self._check_for_snapping(
                pos=(0, rel_event_pos[1]),
                orientation=Orientation.Horizontal
            )
            old_pos = self._horizontal_aid_line.pos
            self._horizontal_aid_line.pos = new_pos
            has_changed = old_pos[1] != self._horizontal_aid_line.pos[1] or has_changed

        if self._vertical_aid_line:
            new_pos = self._check_for_snapping(
                pos=(rel_event_pos[0], 0),
                orientation=Orientation.Vertical
            )
            old_pos = self._vertical_aid_line.pos
            self._vertical_aid_line.pos = new_pos
            has_changed = old_pos[0] != self._vertical_aid_line.pos[0] or has_changed

        # Draw the intersections and the labels.
        if self._intersection_config.show_intersections and has_changed:
            aid_lines = {Orientation.Horizontal: self._horizontal_aid_line, Orientation.Vertical: self._vertical_aid_line}
            intersections = self._get_intersections(
                aid_line_orientations=[o for o, a in aid_lines.items() if a is not None],
                aid_line_positions=[a.pos for a in aid_lines.values() if a is not None]
            )
            self._remove_intersections()
            self._draw_intersections(intersections=intersections)
        if self._aid_line_config.show_label and has_changed:
            if self._horizontal_aid_line:
                self._draw_label(aid_line_div=self._horizontal_aid_line, orientation=Orientation.Horizontal)
            if self._vertical_aid_line:
                self._draw_label(aid_line_div=self._vertical_aid_line, orientation=Orientation.Vertical)

    def _on_mouse_up(self, event):
        """
        Called when the cursor dispatches an up event. It will remove the movement block from the aid lines.
        """
        self._aid_line_movement_block = False

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
        aid_line = super(CursorAidLine, self)._draw_horizontal_aid_line(pos, False)
        aid_line.sensitive = True
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
        aid_line = super(CursorAidLine, self)._draw_vertical_aid_line(pos, False)
        aid_line.sensitive = True
        return aid_line

    def _on_step(self, direction, horizontal, vertical, steps=1, axis_index=0):
        """
        Moves the aid line a number of steps (to the ticks of the axis) in a given direction.

        :param direction: The direction in which the steps should be taken. -1 for backward and 1 for forward.
        :type direction: int
        :param horizontal: Should the step be used on the horizontal aid line?
        :type horizontal: bool
        :param vertical: Should the step be used on the vertical aid line?
        :type vertical: bool
        :param steps: The number of steps the aid line should be move forward.
        :type steps: int
        :param axis_index: The index of the axis that the step should be calculated with.
        :type axis_index: int
        """
        self._aid_line_movement_block = True

        min_offset = steps if direction == -1 else 0
        max_offset = 0 if direction == -1 else -steps

        if horizontal and self._horizontal_aid_line:
            axis = self._chart.vertical_axis_views.values()[axis_index]
            aid_line_pos = self._horizontal_aid_line.pos[0] - axis.pos[0], self._horizontal_aid_line.pos[1] - axis.pos[1]
            index = self._get_next_tick_index(tick_positions=axis.tick_positions, aid_line_pos=aid_line_pos, coordinate=1)

            if 0 + min_offset <= index < len(axis.tick_positions) + max_offset:
                self._horizontal_aid_line.pos = self._horizontal_aid_line.pos[0], axis.tick_positions[index + direction * steps] + axis.pos[1]

            if self._aid_line_config.show_label:
                self._draw_label(aid_line_div=self._horizontal_aid_line, orientation=Orientation.Horizontal)
        if vertical and self._vertical_aid_line:
            axis = self._chart.horizontal_axis_views.values()[axis_index]
            aid_line_pos = self._vertical_aid_line.pos[0] - axis.pos[0], self._vertical_aid_line.pos[1] - axis.pos[1]
            index = self._get_next_tick_index(tick_positions=axis.tick_positions, aid_line_pos=aid_line_pos, coordinate=0)

            if 0 + min_offset <= index < len(axis.tick_positions) + max_offset:
                self._vertical_aid_line.pos = axis.tick_positions[index + direction * steps] + axis.pos[0], self._vertical_aid_line.pos[1]

            if self._aid_line_config.show_label:
                self._draw_label(aid_line_div=self._vertical_aid_line, orientation=Orientation.Vertical)

        # Draw the intersections and the labels.
        if self._intersection_config.show_intersections:
            aid_lines = {Orientation.Horizontal: self._horizontal_aid_line, Orientation.Vertical: self._vertical_aid_line}
            intersections = self._get_intersections(
                aid_line_orientations=[o for o, a in aid_lines.items() if a is not None],
                aid_line_positions=[a.pos for a in aid_lines.values() if a is not None]
            )
            self._remove_intersections()
            self._draw_intersections(intersections=intersections)

    def _on_step_forward(self, steps=1, axis_index=0):
        """
        Moves the aid line a number of steps (to the ticks of the axis) forward.

        :param steps: The number of steps the aid line should be move forward.
        :type steps: int
        :param axis_index: The index of the axis that the step should be calculated with.
        :type axis_index: int
        """
        self._on_step(direction=1, steps=steps, axis_index=axis_index, horizontal=True, vertical=True)

    def _on_step_backward(self, steps=1, axis_index=0):
        """
        Moves the aid line a number of steps (to the ticks of the axis) backward.

        :param steps: The number of steps the aid line should be move backward.
        :type steps: int
        :param axis_index: The index of the axis that the step should be calculated with.
        :type axis_index: int
        """
        self._on_step(direction=-1, steps=steps, axis_index=axis_index, horizontal=True, vertical=True)

    def reset(self):
        """
        Resets this aid line controller.
        """
        self._horizontal_aid_line.unlink(True)
        self._vertical_aid_line.unlink(True)
        self._horizontal_aid_line = None
        self._vertical_aid_line = None
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
        removed, data_objects = super(CursorAidLine, self)._on_selection_set_changed(sender, selection_set_id, selection_diff)
        if not removed:
            return

        aid_lines = {Orientation.Horizontal: self._horizontal_aid_line, Orientation.Vertical: self._vertical_aid_line}
        intersections = self._get_intersections(
            aid_line_orientations=[o for o, a in aid_lines.items() if a is not None],
            aid_line_positions=[a.pos for a in aid_lines.values() if a is not None]
        )
        self._draw_intersections(intersections=intersections)
