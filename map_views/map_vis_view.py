from collections import namedtuple

from libavg import avg, gesture

from configs import config_app
from configs.config_recognizer import CommonRecognizerDefaults
from data_models.data_enums import DataSelectionState
from libavg_charts.configurations.text_label_configuration import TextMarkingConfiguration
from libavg_charts.utils.default_values import DataDefaults
from model import map_provider
from selection_ctrl.lasso_selection_div import LassoSelectionDiv
# imports selection
from selection_ctrl.selection_control import SelectionControl
from selection_ctrl.selection_data_holder import SelectionDataHolder
from views.map_view import MapView
from map_views.views.image_map_provider import ImageMapProvider
from libavg_charts.configurations.chart_configuration import ChartConfiguration
from libavg_charts.charts.chart_enums import LabelPosition

GeoCoord = namedtuple("GeoCoord", "lat long")
MapImageInfo = namedtuple("MapImageInfo", "filename resolution min_geo max_geo")


class MapVisView(avg.DivNode):

    def __init__(self, data_object_list, image_info, data_keys_for_selection, selection_label_text_config=None,
                 size=(0, 0), view_id=-1, label="", chart_config=None, parent=None, **kwargs):
        super(MapVisView, self).__init__(**kwargs)
        self.registerInstance(self, parent)

        self._chart_config = chart_config if chart_config else ChartConfiguration()

        self._selection_label_text_config = selection_label_text_config or TextMarkingConfiguration()
        self._view_id = view_id
        self.__size = avg.Point2D(size)
        self.__callback_content_changed = []
        self.__callback_selection_changed = []

        self.__label = label
        self._label_div = None
        self._label_node = None

        self.__map = map_provider.create_map_from_data(data_object_list=data_object_list)
        self.__map_background_provider = ImageMapProvider(
            filename=image_info.filename, img_dimensions=image_info.resolution,
            min_geo=(image_info.min_geo.long, image_info.min_geo.lat),
            max_geo=(image_info.max_geo.long, image_info.max_geo.lat)
        )
        self.__trans_recognizer = None

        self.__navigation_state = False

        self.__map_view = None
        self.__selection_control = None
        self.__lasso_div = None
        self.__background_tap_recognizer = None

        # key -> event id     value -> tuple: start time, pos
        self.__hold_events = {}

        self._data_keys_for_selection = data_keys_for_selection
        self._selection_data_holder = SelectionDataHolder(data_keys_for_selection)

    def __repr__(self):
        return "M {}: \"{}\"".format(self._view_id, "")

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
    def data_keys_for_selection(self):
        """
        :rtype: list[str]
        """
        return self._data_keys_for_selection

    @property
    def size(self):
        return self.__size

    @size.setter
    def size(self, size):
        self.__size = size
        if self.__map_view:
            self.__map_view.size = size

    @property
    def selection_data_holder(self):
        """
        :rtype: SelectionDataHolder
        """
        return self._selection_data_holder

    @property
    def point_views(self):
        """
        :rtype: list[MapPointView]
        """
        return self.__map_view.point_views

    @property
    def map_background_provider(self):
        """
        :rtype: ImageMapProvider
        """
        return self.__map_background_provider

    def __draw_label(self, label):
        """
        Draws the label for this chart.
        """
        if self._label_node is not None:
            self._label_node.unlink(True)
        if self._label_div is not None:
            self._label_div.unlink(True)

        if not self._chart_config.show_label:
            return

        self._label_div = avg.DivNode(parent=self)
        rect_node = avg.RectNode(
            parent=self._label_div,
            fillcolor='fff',
            fillopacity=1.0,
            # size=(self.size[0], )
        )
        self._label_node = avg.WordsNode(
            # parent=self,
            parent=self._label_div,
            text=label,
            alignment="center",
            fontsize=self._chart_config.label_text_config.font_size,
            color=self._chart_config.label_text_config.color,
            rawtextmode=True
        )

        paddingless_size = (self.__size[0] - self._chart_config.padding_left - self._chart_config.padding_right,
                            self.__size[1] - self._chart_config.padding_top - self._chart_config.padding_bottom)

        self._label_node.pos = (
            self._chart_config.padding_left + paddingless_size[0] / 2,
            self._chart_config.padding_top -
            (self._chart_config.label_text_config.offset_to_other_element + self._label_node.size[1]))

        if self._chart_config.label_pos is LabelPosition.Top:
            rect_node.size = (self.__size[0], self._label_node.pos[1] + self._label_node.size[1])
        else:
            rect_node.size = (self.__size[0], self._chart_config.padding_bottom + self._label_node.size[1])
            self._label_div.pos = (0, self.size[1] - rect_node.size[1])

    def draw_map(self):
        """
        Draws the map if called.
        """
        self.__size = avg.Point2D(self.size)

        if self.__map_view is not None:
            self.__lasso_div.unlink(True)
            self.__map_view.unlink(True)

        self.__map_view = MapView(
            map_model=self.__map,
            map_provider=self.__map_background_provider,
            parent=self,
            size=self.__size
        )

        # setup selection
        self.__selection_control = SelectionControl(
            elements=self.__map.points, div=self.__map_view, relative_div=self.__map_view
        )
        self.__lasso_div = LassoSelectionDiv(
            selection_control=self.__selection_control, parent=self.__map_view, size=self.__size
        )

        self.__background_tap_recognizer = gesture.DoubletapRecognizer(
            node=self.__lasso_div,
            maxTime=CommonRecognizerDefaults.DOUBLE_TAP_MAX_TIME,
            maxDist=CommonRecognizerDefaults.DOUBLE_TAP_MAX_DIST,
            detectedHandler=self.__on_background_tap
        )
        self.__trans_recognizer = gesture.TransformRecognizer(
            eventNode=self.__lasso_div,
            moveHandler=self.__on_transform,
            endHandler=self.__on_transform_end
        )

        self.__map_view.reorderChild(self.__lasso_div, 1)  # recognition placed between map image and data points
        self.__lasso_div.start_listening(
            selection_changed=lambda sender, selected_nodes: self.__on_points_selected(sender, [pv for pv in self.point_views if pv.point_model in selected_nodes], True)
        )

        self.__map_view.start_listening(
            points_selected=self.__on_points_selected,
            point_deselected=self.__on_point_deselected
        )

        self.__draw_label(self.__label)

        for callback in self.__callback_content_changed:
            callback(sender=self, content=self.__map)

    @property
    def content(self):
        return self.__map

    def start_listening(self, content_changed=None, selection_changed=None):
        if content_changed is not None and content_changed not in self.__callback_content_changed:
            self.__callback_content_changed.append(content_changed)
        if selection_changed is not None and selection_changed not in self.__callback_selection_changed:
            self.__callback_selection_changed.append(selection_changed)

    def change_data_selection(self, selection_set_id, selection_set, selection_diff, addition, update_colors=True):
        """
        Updates the selection for this view.

        :param selection_set_id: The id of the selection set.
        :type selection_set_id: str
        :param selection_set: The new current selection set.
        :type selection_set: list
        :param selection_diff: The diff between the new and the old selection set.
        :type selection_diff: list
        :param update_colors: Should the colors be updated to the defaults values?
        :type update_colors: bool
        :return: All nodes that were affected through the change.
        :rtype: list[Node]
        """
        point_views = self.find_map_point_views(
            point_views=self.__map_view.point_views,
            values_to_check=selection_diff,
            key=selection_set_id.split('|')[0]
        )
        # Create new selection set.
        if not self._selection_data_holder.get_selection_set(selection_set_id):
            self.change_state_for_points(points=point_views, state=DataSelectionState.Selected)
            state = DataSelectionState.Selected
            color = DataDefaults.COLOR_SELECTED
            self.change_state_for_points(points=point_views, state=state, highlight_color=color)
            self._selection_data_holder.add_new_selection_set(
                selection_set=selection_set,
                selection_set_id=selection_set_id
            )
            point_views = self.find_map_point_views(
                point_views=self.__map_view.point_views,
                values_to_check=self._selection_data_holder.get_selection_set(selection_set_id),
                key=selection_set_id.split('|')[0]
            )
        # Update the existing one: Add the diff
        elif addition:
            self.change_state_for_points(points=point_views, state=DataSelectionState.Selected)
            state = DataSelectionState.Selected
            color = DataDefaults.COLOR_SELECTED
            self._selection_data_holder.add_selection_to_set(
                selection_set=selection_diff,
                selection_set_id=selection_set_id
            )
            point_views = self.find_map_point_views(
                point_views=self.__map_view.point_views,
                values_to_check=self._selection_data_holder.get_selection_set(selection_set_id),
                key=selection_set_id.split('|')[0]
            )
        # Update the existing one: Remove the diff
        else:  # not addition:
            self.change_state_for_points(points=point_views, state=DataSelectionState.Nothing)
            state = DataSelectionState.Nothing
            color = DataDefaults.COLOR
            self._selection_data_holder.remove_selection_from_set(
                selection_set=selection_diff,
                selection_set_id=selection_set_id
            )
            if self._selection_data_holder.empty:
                point_views = [pv for pv in self.__map_view.point_views if
                               selection_set_id.split('|')[0] in pv.point_model.attribute_dict]
            else:
                point_views = self.find_map_point_views(
                    point_views=self.__map_view.point_views,
                    values_to_check=selection_diff,
                    key=selection_set_id.split('|')[0]
                )

        if update_colors:
            self.change_state_for_points(points=point_views, state=state, highlight_color=color)

        return point_views

    def remove_all_selections(self):
        """
        Removes all selections from this chart.
        """
        self.__on_background_tap()

    def change_state_for_points(self, points, state, highlight_color=None):
        """
        Changes the color of the given node.

        :param points: The nodes in this map to change.
        :type points: list[MapPointView]
        :param state: The state to change the data objects to.
        :type state: DataSelectionState
        """
        for point in points:
            point.point_model.set_element_state(sender=self, element_state=state, highlight_color=highlight_color)
            if state is DataSelectionState.Selected:
                self.__map_view.move_point_view_in_the_foreground(point)

    def __on_points_selected(self, sender, points, lasso_selection=False):
        """
        Called when points in the map view have been selected.

        :type sender: MapView
        :param points: The point views.
        :type points: list[MapPointView]
        :param lasso_selection: Is this selection caused through a lasso?
        :type lasso_selection: bool
        """
        selection_sets = {}
        for point in points:
            if point in self.__map_view.point_views:
                point.point_model.set_element_state(DataSelectionState.Selected, sender=self)
                for key in self._data_keys_for_selection:
                    if key not in point.point_model.attribute_dict:
                        continue

                    if key not in selection_sets:
                        selection_sets[key] = []
                    selection_sets[key].append([point.point_model.attribute_dict[key]])
                    break

        for selection_key, selection_set in selection_sets.iteritems():
            selection_id = self._selection_data_holder.get_next_id(selection_key)
            if not selection_id:
                return

            selection_id, selection_diff = self._selection_data_holder.add_new_selection_set(
                selection_set=selection_set,
                selection_set_id=selection_id,
                single_selection=lasso_selection
            )

            for callback in self.__callback_selection_changed:
                callback(
                    sender=self,
                    selection_data_holder=self._selection_data_holder,
                    selection_set_id=selection_id,
                    selection_diff=selection_diff
                )

    def __on_point_deselected(self, sender, point):
        """
        Called when a point was deselected from the map view.

        :type sender: MapView
        :param point: The point views.
        :type point: MapPointView
        """
        selection_set = []
        for key in self._data_keys_for_selection:
            if key not in point.point_model.attribute_dict:
                continue
            selection_set.append([point.point_model.attribute_dict[key]])
            break

        selection_diffs = {}
        selection_ids = self._selection_data_holder.check_if_selection_in_set(selection_set)
        for selection_id in selection_ids:
            selection_diffs[selection_id] = self._selection_data_holder.remove_selection_from_set(
                selection_set_id=selection_id,
                selection_set=selection_set
            )

        for selection_id, selection_diff in selection_diffs.iteritems():
            for callback in self.__callback_selection_changed:
                callback(
                    sender=self,
                    selection_data_holder=self._selection_data_holder,
                    selection_set_id=selection_id,
                    selection_diff=selection_diff
                )

    def __on_background_tap(self):
        """
        Called when a tap on the background has happened.
        """
        selection_diffs = self._selection_data_holder.remove_all_selection_sets()

        for selection_id, selection_diff in selection_diffs.iteritems():
            point_views = self.find_map_point_views(
                point_views=self.__map_view.point_views,
                values_to_check=selection_diff,
                key=selection_id.split('|')[0]
            )
            self.change_state_for_points(point_views, DataSelectionState.Nothing, highlight_color=DataDefaults.COLOR)

            for callback in self.__callback_selection_changed:
                callback(
                    sender=self,
                    selection_data_holder=self._selection_data_holder,
                    selection_set_id=selection_id,
                    selection_diff=selection_diff
                )

    def __on_transform(self, transform):
        """
        Called when a trans form on the map has started.

        :type transform: avg.Transform
        """
        if not config_app.zoom_enabled and not config_app.pan_enabled:
            return

        if len(self.__trans_recognizer.contacts) >= 2:
            # Get the rel position of all contacts
            contact_pos = [c.getRelPos(self.__map_view, c.events[-1].pos) for c in self.__trans_recognizer.contacts]

            for pos_a in contact_pos:
                for pos_b in contact_pos:
                    # Don't compare a point to itself.
                    if pos_a == pos_b:
                        continue
                    # Check if the distance between two contacts is less than a given value.
                    if ((CommonRecognizerDefaults.TWO_CONTACT_MAX_DIST_CM * config_app.pixel_per_cm) ** 2 >=
                        (pos_a[0] - pos_b[0]) ** 2 + (pos_a[1] - pos_b[1]) ** 2):
                        self.__navigation_state = True
                        break
                if self.__navigation_state:
                    break

            # Set the lasso selection divs activation.
            if self.__lasso_div:
                self.__lasso_div.selection_active = not self.__navigation_state
            # If the navigation mode is activated transform the whole map.
            if self.__navigation_state:
                self.__map_background_provider.transform(
                    translation=transform.trans if config_app.pan_enabled else (0, 0),
                    scale=transform.scale if config_app.zoom_enabled else 1,
                    pivot=transform.pivot
                )
        else:
            self.__navigation_state = False
            if self.__lasso_div:
                self.__lasso_div.selection_active = not self.__navigation_state

    def __on_transform_end(self):
        """
        Called when the transform is ended.
        """
        if self.__lasso_div:
            self.__lasso_div.selection_active = True

    def find_map_point_views(self, point_views, values_to_check, key):
        """
        Checks a list of nodes if there are objects that contain values from the selections et.

        :param point_views: The nodes to check in.
        :type point_views: list[MapPointView]
        :param values_to_check: The selection set that should be checked for.
        :type values_to_check: list
        :param key: The key that is used to check the data objects.
        :type key: str
        :return: All nodes that contain a value from the selection set.
        :rtype: list[MapPointView]
        """
        if key not in self._data_keys_for_selection:
            return []

        found_point_views = []
        for point_view in point_views:
            if key not in point_view.point_model.attribute_dict:
                continue

            if point_view.point_model.attribute_dict[key] in values_to_check or [point_view.point_model.attribute_dict[key]] in values_to_check:
                found_point_views.append(point_view)

        return found_point_views

    def on_frame(self):
        pass
