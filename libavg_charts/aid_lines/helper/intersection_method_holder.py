from libavg.avg import Node
from libavg_charts.charts.chart_basis.chart_base import ChartBase


class IntersectionMethodHolder(object):
    # dict: key -> tuple[diagram type, line orientation]     value -> function
    __intersection_methods = {}

    @staticmethod
    def add_intersection_method(diagram_type, line_orientation, intersection_method):
        """
        Adds a new method to the IntersectionMethodHolder.

        :param diagram_type: The type of the diagram the data objects are from.
        :type diagram_type: type
        :param line_orientation: The orientation of the line that should be checked for intersections.
        :type line_orientation: Orientation
        :param intersection_method: The method that will be called with the other given parameter.
        :type intersection_method: function(dataObjects:list[Node], line_pos:float)
        """
        if not issubclass(diagram_type, ChartBase):
            raise AttributeError("IntersectionMethodHolder.add_intersection_method(): The argument 'diagram_type' is not a subclass from 'ChartBase'!")

        key = (diagram_type, line_orientation)
        IntersectionMethodHolder.__intersection_methods[key] = intersection_method

    @staticmethod
    def get_intersections_with_data_objects(diagram_type, line_orientation, data_objects, data_object_nodes, line_pos, only_at_data_points):
        """
        Calculates all intersections of a line with data objects of an chart.

        :param diagram_type: The type of the diagram the data objects are from.
        :type diagram_type: type
        :param line_orientation: The orientation of the line that should be checked for intersections.
        :type line_orientation: Orientation
        :param data_objects: The data objects in the chart.
        :type data_objects: dict[str, DataObject]
        :param data_object_nodes: The nodes of the data objects in the chart.
        :type data_object_nodes: dict[str, Node]
        :param line_pos: The necessary position of the node of the line according to the orientation.
        :type line_pos: float
        :param only_at_data_points: Only return intersection that are lying on data points on a item (if true).
        :type: bool
        :return: All nodes that were intersect through the line and the positions according to the line orientation of the intersections.
        :rtype: dict[str, list[float]]
        """
        key = (diagram_type, line_orientation)
        if key not in IntersectionMethodHolder.__intersection_methods:
            return {}

        return IntersectionMethodHolder.__intersection_methods[key](data_objects, data_object_nodes, line_pos, only_at_data_points)
