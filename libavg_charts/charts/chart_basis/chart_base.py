from libavg import avg, gesture
from libavg.avg import DivNode

from configs.config_recognizer import CommonRecognizerDefaults
from configs.visual_data import VisDefaults as defaults
from data_models.data_enums import DataSelectionState
from data_models.data_object import DataObject
from events.event_dispatcher import EventDispatcher
from libavg_charts.aid_lines.aid_line_enums import AidLineType
from libavg_charts.charts.chart_enums import LabelPosition
from libavg_charts.configurations.chart_configuration import ChartConfiguration
from libavg_charts.configurations.text_label_configuration import TextMarkingConfiguration
from libavg_charts.utils.default_values import DataDefaults, ChartDefaults
from selection_ctrl.selection_data_holder import SelectionDataHolder


class ChartBase(avg.DivNode, EventDispatcher):
    _DATA_OBJECT_SELECTION_CHANGED = "dataObjectSelectionChanged"
    _DATA_OBJECT_HIGHLIGHTING_CHANGES = "dataObjectHighlightingChanged"

    def __init__(self, data, data_keys_for_selection, label, view_id=-1,
                 chart_config=None, selection_label_text_config=None,
                 parent=None, **kwargs):
        """
        :param data: A dictionary with data objects. Each entry has a key (the name of the data object) and a dict with all
                     values for all the axis in the chart. This value dicts key is a string with the label of the data descriptor
                     and the value is a list with all values on the specified axis.
        :type data: list[DataObject]
        :param data_keys_for_selection: The keys for the attributes of this data object that are important for the selection.
        :type data_keys_for_selection: list[str]
        :param label: The name of this chart.
        :type label: str
        :param chart_config: The configuration used to create this chart.
        :type chart_config: ChartConfiguration
        :param selection_label_text_config: The configuration used to create labels for selected data objects.
        :type: TextLabelConfiguration
        :type parent: DivNode
        :param kwargs: All other parameter for the div node.
        """
        super(ChartBase, self).__init__(**kwargs)
        self.registerInstance(self, parent)
        EventDispatcher.__init__(self)

        self._chart_config = chart_config or ChartConfiguration()
        self._selection_label_text_config = selection_label_text_config or TextMarkingConfiguration()
        self._label = label
        self._view_id = view_id

        # dict: key -> label of the axis     value -> the view of the axis
        self._axis_views = {}

        self._grid_lines_div = avg.DivNode(parent=self)
        self._background_div = avg.DivNode(parent=self)
        self._axis_div = avg.DivNode(parent=self)
        self._data_div = avg.DivNode(parent=self)
        self._selection_label_div = avg.DivNode(parent=self, sensitive=False)
        self._label_node = None

        self._background_tap_recognizer = gesture.DoubletapRecognizer(
            node=self._background_div,
            maxTime=CommonRecognizerDefaults.DOUBLE_TAP_MAX_TIME,
            maxDist=CommonRecognizerDefaults.DOUBLE_TAP_MAX_DIST,
            detectedHandler=self._on_background_tap
        )

        self._padding_size = (self.size[0] - self._chart_config.padding_left - self._chart_config.padding_right,
                              self.size[1] - self._chart_config.padding_top - self._chart_config.padding_bottom)
        # dict: key -> aid line type     value -> aid line controller
        self._aid_line_controllers = {}

        self._data_objects = {d.obj_id: d for d in data}
        # dict: key -> object name     value -> Node
        self._data_object_nodes = {}
        self._data_object_tap_recognizer = {}
        self._data_keys_for_selection = data_keys_for_selection
        self._selection_data_holder = SelectionDataHolder(data_keys_for_selection)

        # key -> object name     value -> WordNode
        self._data_object_label_nodes = {}

    def __repr__(self):
        return "C {}: \"{}\"".format(self._view_id, self._label)

    @property
    def view_id(self):
        """
        :rtype: int
        """
        return self._view_id

    @view_id.setter
    def view_id(self, value):
        """
        :type value: int
        """
        self._view_id = value

    @property
    def data_objects(self):
        """
        :rtype: dict[str, DataObject]
        """
        return self._data_objects

    @property
    def data_object_nodes(self):
        """
        :rtype: dict[str, Node]
        """
        return self._data_object_nodes

    @property
    def data_keys_for_selection(self):
        """
        :rtype: list[str]
        """
        return self._data_keys_for_selection

    @property
    def background_div(self):
        """
        :rtype: DivNode
        """
        return self._background_div

    @property
    def axis_views(self):
        """
        :rtype: list[ChartAxis]
        """
        return self._axis_views

    @property
    def selection_data_holder(self):
        """
        :rtype: SelectionDataHolder
        """
        return self._selection_data_holder

    @property
    def label(self):
        """
        :rtype: str
        """
        return self._label

    def _draw_label(self):
        """
        Draws the label for this chart.
        """
        if not self._chart_config.show_label:
            return

        self._label_node = avg.WordsNode(
            parent=self,
            text=self._label,
            alignment="center",
            fontsize=self._chart_config.label_text_config.font_size,
            color=self._chart_config.label_text_config.color,
            rawtextmode=True,
            variant=self._chart_config.label_text_config.font_variant
        )

        if self._chart_config.label_pos is LabelPosition.Top:
            self._label_node.pos = (self._chart_config.padding_left + self._padding_size[0] / 2,
                                    self._chart_config.padding_top - (self._chart_config.label_text_config.offset_to_other_element + self._label_node.size[1]))
        else:
            self._label_node.pos = (self._padding_size[0] / 2,
                                    self._chart_config. padding_top + self._padding_size[1] + self._chart_config.label_text_config.offset_to_other_element)

    def draw_chart(self):
        """
        Draws/Redraws this whole chart. It will not be drawn if this methods wasn't called.
        """
        raise NotImplementedError("The 'draw_chart' methods needs to be overwritten through the children of 'ChartBase'.")

    def _draw_grid_lines(self, axis):
        """
        Draws the grid lines in this chart.

        :param axis: The axis the grid lines are connected with.
        :type axis: ChartAxis
        """
        raise NotImplementedError("The '_draw_grid_lines' methods needs to be overwritten and used through the children of 'ChartBase'.")

    def _create_data_objects_for_base(self):
        """
        Creates data objects visualisations for all data objects in this chart. Should always be called at the end of
        the child implementation.
        """
        for key, node in self._data_object_nodes.iteritems():
            self._data_objects[key].start_listening(
                color_changed=self._on_data_object_color_changed,
                selection_state_changed=self._on_data_object_selection_state_changed
            )
            self._data_objects[key].start_listening(selection_state_changed=self._on_data_object_highlighted)
            self._data_object_tap_recognizer[key] = gesture.TapRecognizer(
                node=node,
                maxTime=CommonRecognizerDefaults.TAP_MAX_TIME,
                maxDist=CommonRecognizerDefaults.TAP_MAX_DIST,
                detectedHandler=(lambda sender_id=key: self._on_data_objects_selected_tap(sender_id=sender_id))
            )

    def add_aid_line_controller(self, aid_line_controller_type):
        """
        Adds a new aid line controller to this chart.

        :param aid_line_controller_type: The controller that should be added.
        :type aid_line_controller_type: AidLineType
        """
        raise NotImplementedError("The 'add_aid_line_controller' methods needs to be overwritten through the children of 'ChartBase'.")

    def _add_aid_line_controller(self, aid_line_controller_type):
        """
        Adds possible to a newly added aid line controller several events.

        :param aid_line_controller_type: The controller that should be added.
        :type aid_line_controller_type: AidLineType
        """
        if AidLineType.can_select(aid_line_controller_type):
            self._aid_line_controllers[aid_line_controller_type].start_listening(data_objects_selected=self._on_data_objects_selected_aid_line)

    def remove_aid_line_controller(self, aid_line_controller_type):
        """
        Removes a already added aid line controller from this chart.

        :param aid_line_controller_type: The controller that should be removed.
        :type aid_line_controller_type: AidLineType
        """
        if aid_line_controller_type not in self._aid_line_controllers:
            return

        self._aid_line_controllers.pop(aid_line_controller_type).delete()

    def reset_aid_line_controller(self, aid_line_controller_type=None):
        """
        Resets aid line controllers.

        :param aid_line_controller_type: The aid line type to reset the aid line for. If None all aid line controller will be reseted.
        :type aid_line_controller_type: AidLineType
        """
        if aid_line_controller_type and aid_line_controller_type not in self._aid_line_controllers:
            return

        if aid_line_controller_type:
            self._aid_line_controllers[aid_line_controller_type].reset()
        else:
            for aid_line_controller in self._aid_line_controllers.itervalues():
                aid_line_controller.reset()

    def set_aid_line_controller_attributes(self, aid_line_controller_type=None, **kwargs):
        """
        Sets different attributes for a aid line controller.

        :param aid_line_controller_type: The controller which attribute should be set. If not given, all aid controllers will set the new value.
        :type aid_line_controller_type: AidLineType
        :param kwargs: The possible parameters to set.
        """
        if aid_line_controller_type:
            if aid_line_controller_type not in self._aid_line_controllers:
                return
            self._aid_line_controllers[aid_line_controller_type].set_attributes(**kwargs)
        else:
            for controller in self._aid_line_controllers.values():
                controller.set_attributes(**kwargs)

    def invoke_aid_line_controller_event(self, event_name, aid_line_controller_type=None, **kwargs):
        """
        Invokes a event on the given aid line controller.

        :param event_name: The name of the event that should be invoked.
        :type event_name: str
        :param aid_line_controller_type: The controller which attribute should be set. If not given, all aid line controllers will invoke the event.
        :type aid_line_controller_type: AidLineType
        :param kwargs: The possible parameters for the event.
        """
        aid_line_controller = self._aid_line_controllers.values()
        if aid_line_controller_type:
            if aid_line_controller_type not in self._aid_line_controllers:
                return
            aid_line_controller = [self._aid_line_controllers[aid_line_controller_type]]

        for controller in aid_line_controller:
            controller.invoke_event(event_name=event_name, **kwargs)

    def change_data_selection(self, selection_set_id, selection_set, selection_diff, addition, update_colors=True):
        """
        Updates the selection for this view.

        :param selection_set_id: The id of the selection set.
        :type selection_set_id: str
        :param selection_set: The new current selection set.
        :type selection_set: list
        :param selection_diff: The diff between the new and the old selection set.
        :type selection_diff: list
        :param addition: Was this change a addition?
        :type addition: bool
        :param update_colors: Should the colors be updated to the defaults values?
        :type update_colors: bool
        :return: All keys to the data objects that were affected through the change.
        :rtype: list[str]
        """
        data_objects = self.find_data_objects(
            data_objects=self._data_objects,
            values_to_check=selection_diff,
            key=selection_set_id.split('|')[0]
        )
        # Create new selection set.
        if not self._selection_data_holder.get_selection_set(selection_set_id):
            color = DataDefaults.COLOR_SELECTED
            opacity = defaults.ITEM_OPACITY_SELECTED
            self._selection_data_holder.add_new_selection_set(
                selection_set=selection_set,
                selection_set_id=selection_set_id
            )
            self.change_selection_state_for_data_objects(data_objects.keys(), DataSelectionState.Selected)
            data_objects = self.find_data_objects(
                data_objects=self._data_objects,
                values_to_check=self._selection_data_holder.get_selection_set(selection_set_id),
                key=selection_set_id.split('|')[0]
            )
        # Update the existing one: Add the diff
        elif addition:
            color = defaults.DEFAULT_SELECTION_COLOR
            opacity = defaults.ITEM_OPACITY_SELECTED
            self._selection_data_holder.add_selection_to_set(
                selection_set=selection_diff,
                selection_set_id=selection_set_id
            )
            self.change_selection_state_for_data_objects(data_objects.keys(), DataSelectionState.Selected)
            data_objects = self.find_data_objects(
                data_objects=self._data_objects,
                values_to_check=self._selection_data_holder.get_selection_set(selection_set_id),
                key=selection_set_id.split('|')[0]
            )
        # Update the existing one: Remove the diff
        else:  # not addition:
            color = defaults.ITEM_COLOR
            opacity = defaults.ITEM_OPACITY
            self._selection_data_holder.remove_selection_from_set(
                selection_set=selection_diff,
                selection_set_id=selection_set_id
            )
            # Check if an data object is in another selection set. Remove it if its the case.
            for do_id, data_object in [(d_id, do) for d_id, do in data_objects.iteritems()]:
                for att_key, attribute in data_object.attributes.iteritems():
                    if att_key not in self._data_keys_for_selection:
                        continue
                    if len(self._selection_data_holder.check_if_selection_in_set([attribute.values])) != 0:
                        data_objects.pop(do_id, None)

            self.change_selection_state_for_data_objects(data_objects.keys(), DataSelectionState.Nothing)
            if self._selection_data_holder.empty:
                data_objects = self._data_objects
            else:
                data_objects = self.find_data_objects(
                    data_objects=self._data_objects,
                    values_to_check=selection_diff,
                    key=selection_set_id.split('|')[0]
                )

        if update_colors:
            self.change_color_for_data_objects(data_objects.keys(), color, opacity)

        return data_objects.keys()

    def remove_all_selections(self):
        """
        Removes all selections from this chart.
        """
        self._on_background_tap()

    def change_color_for_data_objects(self, obj_ids, color, opacity):
        """
        Changes the color of the given data objects.

        :param obj_ids: The ids of all data objects that should change the color.
        :type obj_ids: list[str]
        :param color: The color to change the data objects to.
        :type color: Color
        :param opacity: The opacity for the data object.
        :type opacity: float
        """
        for obj_id, data_object in [(obj_id, do) for obj_id, do in self._data_objects.iteritems() if obj_id in obj_ids]:
            data_object.color = color

            if obj_id in self._data_object_nodes:
                if isinstance(self._data_object_nodes[obj_id], avg.RectNode):
                    self._data_object_nodes[obj_id].fillopacity = opacity if opacity is not None else self._data_object_nodes[obj_id].fillopacity
                else:
                    self._data_object_nodes[obj_id].opacity = opacity if opacity is not None else self._data_object_nodes[obj_id].opacity
            if obj_id in self._data_object_label_nodes:
                self._data_object_label_nodes[obj_id].color = color

    def change_selection_state_for_data_objects(self, obj_ids, state):
        """
        Changes the selection state of a given data object.

        :param obj_ids: The ids of all data objects that should change the color.
        :type obj_ids: list[str]
        :param state: The new state for the data objects.
        :type state: DataSelectionState
        """
        for obj_id, data_object in [(obj_id, do) for obj_id, do in self._data_objects.iteritems() if obj_id in obj_ids]:
            data_object.selection_state = state
            if state is DataSelectionState.Selected:
                self._data_div.reorderChild(self._data_object_nodes[obj_id], self._data_div.getNumChildren() - 1)

    def find_data_objects(self, data_objects, values_to_check, key):
        """
        Checks a list of data objects if there are objects that contain values from the selections set.

        :param data_objects: The data objects to check in.
        :type data_objects: dict[str, DataObject]
        :param values_to_check: The selection set that should be checked for.
        :type values_to_check: list
        :param key: The key that is used to check the data objects.
        :type key: str
        :return: All data objects that contain a value from the selection set.
        :rtype: dict[str, DataObject]
        """
        if key not in self._data_keys_for_selection:
            return {}

        found_data_objects = {}
        for obj_id, data_object in data_objects.iteritems():
            if key not in data_object.attributes:
                continue
            for data_value in values_to_check:
                if not (data_value == data_object.attributes[key].values or [data_value] == data_object.attributes[key].values):
                    continue
                found_data_objects[obj_id] = data_object

        return found_data_objects

    def _on_data_objects_selected_aid_line(self, sender, selected_data):
        """
        Called when a subset of data objects were selected through an aid line.

        :type sender: AidLineControllerBase
        :param selected_data: The selected data set and their nodes.
        :type selected_data: list[DataObject]
        """
        selection_sets = {}
        for data_object in selected_data:
            for key in self._data_keys_for_selection:
                if key not in data_object.attributes:
                    continue

                if key not in selection_sets:
                    selection_sets[key] = []
                selection_sets[key].append(data_object.attributes[key].values)

        self.change_color_for_data_objects([do.obj_id for do in selected_data], color=DataDefaults.COLOR_SELECTED, opacity=defaults.ITEM_OPACITY_SELECTED)
        self.change_selection_state_for_data_objects([do.obj_id for do in selected_data], state=DataSelectionState.Selected)

        for selection_key, selection_set in selection_sets.iteritems():
            selection_id = self._selection_data_holder.get_next_id(selection_key)
            if not selection_id:
                return

            selection_id, selection_diff = self._selection_data_holder.add_new_selection_set(
                selection_set=selection_set,
                selection_set_id=selection_id
            )

            self.dispatch(
                self._DATA_OBJECT_SELECTION_CHANGED,
                sender=self,
                selection_data_holder=self._selection_data_holder,
                selection_set_id=selection_id,
                selection_diff=selection_diff
            )

    def _on_data_objects_selected_tap(self, sender_id):
        """
        Called when on a data object in the view was tapped.

        :param sender_id: The id of the tapped node.
        :type sender_id: object
        """
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
            if len(selection_ids) > 0:
                self.change_color_for_data_objects([sender_id], color=defaults.ITEM_COLOR, opacity=defaults.ITEM_OPACITY)
                self.change_selection_state_for_data_objects([sender_id], state=DataSelectionState.Nothing)

                for selection_id in selection_ids:
                    selection_diffs[selection_id] = self._selection_data_holder.remove_selection_from_set(
                        selection_set_id=selection_id,
                        selection_set=selection_set
                    )
            else:
                self.change_color_for_data_objects([sender_id], color=DataDefaults.COLOR_SELECTED, opacity=defaults.ITEM_OPACITY_SELECTED)
                self.change_selection_state_for_data_objects([sender_id], state=DataSelectionState.Selected)

                # If the selection wasn't found, create a new set with it.
                selection_id = self._selection_data_holder.get_next_id(selection_key)
                selection_id, selection_diff = self._selection_data_holder.add_new_selection_set(
                    selection_set=selection_set,
                    selection_set_id=selection_id,
                    single_selection=False
                )
                selection_diffs[selection_id] = selection_diff
            for selection_id, selection_diff in selection_diffs.iteritems():
                self.dispatch(
                    self._DATA_OBJECT_SELECTION_CHANGED,
                    sender=self,
                    selection_data_holder=self._selection_data_holder,
                    selection_set_id=selection_id,
                    selection_diff=selection_diff
                )

    def _on_axis_marking_tap(self, sender, marking_node):
        """
        Called when an marking on a axis was tapped.

        :type sender: ChartAxis
        :param marking_node: The word node that was tapped.
        :type marking_node: WordsNode
        """
        if marking_node is None:
            return
        if sender.data_desc.key_name not in self._data_keys_for_selection:
            return

        selection_sets = {sender.data_desc.key_name: [[marking_node.text.encode('utf-8')]]}
        data_objects = self.find_data_objects(self._data_objects, selection_sets.values(), sender.data_desc.key_name)

        for selection_key, selection_set in selection_sets.iteritems():
            selection_ids = self._selection_data_holder.check_if_selection_in_set(selection_set)
            selection_diffs = {}
            # If the selection is in a selection set, delete it from it.
            if len(selection_ids) > 0:
                self.change_color_for_data_objects(data_objects.keys(), color=defaults.ITEM_COLOR, opacity=defaults.ITEM_OPACITY)
                self.change_selection_state_for_data_objects(data_objects.keys(), state=DataSelectionState.Nothing)

                for selection_id in selection_ids:
                    selection_diffs[selection_id] = self._selection_data_holder.remove_selection_from_set(
                        selection_set_id=selection_id,
                        selection_set=selection_set
                    )
            else:
                self.change_color_for_data_objects(data_objects.keys(), color=DataDefaults.COLOR_SELECTED, opacity=defaults.ITEM_OPACITY_SELECTED)
                self.change_selection_state_for_data_objects(data_objects.keys(), state=DataSelectionState.Selected)

                # If the selection wasn't found, create a new set with it.
                selection_id = self._selection_data_holder.get_next_id(selection_key)
                selection_id, selection_diff = self._selection_data_holder.add_new_selection_set(
                    selection_set=selection_set,
                    selection_set_id=selection_id,
                    single_selection=False
                )
                selection_diffs[selection_id] = selection_diff
            for selection_id, selection_diff in selection_diffs.iteritems():
                self.dispatch(
                    self._DATA_OBJECT_SELECTION_CHANGED,
                    sender=self,
                    selection_data_holder=self._selection_data_holder,
                    selection_set_id=selection_id,
                    selection_diff=selection_diff
                )

    def _on_background_tap(self):
        """
        Called when a tap on the background has happened.
        """
        for axis in self._axis_views.values():
            axis.reset_markings()

        data_object_ids = [do_id for do_id, do in self._data_objects.iteritems() if do.selection_state is DataSelectionState.Selected]
        self.change_color_for_data_objects(
            obj_ids=data_object_ids,
            color=defaults.ITEM_COLOR,
            opacity=defaults.ITEM_OPACITY
        )
        self.change_color_for_data_objects(data_object_ids, color=DataDefaults.COLOR, opacity=defaults.ITEM_OPACITY)
        self.change_selection_state_for_data_objects(data_object_ids, state=DataSelectionState.Nothing)

        selection_diffs = self._selection_data_holder.remove_all_selection_sets()
        for selection_id, selection_diff in selection_diffs.iteritems():
            self.dispatch(
                self._DATA_OBJECT_SELECTION_CHANGED,
                sender=self,
                selection_data_holder=self._selection_data_holder,
                selection_set_id=selection_id,
                selection_diff=selection_diff
            )

    def _on_data_object_color_changed(self, sender, new_color):
        """
        Called when the color of a data object has changed.

        :type sender: DataObject
        :param new_color: The new color.
        :type new_color: Color
        """
        raise NotImplementedError("The method '_on_data_object_color_changed' needs to be implemented from the children of the 'ChartBase' class.")

    def _on_data_object_selection_state_changed(self, sender, new_state, old_state):
        """
        Called when the selection state of a data object has changed.

        :type sender: DataObject
        :param new_state: The new state.
        :type new_state: DataSelectionState
        :param old_state: The old state.
        :type old_state: DataSelectionState
        """
        raise NotImplementedError("The method '_on_data_object_selection_state_changed' needs to be implemented from the children of the 'ChartBase' class.")

    def _on_data_object_highlighted(self, sender, new_state, old_state):
        """
        Called when the selection state of a data object has changed. Only used if the old or new state was highlighted.

        :type sender: DataObject
        :param new_state: The new state.
        :type new_state: DataSelectionState
        :param old_state: The old state.
        :type old_state: DataSelectionState
        """
        if new_state is DataSelectionState.Highlighted:
            self.change_color_for_data_objects([sender.obj_id], color=DataDefaults.COLOR_HIGHLIGHTED, opacity=defaults.ITEM_OPACITY_HIGHLIGHTED)
            self.change_selection_state_for_data_objects([sender.obj_id], state=DataSelectionState.Highlighted)
        elif new_state is DataSelectionState.Nothing and old_state is DataSelectionState.Highlighted:
            self.change_color_for_data_objects([sender.obj_id], color=DataDefaults.COLOR, opacity=defaults.ITEM_OPACITY)
            self.change_selection_state_for_data_objects([sender.obj_id], state=DataSelectionState.Nothing)

        self.dispatch(self._DATA_OBJECT_HIGHLIGHTING_CHANGES, sender=self, data_item=sender)

    def start_listening(self, data_object_selection_changed=None, data_object_highlighting_changed=None):
        """
        Registers a callback to listen to changes to this chart. Listeners can register to any number of the provided
        events. For the required structure of the callbacks see below.

        :param data_object_selection_changed: Called when in the selection of data objects in this chart was changed.
        :type data_object_selection_changed: function(sender:ChartBase, selection_data_holder:SelectionDataHolder, selection_set_id:str, selection_diff:list)
        :param data_object_highlighting_changed: Called when the selection state has changed from or to highlighted.
        :type data_object_highlighting_changed: function(sender:ChartBase, data_item:DataObject)
        """
        self.bind(self._DATA_OBJECT_SELECTION_CHANGED, data_object_selection_changed)
        self.bind(self._DATA_OBJECT_HIGHLIGHTING_CHANGES, data_object_highlighting_changed)

    def stop_listening(self, data_object_selection_changed=None, data_object_highlighting_changed=None):
        """
        Stops listening to an event the listener has registered to previously. The provided callback needs to be the
        same that was used to listen to the event in the fist place.

        :param data_object_selection_changed: Called when in the selection of data objects in this chart was changed.
        :type data_object_selection_changed: function(sender:ChartBase, selection_data_holder:SelectionDataHolder, selection_set_id:str, selection_diff:list)
        :param data_object_highlighting_changed: Called when the selection state has changed from or to highlighted.
        :type data_object_highlighting_changed: function(sender:ChartBase, data_item:DataObject)
        """
        self.unbind(self._DATA_OBJECT_SELECTION_CHANGED, data_object_selection_changed)
        self.bind(self._DATA_OBJECT_HIGHLIGHTING_CHANGES, data_object_highlighting_changed)
