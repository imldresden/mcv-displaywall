from libavg_charts.aid_lines.aid_line_controller_base import AidLineControllerBase
from libavg_charts.configurations.selection_line_configuration import SelectionLineConfiguration
from libavg import avg
from libavg.avg import CursorEvent
from selection_ctrl.selection_lasso import SelectionLasso
from libavg_charts.aid_lines.helper.selection_method_holder import SelectionMethodHolder, SelectionTypes


class LassoSelectionAidLine(AidLineControllerBase):
    _DATA_OBJECTS_SELECTED = "dataObjectsSelected"

    # TODO: Use the selection line config for the lasso.
    def __init__(self, selection_line_config=None, **kwargs):
        """
        :param selection_line_config: The container that holds all values necessary for selections.
        :type selection_line_config: SelectionLineConfiguration
        :param kwargs: Other parameters for the base.
        """
        self._lasso_aid_lines = {}
        self._selection_line_config = selection_line_config if selection_line_config else SelectionLineConfiguration()
        super(LassoSelectionAidLine, self).__init__(**kwargs)

        self._chart.background_div.subscribe(avg.Node.CURSOR_DOWN, self.__on_mouse_down)
        self._chart.selection_data_holder.stop_listening(
            selection_set_added=self._on_selection_set_changed,
            selection_set_removed=self._on_selection_set_changed
        )

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
        if event.cursorid in self._lasso_aid_lines:
            return
        self._lasso_aid_lines[event.cursorid] = SelectionLasso(parent=self._internal_div, event=event)
        self._lasso_aid_lines[event.cursorid].start_listening(lasso_up=self.__on_lasso_up)

    def __on_lasso_up(self, sender, event):
        """
        Called when the cursor dispatches an up event. It will select a area between the given aid lines.

        :type sender: SelectionLasso
        :type event: CursorEvent
        """
        if event.cursorid not in self._lasso_aid_lines:
            return

        selection = SelectionMethodHolder.get_selection_from_data_objects(
            diagram_type=type(self._chart),
            selection_type=SelectionTypes.Lasso,
            data_object_nodes=self._chart.data_object_nodes,
            value1=self._lasso_aid_lines[event.cursorid].polygon(),
            value2=None
        )
        self._lasso_aid_lines.pop(event.cursorid)

        selection = [self._chart.data_objects[key] for key in selection.iterkeys()]
        self.dispatch(self._DATA_OBJECTS_SELECTED, sender=self, selected_data=selection)

    def _draw_intersections(self, intersections):
        pass

    def _draw_label(self, aid_line_div, orientation):
        pass

    def _on_step_backward(self, steps=1, axis_index=0):
        pass

    def _on_step_forward(self, steps=1, axis_index=0):
        pass

    def reset(self):
        """
        Resets this aid line controller.
        """
        for lasso in self._lasso_aid_lines.itervalues():
            lasso.clear()
        self._lasso_aid_lines.clear()
        self._remove_intersections()

    def start_listening(self, data_objects_selected=None):
        """
        Registers a callback to listen to changes or events of this lasso aid line controller. Listeners can register to any number of the
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
