from libavg import avg
from libavg.avg import CursorEvent, Node
from libavg.gesture import SwipeRecognizer

import configs.config_app as config_app
from configs.visual_data import VisDefaults as defaults
from data_models.data_enums import DataSelectionState
from data_models.data_object import DataObject
from device_tracking.device import Device
from device_tracking.device_manager import DeviceManager
from events.event_injection import inject_touch_event
from libavg_charts.aid_lines.aid_line_enums import AidLineType
from libavg_charts.aid_lines.deposit_aid_line import DepositAidLine
from libavg_charts.charts.chart_basis.chart_base import ChartBase
from logging_base.study_logging import StudyLog
from multi_view_ctrl.multi_div_node import MultiDivNode
from pointer_ctrl.configurations.device_pointer_configurations import DevicePointerConfigurations
from pointer_ctrl.cross_cursor import CrossCursor
from pointer_ctrl.pointer_control import PointerControl
from pointer_ctrl.pointer_device_view import PointerDeviceView
from selection_ctrl.selection_color_mapper import SelectionColorMapper
from selection_ctrl.selection_data_holder import SelectionDataHolder
from map_views.map_vis_view import MapVisView
from map_views.model.map_point import MapPoint
from map_views.views.map_point_detail_view import MapPointDetailView
from map_views.views.map_point_view import MapPointView
from tornado_server.server import TornadoServer


class DivicoControl(object):
    def __init__(self, multi_view_node):
        """
        :param multi_view_node: The multi view node this controller should work on.
        :type multi_view_node: MultiDivNode
        """
        self.__multi_view_node = multi_view_node
        for grid_element_divs in self.__multi_view_node.grid_element_divs.values():
            for view_node in grid_element_divs.child_nodes:
                # Add the listener to the particular views.
                if isinstance(view_node, ChartBase):
                    view_node.start_listening(data_object_selection_changed=self.__on_selection_of_data_objects_in_view)
                elif isinstance(view_node, MapVisView):
                    view_node.start_listening(selection_changed=self.__on_selection_of_data_objects_in_view)

        self.__devices_current_views = {}
        # key -> device id     value -> event
        self.__hold_on_devices = {}

        # key -> device id     value -> last pos
        self.__double_tap_hold_on_devices = {}
        # key -> device id     value -> the state: 'Idle', 'Zoom' or 'Pan'
        self.__double_tap_hold_state = {}
        # key -> device_id     value -> event id that caused the double tap hold
        self.__double_tap_hold_event_id = {}

        # key -> device id     value -> data object/node/mappoint
        self.__highlighted_data_item_on_device = {}
        self.__swipe_on_devices = []
        self.__device_manager = DeviceManager(config_app.optitrack_ip, config_app.optitrack_port)
        self.__device_manager.subscribe(DeviceManager.DEVICE_ADDED, self.__on_device_added)

        self.__current_pointer_mode = 0
        self.__pointer_modes = [DevicePointerConfigurations(pointer_div_node_class=CrossCursor)]
        self.__pointer_control = PointerControl(parent=self.__multi_view_node)

        self.__zoom_pivot_pos = None
        self.__pan_pivot_pos = None
        self.__pan_frame_count = -1

        self.__tornado_server = None
        self.__event_id = 0

    def start_server(self):
        """
        Start the server for this web client control.
        """
        self.__tornado_server = TornadoServer(divico_controller=self)
        self.__tornado_server.start()

    def __on_device_added(self, device):
        """
        Called when a new device was added.

        :param device: The newly added device.
        :type device: Device
        """
        self.__pointer_control.add_new_pointer(device=device, pointer_mode=self.__pointer_modes[-1])
        self.__devices_current_views[device.id] = PointerDeviceView(device, self.__pointer_modes[self.__current_pointer_mode])
        self.__highlighted_data_item_on_device[device.id] = None

        # Add the event for the pointer of the wall.
        device.start_listening(device_moved=self.__on_device_moved)

    def __on_device_moved(self, sender, pos_space, pos_screen):
        """
        Called if the device is moved.
        It handles the movement of the cursor, the highlighting and the panning on a map.

        :type sender: Device
        :param pos_space: The position of the device in the space in front of the screen.
        :type pos_space: tuple[float, float, float]
        :param pos_screen: The position of the cursor on the screen.
        :type pos_screen: tuple[float, float]
        """
        self.__pointer_control.move_pointer(device_id=sender.id, pos=pos_screen)
        self.__check_highlighting(sender.id, pos_screen)

        # Inject a move (for drag)
        if sender.id in self.__hold_on_devices:
            inject_touch_event(
                event_type=avg.Event.CURSOR_MOTION,
                pos=(sender.pos_screen_x + self.__multi_view_node.pos[0], sender.pos_screen_y + self.__multi_view_node.pos[1]),
                event_id=self.__hold_on_devices[sender.id]
            )
        # Use the movement for the drag on a map.
        elif sender.id in self.__double_tap_hold_on_devices:
            # Only allow the padding if no zoom is active.
            if self.__double_tap_hold_state[sender.id] == 'Zoom':
                return

            device = self.__device_manager.devices[sender.id]
            grid_element_div = self.__multi_view_node.get_grid_element_from_pos((device.pos_screen_x, device.pos_screen_y))
            # Look for a grid element with a map view in it.
            if not grid_element_div:
                return
            for vis_view in grid_element_div.child_nodes:
                if not isinstance(vis_view, MapVisView):
                    return

                if self.__pan_pivot_pos is None:
                    self.__pan_pivot_pos = device.pos_screen_x - grid_element_div.pos[0], device.pos_screen_y - grid_element_div.pos[1]
                old_pos = self.__double_tap_hold_on_devices[device.id]
                translation = (device.pos_screen_x - old_pos[0], device.pos_screen_y - old_pos[1])
                # Save the current double tap hold activity.
                if self.__double_tap_hold_state[sender.id] != 'Pan':
                    if config_app.min_pan_movement ** 2 < translation[0] ** 2 + translation[1] ** 2:
                        self.__double_tap_hold_state[sender.id] = 'Pan'
                        # Let the cursor up be somewhere else to prevent other inputs.
                        inject_touch_event(
                            event_type=avg.Event.CURSOR_UP,
                            pos=(-100, -100),
                            event_id=self.__double_tap_hold_event_id[sender.id]
                        )
                    else:
                        return

                if not config_app.pan_enabled:
                    return

                # Only allow the pan to be activated in a given number of frames (for the performance).
                self.__pan_frame_count += 1
                if self.__pan_frame_count % config_app.pan_frequency_factor == 0:
                    # The scale is the same while the map is panning.
                    vis_view.map_background_provider.transform(
                        scale=1,
                        translation=translation,
                        pivot=self.__pan_pivot_pos
                    )
                    self.__double_tap_hold_on_devices[device.id] = device.pos_screen_x, device.pos_screen_y

    def on_device_touchpad_created(self, connection_id):
        """
        Called when a new touchpad from a
        :param connection_id:
        :return:
        """
        self.__device_manager.on_pair_webclient(connection_id)

    def on_device_touchpad_event(self, connection_id, update_type):
        """
        Handles the touchup and touchdown events from the touchpad
        :param connection_id: The id of the connection.
        :type connection_id: int
        :param update_type: Either "touchdown" or "touchup".
        :type update_type: str
        """
        device = self.__device_manager.get_device_from_connection_id(connection_id)
        if update_type == "touchDown":
            self.__on_device_canvas_cursor_down(device)
        elif update_type == "touchUp":
            self.__on_device_canvas_cursor_up(device)
        elif update_type == "swipeUp":
            self.__on_device_canvas_swipe(device, SwipeRecognizer.UP)
        elif update_type == "swipeDown":
            self.__on_device_canvas_swipe(device, SwipeRecognizer.DOWN)

    def __check_highlighting(self, device_id, pos_screen):
        """
        Checks if a data items lies under the position and highlights it if possible.

        :param device_id: The id of the device the position is associated with.
        :type device_id: int
        :param pos_screen: The position of the cursor on the screen.
        :type pos_screen: tuple[float, float]
        """
        if device_id not in self.__highlighted_data_item_on_device:
            return

        grid_element_div = self.__multi_view_node.get_grid_element_from_pos(pos_screen)
        # Look for a grid element under the cursor.
        if not grid_element_div:
            return

        # Set highlighting colors if the cursor points on a data item.
        for vis_view in grid_element_div.child_nodes:
            highlighted_element = None

            rel_pos = grid_element_div.get_rel_pos(pos_screen)
            element = vis_view.getElementByPos(rel_pos)
            # For all charts.
            if isinstance(vis_view, ChartBase):
                chart = self.__get_parent_from_node_with_type(element, ChartBase, ChartBase)
                if chart is not None and element in chart.data_object_nodes.values():
                    data_object_key = chart.data_object_nodes.keys()[chart.data_object_nodes.values().index(element)]
                    data_object = chart.data_objects[data_object_key]
                    # Set the data item as highlighted.
                    if data_object.selection_state is DataSelectionState.Nothing:
                        data_object.selection_state = DataSelectionState.Highlighted
                    highlighted_element = data_object
            # For the map views.
            elif isinstance(vis_view, MapVisView):
                map_point_view = self.__get_parent_from_node_with_type(element, MapPointView, MapVisView)
                if map_point_view is not None:
                    # Set the data item as highlighted.
                    if map_point_view.point_model.element_state is DataSelectionState.Nothing:
                        map_point_view.point_model.element_state = DataSelectionState.Highlighted
                    highlighted_element = map_point_view.point_model

            # Set the new element to be highlighted and delete the old one.
            if highlighted_element is not self.__highlighted_data_item_on_device[device_id]:
                if self.__highlighted_data_item_on_device[device_id] is not None:
                    if isinstance(self.__highlighted_data_item_on_device[device_id], DataObject):
                        if self.__highlighted_data_item_on_device[device_id].selection_state is DataSelectionState.Highlighted:
                            self.__highlighted_data_item_on_device[device_id].selection_state = DataSelectionState.Nothing
                    elif isinstance(self.__highlighted_data_item_on_device[device_id], MapPoint):
                        if self.__highlighted_data_item_on_device[device_id].element_state is DataSelectionState.Highlighted:
                            self.__highlighted_data_item_on_device[device_id].element_state = DataSelectionState.Nothing
                    elif isinstance(self.__highlighted_data_item_on_device[device_id], Node):
                        if self.__highlighted_data_item_on_device[device_id].element_state is DataSelectionState.Highlighted:
                            self.__highlighted_data_item_on_device[device_id].element_state = DataSelectionState.Nothing
                self.__highlighted_data_item_on_device[device_id] = highlighted_element

    def __on_device_canvas_swipe(self, sender, direction):
        """
        Called when a swipe event on a device canvas was entered.

        :param sender: The device view that caused this event.
        :type sender: Device
        :param direction: The direction of the swipe.
        :type direction: int
        """
        self.__swipe_on_devices.append(sender.id)

        # Pointer mode change.
        # Tool creation or deletion.
        if direction is SwipeRecognizer.UP:
            self.__on_swipe_up(sender=sender)
        elif direction is SwipeRecognizer.DOWN:
            self.__on_swipe_down(sender=sender)

    def __on_swipe_up(self, sender):
        """
        Called when a swipe up occurred.
        Creates aid lines or shows the detail view of map points.

        :param sender: The device that caused this event.
        :type sender: Device
        """
        grid_element_div = self.__multi_view_node.get_grid_element_from_pos((sender.pos_screen_x, sender.pos_screen_y))
        # Look for a grid element under the cursor.s.
        if not grid_element_div:
            return
        for vis_view in grid_element_div.child_nodes:
            rel_pos = grid_element_div.get_rel_pos((sender.pos_screen_x, sender.pos_screen_y))
            if isinstance(vis_view, MapVisView):
                element = vis_view.getElementByPos(rel_pos)
                # Show the detail view of the map point.
                if isinstance(element, avg.ImageNode):
                    map_point_view = self.__get_parent_from_node_with_type(element, MapPointView, MapVisView)

                    if map_point_view is not None:
                        map_point_view.show_detail_view(True)
                        StudyLog.get_instance().write_event_log('A DoD was opened (by swipe).')
                else:
                    map_point_detail_view = self.__get_parent_from_node_with_type(element, MapPointDetailView, MapVisView)
                    if map_point_detail_view:
                        map_point_detail_view.map_point_view.show_detail_view(True)
                        StudyLog.get_instance().write_event_log('A DoD was opened (by swipe).')

            # Aid line creation
            if isinstance(vis_view, ChartBase):
                for aid_line_type in [AidLineType.Deposit, AidLineType.DepositVertical, AidLineType.DepositHorizontal]:
                    vis_view.invoke_aid_line_controller_event(
                        event_name=DepositAidLine.ADD_AID_LINE,
                        aid_line_controller_type=aid_line_type,
                        pos=rel_pos
                    )

    def __on_swipe_down(self, sender):
        """
        Called when a swipe down occurred.
        Deletes aid lines or hides the detail view of map points.

        :param sender: The device that caused this event.
        :type sender: Device
        """
        grid_element_div = self.__multi_view_node.get_grid_element_from_pos((sender.pos_screen_x, sender.pos_screen_y))
        # Look for a grid element under the cursor.
        if not grid_element_div:
            return
        for vis_view in grid_element_div.child_nodes:
            rel_pos = grid_element_div.get_rel_pos((sender.pos_screen_x, sender.pos_screen_y))
            if isinstance(vis_view, MapVisView):
                element = vis_view.getElementByPos(rel_pos)
                # Show the detail view of the map point.
                if isinstance(element, avg.ImageNode):
                    map_point_view = self.__get_parent_from_node_with_type(element, MapPointView, MapVisView)
                    if map_point_view:
                        map_point_view.show_detail_view(False)
                        StudyLog.get_instance().write_event_log('A DoD was closed (by swipe).')
                else:
                    map_point_detail_view = self.__get_parent_from_node_with_type(element, MapPointDetailView, MapVisView)
                    if map_point_detail_view:
                        map_point_detail_view.map_point_view.show_detail_view(False)
                        StudyLog.get_instance().write_event_log('A DoD was closed (by swipe).')

            # Aid line deletion.
            elif isinstance(vis_view, ChartBase):
                for aid_line_type in [AidLineType.Deposit, AidLineType.DepositVertical, AidLineType.DepositHorizontal, AidLineType.AxisDragX, AidLineType.AxisDragY]:
                    vis_view.invoke_aid_line_controller_event(
                        event_name=DepositAidLine.DELETE_AID_LINE,
                        aid_line_controller_type=aid_line_type,
                        pos=rel_pos
                    )

    def __on_device_canvas_hold(self, sender, event):
        """
        Called when a hold event on a device canvas was entered.
        It will save the hold for this device for other events.

        :type sender: PointerDeviceView
        :param event: The event.
        :type event: CursorEvent
        """
        if sender.device_id not in self.__device_manager.devices:
            return

        self.__hold_on_devices[sender.device_id] = event

    def __on_device_canvas_drag(self, sender, pos_change):
        """
        Called when a drag event on the device canvas was recognized.

        :type sender: PointerDeviceView
        :param pos_change: The last movement.
        :type pos_change: tuple[float, float]
        """
        pass

    def __on_device_double_tap_hold(self, sender, event):
        """
        Called when a hold after/in a double tap was recognized.
        Set values for possible pan or zoom interactions.

        :type sender: PointerDeviceView
        :param event: The event.
        :type event: CursorEvent
        """
        if sender.device_id not in self.__device_manager.devices:
            return

        device = self.__device_manager.devices[sender.device_id]
        self.__double_tap_hold_on_devices[sender.device_id] = device.pos_screen_x, device.pos_screen_y
        self.__double_tap_hold_state[sender.device_id] = 'Idle'
        self.__double_tap_hold_event_id[sender.device_id] = event.cursorid
        self.__pan_frame_count = -1

    def __on_device_double_tap_hold_drag(self, sender, pos_change):
        """
        Called when a drag after a double tap hold was recognized.
        Handles the zoom with the device.

        :type sender: PointerDeviceView
        :param pos_change: The last movement.
        :type pos_change: tuple[float, float]
        """
        if sender.device_id not in self.__device_manager.devices:
            return
        if self.__double_tap_hold_state[sender.device_id] == 'Pan':
            return

        if self.__double_tap_hold_state[sender.device_id] != 'Zoom':
            self.__double_tap_hold_state[sender.device_id] = 'Zoom'
            # Let the cursor up be somewhere else to prevent other inputs.
            inject_touch_event(
                event_type=avg.Event.CURSOR_UP,
                pos=(-100, -100),
                event_id=self.__double_tap_hold_event_id[sender.device_id]
            )

        if not config_app.zoom_enabled:
            return

        device = self.__device_manager.devices[sender.device_id]
        grid_element_div = self.__multi_view_node.get_grid_element_from_pos((device.pos_screen_x, device.pos_screen_y))
        # Look for a grid element under the cursor.
        if not grid_element_div:
            return
        for vis_view in grid_element_div.child_nodes:
            if not isinstance(vis_view, MapVisView):
                return
            # Only use the y value for the zoom
            if self.__zoom_pivot_pos is None:
                self.__zoom_pivot_pos = device.pos_screen_x - grid_element_div.pos[0], device.pos_screen_y - grid_element_div.pos[1]
            # TODO: Update the scale factor if wished
            vis_view.map_background_provider.transform(
                scale=(200 / (200 - pos_change[1])),
                translation=(0, 0),
                pivot=self.__zoom_pivot_pos
            )

    def __on_device_double_tap_hold_end(self, sender):
        """
        Called when a double tap hold has ended.
        Reset values for the pan and zoom.

        :type sender: PointerDeviceView
        """
        self.__zoom_pivot_pos = None
        self.__pan_pivot_pos = None

    def __on_device_canvas_cursor_down(self, sender):
        """
        Called when a cursor down event on the device canvas was recognized.
        Injects the cursor down event.

        :type sender: Device
        """
        self.__hold_on_devices[sender.id] = self.__event_id
        self.__event_id += 1
        inject_touch_event(avg.Event.CURSOR_DOWN, sender.pos_screen, self.__hold_on_devices[sender.id])

    def __on_device_canvas_cursor_up(self, sender):
        """
        Called when a cursor up event on the device canvas was recognized.
        Injects the event at a given position. Deletes some values.

        :type sender: Device
        """
        # If the last event was a swipe, move the injection point outside of the view to prevent an tap event from the injection.
        if sender.id in self.__swipe_on_devices:
            pos = -100, -100
            self.__swipe_on_devices.remove(sender.id)
        else:
            pos = (sender.pos_screen_x + self.__multi_view_node.pos[0], sender.pos_screen_y + self.__multi_view_node.pos[1])

        # Check if a double tap has happened from this device. If yes check its that. Only allow a normal cursor up
        # event if the double tap hold wasn't either a zoom or a pan.
        if not (sender.id in self.__double_tap_hold_on_devices and self.__double_tap_hold_state[sender.id] != 'Idle'):
            inject_touch_event(
                event_type=avg.Event.CURSOR_UP,
                pos=pos,
                event_id=self.__hold_on_devices[sender.id]
            )

        if sender.id in self.__hold_on_devices:
            self.__hold_on_devices.pop(sender.id)
        if sender.id in self.__double_tap_hold_on_devices:
            self.__double_tap_hold_on_devices.pop(sender.id)
            self.__double_tap_hold_state.pop(sender.id)
            self.__double_tap_hold_event_id.pop(sender.id)

    def __on_selection_of_data_objects_in_view(self, sender, selection_data_holder, selection_set_id, selection_diff):
        """
        Called when a selection on a node in a grid element div were made.
        Sets the color and the state of all visviews in the application.

        :type sender: Node
        :param selection_data_holder: The selection data holder for the vis.
        :type selection_data_holder: SelectionDataHolder
        :param selection_set_id: The id of the changed selection.
        :type selection_set_id: str
        :param selection_diff: The diff of the previous selection and the new one.
        :type selection_diff: list
        """
        removed = len(selection_data_holder.check_if_selection_in_set(selection_diff)) == 0
        selection_color = avg.Color(SelectionColorMapper.get_next_selection_color(selection_set_id))
        if removed and len(selection_data_holder.get_selection_set(selection_set_id)) == 0:
            SelectionColorMapper.remove_selection_id(selection_set_id)

        color = defaults.ITEM_COLOR if removed else selection_color  # DataDefaults.COLOR_SELECTED
        opacity = defaults.ITEM_OPACITY if removed else defaults.ITEM_OPACITY_SELECTED
        state = DataSelectionState.Nothing if removed else DataSelectionState.Selected

        # Set the color and for the new selected/deselected data objects of a chart.
        if isinstance(sender, ChartBase):
            data_object_ids = sender.find_data_objects(
                data_objects=sender.data_objects,
                values_to_check=selection_diff,
                key=selection_set_id.split('|')[0]
            ).keys()
            extra_colors = self.__get_original_color_for_data_objects(
                selection_data_holder=selection_data_holder,
                changed_data_object_ids=data_object_ids,
                vis_view_data_objects=sender.data_objects,
                vis_view=sender
            ) if removed else {}

            sender.change_color_for_data_objects(data_object_ids, color=color, opacity=opacity)
            # Set the color of those that are already selected new.
            for data_object_id, other_color in extra_colors.iteritems():
                sender.change_color_for_data_objects([data_object_id], color=other_color, opacity=defaults.ITEM_OPACITY_SELECTED)
            sender.change_selection_state_for_data_objects(data_object_ids, state=state)
        elif isinstance(sender, MapVisView):
            point_views = sender.find_map_point_views(
                point_views=sender.point_views,
                values_to_check=selection_diff,
                key=selection_set_id.split('|')[0]
            )
            sender.change_state_for_points(point_views, state=state, highlight_color=color)

        # Search all views that have the same data key as the sender.
        vis_views_to_notify = []
        for grid_element_div in self.__multi_view_node.grid_element_divs.itervalues():
            for vis_view in grid_element_div.child_nodes:
                if sender is vis_view:
                    continue
                if selection_set_id.split('|')[0] in vis_view.data_keys_for_selection:
                    vis_views_to_notify.append(vis_view)

        # Set the new selection for all the other vis views that have the same key to represent.
        for vis_view in vis_views_to_notify:
            selection_set = selection_data_holder.get_selection_set(selection_set_id)
            changed_object_set = vis_view.change_data_selection(
                selection_set_id=selection_set_id,
                selection_set=selection_set,
                selection_diff=selection_diff,
                addition=not removed,
                update_colors=False
            )

            in_vis_removed = len(vis_view.selection_data_holder.check_if_selection_in_set(selection_diff)) == 0
            state = DataSelectionState.Nothing if in_vis_removed else DataSelectionState.Selected
            opacity = defaults.ITEM_OPACITY if in_vis_removed else defaults.ITEM_OPACITY_SELECTED
            color = defaults.ITEM_COLOR if in_vis_removed else selection_color  # DataDefaults.COLOR_SELECTED

            if isinstance(vis_view, ChartBase):
                extra_colors = self.__get_original_color_for_data_objects(
                    selection_data_holder=vis_view.selection_data_holder,
                    changed_data_object_ids=changed_object_set,
                    vis_view_data_objects=vis_view.data_objects,
                    vis_view=vis_view
                ) if in_vis_removed else {}

                vis_view.change_color_for_data_objects(changed_object_set, color=color, opacity=opacity)
                # Set the color and the state of those that are already selected new.
                for data_object_id, other_color in extra_colors.iteritems():
                    vis_view.change_color_for_data_objects([data_object_id], color=other_color, opacity=defaults.ITEM_OPACITY_SELECTED)
                    vis_view.change_selection_state_for_data_objects([data_object_id], state=DataSelectionState.Selected)
                vis_view.change_selection_state_for_data_objects(changed_object_set, state=state)
            elif isinstance(vis_view, MapVisView):
                vis_view.change_state_for_points(changed_object_set, state=state, highlight_color=color)

    @staticmethod
    def __get_original_color_for_data_objects(selection_data_holder, changed_data_object_ids, vis_view_data_objects, vis_view):
        """
        It calculates the original color of given data objects. It controls if the changed data objects are in another
        selection and get its previous color.

        :param selection_data_holder: The selection data holder for a given vis view.
        :type selection_data_holder: SelectionDataHolder
        :param changed_data_object_ids: The data objects that were changed.
        :type changed_data_object_ids: list[str]
        :param vis_view_data_objects: All data objects from the vis view the changed data objects are checked with.
        :type vis_view_data_objects: dict[str, DataObject]
        :param vis_view: The chart this method is used on.
        :type vis_view: ChartBase
        :return: All data object ids that will need another color.
        :rtype: dict[str, avg.Color]
        """
        extra_colors = {}
        # If the selection was removed check that data objects don't get the default color though they are selected
        # through another selection.
        for key, old_selection_sets in selection_data_holder.selection_sets.iteritems():
            # Get the data objects that are selected through this selection.
            dos = vis_view.find_data_objects(
                data_objects=vis_view_data_objects,
                values_to_check=old_selection_sets,
                key=key.split('|')[0]
            )
            # If a data object is in the list of removed selections and in a list of a current selection, remove
            # it from the first one an change the color to the correct selection.
            for data_object_id in dos.iterkeys():
                if data_object_id not in changed_data_object_ids:
                    continue
                changed_data_object_ids.remove(data_object_id)
                extra_colors[data_object_id] = SelectionColorMapper.get_selection_color_for(key)

        return extra_colors

    @staticmethod
    def __get_parent_from_node_with_type(node, parent_type, end_search_type=None):
        """
        Checks if a given node is a child of a given parent type.

        :param node: The node the parents should be checked for.
        :type node: Node
        :param parent_type: The searched parent for the node.
        :type parent_type: DivNode
        :param end_search_type: If the search reaches a parent with this type, the search will be stopped.
        :type end_search_type: DivNode
        :return: The parent with the given type. If none was found its also None.
        :rtype: DivNode
        """
        parent = None
        while node and not isinstance(node, end_search_type):
            if not node.parent:
                break

            if isinstance(node.parent, parent_type):
                parent = node.parent
                break
            if isinstance(node.parent, end_search_type):
                break
            node = node.parent

        return parent

    def on_frame(self):
        """
        Needs to be called every frame of the program.
        """
        # Update all devices and their views.
        self.__device_manager.on_frame()
        for grid_element_div in self.__multi_view_node.grid_element_divs.itervalues():
            for vis_view in grid_element_div.child_nodes:
                if isinstance(vis_view, MapVisView):
                    vis_view.on_frame()

        for device_view in self.__devices_current_views.itervalues():
            device_view.on_frame()

    def reset(self):
        """
        Allows that the whole view will be reset:
        All selections, all aid lines will be removed and all details views will be hidden.
        """
        for grid_element_div in self.__multi_view_node.grid_element_divs.values():
            for vis_view in grid_element_div.child_nodes:
                if isinstance(vis_view, ChartBase) or isinstance(vis_view, MapVisView):
                    vis_view.remove_all_selections()
                if isinstance(vis_view, ChartBase):
                    vis_view.reset_aid_line_controller()
                elif isinstance(vis_view, MapVisView):
                    vis_view.draw_map()
