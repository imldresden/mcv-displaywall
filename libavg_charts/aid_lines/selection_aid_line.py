from libavg_charts.aid_lines.cursor_aid_line import CursorAidLine
from libavg_charts.aid_lines.helper.selection_method_holder import SelectionMethodHolder, SelectionTypes
from libavg import avg
from libavg.avg import CursorEvent
from libavg_charts.configurations.selection_line_configuration import SelectionLineConfiguration


class SelectionAidLine(CursorAidLine):
    _DATA_OBJECTS_SELECTED = "dataObjectsSelected"

    def __init__(self, selection_line_config=None, **kwargs):
        """
        :param selection_line_config: The container that holds all values necessary for selections.
        :type selection_line_config: SelectionLineConfiguration
        :param kwargs: Other parameters for the base.
        """
        self._selection_line_config = selection_line_config if selection_line_config else SelectionLineConfiguration()
        super(SelectionAidLine, self).__init__(**kwargs)

        self._recognition_div.subscribe(avg.Node.CURSOR_DOWN, self.__on_mouse_down)
        # TODO: Add this directly to the event.
        self._recognition_div.subscribe(avg.Node.CURSOR_UP, self.__on_mouse_up)

        self.__horizontal_selection_line = None
        self.__vertical_selection_line = None

    @property
    def selection_line_config(self):
        """
        :rtype: SelectionLineConfiguration
        """
        return self._selection_line_config

    @selection_line_config.setter
    def selection_line_config(self, selection_config):
        """
        :type selection_config: SelectionLineConfiguration
        """
        self._selection_line_config = selection_config

    def __on_mouse_down(self, event):
        """
        Called when the cursor dispatched a down event. It will draw the other aid lines for the selection.

        :type event: CursorEvent
        """
        if self._aid_line_movement_block:
            return

        pos = (self._vertical_aid_line.pos[0] if self._vertical_aid_line else 0,
               self._horizontal_aid_line.pos[1] if self._horizontal_aid_line else 0)
        self.__horizontal_selection_line = self._draw_horizontal_selection_line(pos=pos)
        self.__vertical_selection_line = self._draw_vertical_selection_line(pos=pos)

    def __on_mouse_up(self, event):
        """
        Called when the cursor dispatches an up event. It will select a area between the given aid lines.
        """
        if self._aid_line_movement_block:
            super(SelectionAidLine, self)._on_mouse_up(event=event)
            self._on_mouse_move(event=event)
            return

        selection = self._get_selection()
        if self.__horizontal_selection_line:
            self.__horizontal_selection_line.unlink(True)
        self.__horizontal_selection_line = None
        if self.__vertical_selection_line:
            self.__vertical_selection_line.unlink(True)
        self.__vertical_selection_line = None

        self.dispatch(self._DATA_OBJECTS_SELECTED, sender=self, selected_data=selection)

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
        aid_line = super(SelectionAidLine, self)._draw_horizontal_aid_line(pos, False)
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
        aid_line = super(SelectionAidLine, self)._draw_vertical_aid_line(pos, False)
        aid_line.sensitive = True
        return aid_line

    def _draw_horizontal_selection_line(self, pos):
        """
        Draws a horizontal selection line.

        :param pos: The position of the line.
        :type pos: tuple[int, int]
        :return: The created selection line.
        :rtype: DivNode
        """
        selection_line = avg.DivNode(
            parent=self._aid_lines_div,
            pos=(0, pos[1])
        )
        avg.LineNode(
            parent=selection_line,
            pos1=(self._aid_line_area[0] - self._selection_line_config.extra_length, 0),
            pos2=(self._aid_line_area[2] + self._selection_line_config.extra_length, 0),
            color=self._selection_line_config.color,
            strokewidth=self._selection_line_config.width,
            sensitive=False
        )
        return selection_line

    def _draw_vertical_selection_line(self, pos):
        """
        Draws a vertical selection line.

        :param pos: The position of the line.
        :type pos: tuple[int, int]
        :return: The created selection line.
        :rtype: DivNode
        """
        selection_line = avg.DivNode(
            parent=self._aid_lines_div,
            pos=(pos[0], 0)
        )
        avg.LineNode(
            parent=selection_line,
            pos1=(0, self._aid_line_area[1] - self._selection_line_config.extra_length),
            pos2=(0, self._aid_line_area[3] + self._selection_line_config.extra_length),
            color=self._selection_line_config.color,
            strokewidth=self._selection_line_config.width,
            sensitive=False
        )
        return selection_line

    def _get_selection(self):
        """
        Calculates the selection.

        :return: The selected nodes.
        :rtype: dict[DataObject, Node]
        """
        selection = {}
        if self.__horizontal_selection_line and self.__vertical_selection_line:
            selection = SelectionMethodHolder.get_selection_from_data_objects(
                diagram_type=type(self._chart),
                selection_type=SelectionTypes.Rectangle,
                data_object_nodes=self._chart.data_object_nodes,
                value1=(self.__vertical_selection_line.pos[0], self.__horizontal_selection_line.pos[1]),
                value2=(self._vertical_aid_line.pos[0], self._horizontal_aid_line.pos[1])
            )
        elif self.__horizontal_selection_line:
            selection = SelectionMethodHolder.get_selection_from_data_objects(
                diagram_type=type(self._chart),
                selection_type=SelectionTypes.HorizontalLine,
                data_object_nodes=self._chart.data_object_nodes,
                value1=self.__horizontal_selection_line.pos[1],
                value2=self._horizontal_aid_line.pos[1]
            )
        elif self.__vertical_selection_line:
            selection = SelectionMethodHolder.get_selection_from_data_objects(
                diagram_type=type(self._chart),
                selection_type=SelectionTypes.VerticalLine,
                data_object_nodes=self._chart.data_object_nodes,
                value1=self.__vertical_selection_line.pos[0],
                value2=self._vertical_aid_line.pos[0]
            )

        selection = [self._chart.data_objects[key] for key in selection.iterkeys()]
        return selection

    def start_listening(self, data_objects_selected=None):
        """
        Registers a callback to listen to changes or events of this selection aid line controller. Listeners can register to any number of the
        provided events. For the required structure of the callbacks see below.

        :param data_objects_selected: Called when a subset of the data was selected through this controller.
        :type data_objects_selected: function(sender:SelectionAidLine, selected_data:list[DataObject])
        """
        self.bind(self._DATA_OBJECTS_SELECTED, data_objects_selected)

    def stop_listening(self, data_objects_selected=None):
        """
        Stops listening to an event the listener has registered to previously. The provided callback needs to be the
        same that was used to listen to the event in the fist place.

        :param data_objects_selected: Called when a subset of the data was selected through this controller.
        :type data_objects_selected: function(sender:SelectionAidLine, selected_data:list[DataObject])
        """
        self.unbind(self._DATA_OBJECTS_SELECTED, data_objects_selected)
