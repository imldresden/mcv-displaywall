from libavg import avg

from data_models.data_enums import DataSelectionState
from data_models.data_enums import ListAction
from events.event_dispatcher import EventDispatcher
from image_map_provider import ImageMapProvider
from map_point_view import MapPointView
from map_views.controls.geo_coord_mapper import GeoCoordMapper
from map_views.model.map_point import MapPoint
from world_map_svg_provider import WorldMapProvider


class MapView(avg.DivNode, EventDispatcher):
    __POINTS_SELECTED = "pointsSelected"
    __POINT_DESELECTED = "pointDeselected"

    def __init__(self, map_model, size, parent, map_provider, country_list=None, **kwargs):
        """
        :param map_model: The model this view is based on.
        :type map_model: MapModel
        :param parent: The parent this view should be shown in.
        :type parent: DivNode
        :param geo_cord_border: Border for the data points of the map. (left, top, right, bottom)
        :type geo_cord_border: tuple
        """
        super(MapView, self).__init__(**kwargs)
        self.registerInstance(self, parent)
        EventDispatcher.__init__(self)
        self.subscribe(avg.Node.KILLED, self.__on_self_killed)

        self.__map_model = map_model
        self.__map_model.start_listening(points_changed=self.__on_points_changed)

        self.__map_provider = map_provider
        if isinstance(self.__map_provider, ImageMapProvider):
            self.__map_provider.start_listening(image_moved=self.__on_background_resized)
        self.__geo_coord_mapper = GeoCoordMapper()

        self.__size = size
        self.__background_div = avg.DivNode(parent=self, size=size)
        self.__point_div = avg.DivNode(parent=self)
        self.__point_detail_div = avg.DivNode(parent=self)
        self.__point_views = []

        self.__country_list = [] if not country_list else country_list
        self.update(country_list=country_list)

        self.size = size
        self.crop = True

    def __on_self_killed(self):
        """
        Called when this node itself was killed through unlink(True).
        """
        for point in self.__point_views:
            point.unlink(True)
        self.__point_views = []

        self.__point_div.unlink(True)
        self.__point_div = None
        self.__background_div.unlink(True)
        self.__background_div = None
        self.__point_detail_div.unlink(True)
        self.__point_detail_div = None

    @property
    def point_views(self):
        """
        :rtype: list[MapPointView]
        """
        return self.__point_views

    @property
    def size(self):
        return super(MapView, self).size

    @size.setter
    def size(self, size):
        self.__map_provider.resize(size=size)

    def update(self, country_list=None):
        """
        Change the view of this map according to the given country list.

        :param country_list: A lits of all alpha2 country codes of countries that should be shown.
        :type country_list: list
        """
        self.__country_list = country_list
        self.__set_background(country_list=country_list)
        self.__set_map_data(country_list=country_list)

    def __on_background_resized(self, sender, offset, scale_factor):
        self.__geo_coord_mapper.set_map_coord_offset(offset)
        self.__geo_coord_mapper.set_map_scale_factor(scale_factor)
        self.__geo_coord_mapper.set_background_image_original_properties(self.__map_provider.get_image_values())

        for point_view in self.__point_views:
            point_view.update_position(self.__geo_coord_mapper)
            point_view.update_scale(scale_factor)

    def __set_background(self, country_list):
        """
        Creates a view for the background. This will be created through the WorldMapProvider and is yet only the
        european region.

        :param country_list: The list of all countries that should be created through this map.
        :type country_list: list
        """
        if self.__background_div:
            self.__background_div.unlink(True)
        self.__background_div = avg.DivNode(parent=self, size=self.__size)

        if isinstance(self.__map_provider, WorldMapProvider):
            self.__map_provider.place_scaled_country_images(
                country_list=country_list,
                parent=self.__background_div,
                size=self.__background_div.size
            )
        else:
            self.__map_provider.place_image(
                parent=self.__background_div,
                size=self.__background_div.size
            )
        print "background image loaded and placed"

    def __set_map_data(self, country_list):
        """
        Creates the view according to the given model. The old view will be deleted.

        :param country_list: The list of all countries whose points should be displayed.
        :type country_list: list
        """
        if self.__map_model is None:
            return

        self.__geo_coord_mapper.set_map_coord_offset(self.__map_provider.current_offset)
        self.__geo_coord_mapper.set_map_scale_factor(self.__map_provider.current_scale_factor)
        self.__geo_coord_mapper.set_background_image_original_properties(self.__map_provider.get_image_values())

        # Delete the old point views.
        for point_view in self.__point_views:
            point_view.unlink(True)
        self.reorderChild(self.__point_div, self.getNumChildren()-1)
        self.reorderChild(self.__point_detail_div, self.getNumChildren() - 1)

        # Create the new point views.
        print "started calculating map data positions"
        for point in self.__map_model.points:
            if country_list is None or point.country_code in country_list:
                new_point_view = MapPointView(
                    point_model=point,
                    geo_coord_mapper=self.__geo_coord_mapper,
                    parent=self.__point_div,
                    detail_parent=self.__point_detail_div
                )
                self.__point_views.append(new_point_view)
                point.start_listening(selection_state_changed=self.__on_point_element_state_changed)

    def __on_points_changed(self, sender, action, elements):
        if action == ListAction.added:
            for element in elements:
                new_point_view = MapPointView(
                    point_model=element,
                    geo_coord_mapper=self.__geo_coord_mapper,
                    parent=self.__point_div,
                    detail_parent=self.__point_detail_div
                )
                self.__point_views.append(new_point_view)
        elif action == ListAction.removed:
            to_remove = []
            for element in elements:
                for point_view in self.__point_views:
                    if point_view.point_model is element:
                        to_remove.append(point_view)
                        break
            for point_view in to_remove:
                self.__point_views.remove(point_view)
                point_view.unlink()

    def __on_point_element_state_changed(self, sender, element_state, highlight_color=None):
        """
        Called when the element state of a point has changed.

        :type sender: MapPoint
        :param element_state: The new state of the point.
        :type element_state: DataSelectionState
        """
        map_point_views = [v for v in self.__point_views if v.point_model is sender]
        if len(map_point_views) == 0:
            return

        if element_state is DataSelectionState.Selected:
            self.dispatch(self.__POINTS_SELECTED, sender=self, points=[map_point_views[0]])
        elif element_state is DataSelectionState.Nothing:
            self.dispatch(self.__POINT_DESELECTED, sender=self, point=map_point_views[0])

    def move_point_view_in_the_foreground(self, point):
        """
        Moves a given point div in the front of the points_div.

        :param point: The point to move.
        :type point: MapPointView
        """
        if point not in self.__point_views:
            return

        self.__point_div.reorderChild(point, self.__point_div.getNumChildren() - 1)
        if point.detail_view:
            self.__point_detail_div.reorderChild(point.detail_view, self.__point_detail_div.getNumChildren() - 1)

    def start_listening(self, points_selected=None, point_deselected=None):
        """
        Registers a callback to listen to changes to this map view. Listeners can register to any number of the provided
        events. For the required structure of the callbacks see below.

        :param points_selected: Called when a set of points are selected.
        :type points_selected: function(sender:MapView, points:list[MapPointView])
        :param point_deselected: Called when a point is deselected.
        :type point_deselected: function(sender:MapView, point:MapPointView)
        """
        self.bind(self.__POINTS_SELECTED, points_selected)
        self.bind(self.__POINT_DESELECTED, point_deselected)

    def stop_listening(self, points_selected=None, point_deselected=None):
        """
        Stops listening to an event the listener has registered to previously. The provided callback needs to be the
        same that was used to listen to the event in the fist place.

        :param points_selected: Called when a set of points are selected.
        :type points_selected: function(sender:MapView, points:list[MapPointView])
        :param point_deselected: Called when a point is deselected.
        :type point_deselected: function(sender:MapView, point:MapPointView)
        """
        self.unbind(self.__POINTS_SELECTED, points_selected)
        self.unbind(self.__POINT_DESELECTED, point_deselected)
