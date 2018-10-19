from libavg import avg
from selection import SelectionType


class LassoSelectionDiv(avg.DivNode):

    def __init__(self, selection_control, parent=None, **kwargs):
        super(LassoSelectionDiv, self).__init__(**kwargs)
        self.registerInstance(self, parent)

        self.__selection_control = selection_control

        self.subscribe(avg.Node.CURSOR_DOWN, self.__on_lasso_div_down)

        self.__callbacks_selection_changed=[]

        self.__selection_active = True

    @property
    def selection_active(self):
        return self.__selection_active

    @selection_active.setter
    def selection_active(self, value):
        if self.__selection_active == value:
            return 

        self.__selection_active = value
        if not value:
            self.__selection_control.remove_all_selections()

    def start_listening(self, selection_changed=None):
        if selection_changed is not None and selection_changed not in self.__callbacks_selection_changed:
            self.__callbacks_selection_changed.append(selection_changed)

    def stop_listening(self, selection_changed=None):
        if selection_changed is not None:
            self.__callbacks_selection_changed.remove(selection_changed)

    def __on_lasso_div_down(self, event):
        if not self.__selection_active:
            return

        lasso = self.__selection_control.create_selection(selection_type=SelectionType.LASSO_SELECTION, event=event)
        lasso.start_listening(lasso_up=self.__on_lasso_up)

    def __on_lasso_up(self, sender, event):
        if not self.__selection_active:
            return

        contact_id = event.contact.id
        if isinstance(event, avg.MouseEvent):
            contact_id = -1
        selection_index = self.__selection_control.get_selection_index_for_touch(contact_id)
        if selection_index is None:
            return

        selected_nodes = self.__selection_control.get_nodes_in_selection(selection_index)
        self.__selection_control.remove_selection(selection_index)

        if len(selected_nodes) == 0:
            # gets triggered a lot on wall because of ghost touches
            # print "number of selected nodes: ", len(selected_nodes)
            return

        for callback in self.__callbacks_selection_changed:
            callback(sender=self, selected_nodes=selected_nodes)
