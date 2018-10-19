import networkx as nx

from data_models.data_enums import ListAction


class Map(object):

    def __init__(self):
        self.__graph = nx.Graph()
        # nodes are handled separately because NetworkX always only return a copy of all nodes when 'nodes()' is called
        # and the instance of the node list needs to be consistent to work in a satisfactory way with the modification
        # controller, further the list needs to be observable to make sure external changes will be noticed by the
        # modification controller
        self.__points = []

        self.__country_data = {}
        self.__callback_points_changed = []
        self.__callback_country_data_changed = []

    @property
    def internal_graph(self):
        """
        :rtype: nx.Graph
        """
        return self.__graph

    @property
    def points(self):
        """
        :rtype: list[Point]
        """
        return self.__points

    @property
    def country_data(self):
        """
        :rtype: list[MultivariateDataObject]
        """
        return self.__country_data

    @country_data.setter
    def country_data(self, country_data):
        """
        :type country_data: list[MultivariateDataObject]
        """
        self.__country_data = country_data

    def add_point(self, point, dispatch=True):
        """
        Adds a point to this map.

        :param point: The point to add.
        :type point: Point
        :param dispatch: Should this dispatch the event for "points changed"?
        :type dispatch: bool
        """
        self.__graph.add_node(point)
        self.__points.append(point)
        for callback in self.__callback_points_changed:
            callback(sender=self, action=ListAction.added, elements=[point])

    def remove_point(self, point, dispatch=True):
        """
        Removes a point from this map.

        :param point: The point to remove.
        :type point: Point
        :param dispatch: Should this dispatch the event for "points changed"?
        :type dispatch: bool
        """
        self.__graph.remove_node(point)
        self.__points.remove(point)
        for callback in self.__callback_points_changed:
            callback(sender=self, action=ListAction.removed, elements=[point])

    def clear(self, dispatch=True):
        """
        Removed all points from this map.

        :param dispatch: Should this dispatch the event for "points changed"?
        :type dispatch: bool
        """
        old_points = self.__points
        self.__points = []
        self.__graph.clear()
        for callback in self.__callback_points_changed:
            callback(sender=self, action=ListAction.removed, elements=[old_points])

    def start_listening(self, points_changed=None, country_data_changed=None):
        """
        Registers a callback to listen to changes to this map. Listeners can register to any number of the provided
        events. For the required structure of the callbacks see below.

        :param points_changed: Called whenever a point in this map is deleted or added.
        :type points_changed: function(sender:Map, action:ListAction, elements:[Point])
        :param country_data_changed: Called whenever the data for the countries has changed.
        :type country_data_changed: function(sender:Map, new_country_data:dict)
        """
        if points_changed is not None and points_changed not in self.__callback_points_changed:
            self.__callback_points_changed.append(points_changed)
        if country_data_changed is not None and country_data_changed not in self.__callback_country_data_changed:
            self.__callback_country_data_changed.append(country_data_changed)

    def stop_listening(self, points_changed=None, country_data_changed=None):
        """
        Stops listening to an event the listener has registered to previously. The provided callback needs to be the
        same that was used to listen to the event in the fist place.

        :param points_changed: Called whenever a point in this map is deleted or added.
        :type points_changed: function(sender:Map, action:ListAction, elements:[Point])
        :param country_data_changed: Called whenever the data for the countries has changed.
        :type country_data_changed: function(sender:Map, new_country_data:dict)
        """
        if points_changed is not None:
            self.__callback_points_changed.remove(points_changed)
        if country_data_changed is not None:
            self.__callback_country_data_changed.remove(country_data_changed)
