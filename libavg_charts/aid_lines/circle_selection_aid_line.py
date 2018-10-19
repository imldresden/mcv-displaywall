from libavg_charts.aid_lines.aid_line_controller_base import AidLineControllerBase
from libavg import avg
from libavg.avg import CursorEvent, DivNode
from libavg_charts.aid_lines.helper.selection_method_holder import SelectionMethodHolder, SelectionTypes


class CircleSelectionAidLine(AidLineControllerBase):
    _DATA_OBJECTS_SELECTED = "dataObjectsSelected"

    def __init__(self, **kwargs):
        """
        :param kwargs: Other parameters for the base.
        """
        super(CircleSelectionAidLine, self).__init__(**kwargs)

        size = self._aid_line_area[2] - self._aid_line_area[0], self._aid_line_area[3] - self._aid_line_area[1]
        self._recognition_div = avg.DivNode(
            parent=self._internal_div,
            pos=(self._aid_line_area[0], self._aid_line_area[1]),
            size=size
        )
        self._recognition_div.subscribe(avg.Node.CURSOR_OVER, self.__on_mouse_enter)
        self._recognition_div.subscribe(avg.Node.CURSOR_OUT, self.__on_mouse_leave)
        self._recognition_div.subscribe(avg.Node.CURSOR_MOTION, self.__on_mouse_move)
        self._recognition_div.subscribe(avg.Node.CURSOR_UP, self.__on_mouse_up)

        self.__circle_selection_line = None

    def __on_mouse_enter(self, event):
        """
        Called if cursor enters the aid line area. It creates a new aid line.

        :type event: CursorEvent
        """
        pos = event.pos[0] - self._chart.pos[0], event.pos[1] - self._chart.pos[1]
        self.__circle_selection_line = self._draw_circle_aid_line(pos=pos)

    def __on_mouse_leave(self, event):
        """
        Called when the cursor leaves the aid line area. It will delete the aid lines.

        :type event: CursorEvent
        """
        if self.__circle_selection_line:
            self.__circle_selection_line.unlink(True)
        self.__circle_selection_line = None

    def __on_mouse_move(self, event):
        """
        Called when the cursor moves in the aid line area. It will move the aid lines.

        :type event: CursorEvent
        """
        pos = event.pos[0] - self._chart.pos[0], event.pos[1] - self._chart.pos[1]

        if self.__circle_selection_line:
            self.__circle_selection_line.pos = pos

    def __on_mouse_up(self, event):
        """
        Called when a cursor up event was recognized. It will get a selection and dispatches it.

        :type event: CursorEvent
        """
        self.dispatch(self._DATA_OBJECTS_SELECTED, sender=self, selected_data=self._get_selection())

    def _draw_circle_aid_line(self, pos):
        """
        Draws a circle aid line.

        :param pos: The position of the cursor.
        :type pos: tuple[int, int]
        :return: The created aid line.
        :rtype: DivNode
        """
        aid_line = avg.DivNode(
            parent=self._aid_lines_div,
            pos=pos
        )
        avg.CircleNode(
            parent=aid_line,
            r=self._aid_line_config.circle_radius,
            color=self._aid_line_config.color,
            strokewidth=self._aid_line_config.width
        )
        return aid_line

    def _get_selection(self):
        """
        Calculates the selection.

        :return: The selected nodes.
        :rtype: dict[str, Node]
        """
        selection = SelectionMethodHolder.get_selection_from_data_objects(
            diagram_type=type(self._chart),
            selection_type=SelectionTypes.Circle,
            data_object_nodes=self._chart.data_object_nodes,
            value1=self.__circle_selection_line.pos,
            value2=self.__circle_selection_line.getChild(0).r
        )
        return selection

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

    def reset(self):
        """
        Resets this aid line controller.
        """
        self.__circle_selection_line.unlink(True)
        self.__circle_selection_line = None
        self._remove_intersections()

    def start_listening(self, data_objects_selected=None):
        """
        Registers a callback to listen to changes or events of this circle selection aid line controller. Listeners can register to any number of the
        provided events. For the required structure of the callbacks see below.

        :param data_objects_selected: Called when a subset of the data was selected through this controller.
        :type data_objects_selected: function(sender:CircleSelectionAidLine, selected_data:dict[str, Node])
        """
        self.bind(self._DATA_OBJECTS_SELECTED, data_objects_selected)

    def stop_listening(self, data_objects_selected=None):
        """
        Stops listening to an event the listener has registered to previously. The provided callback needs to be the
        same that was used to listen to the event in the fist place.

        :param data_objects_selected: Called when a subset of the data was selected through this controller.
        :type data_objects_selected: function(sender:SelectionAidLine, selected_data:dict[str, Node])
        """
        self.unbind(self._DATA_OBJECTS_SELECTED, data_objects_selected)
