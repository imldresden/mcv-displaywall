from libavg.avg import Node
from libavg_charts.charts.chart_basis.chart_base import ChartBase


class DataPointSnappingMethodHolder(object):
    # dict: key -> tuple[diagram type, line orientation]     value -> function
    __snapping_methods = {}

    @staticmethod
    def add_snapping_method(diagram_type, line_orientation, snapping_method):
        """
        Adds a new method to the IntersectionMethodHolder.

        :param diagram_type: The type of the diagram the data objects are from.
        :type diagram_type: type
        :param line_orientation: The orientation of the line that should be checked for the snapping.
        :type line_orientation: Orientation
        :param snapping_method: The method that will be called with the other given parameter.
        :type snapping_method: function(dataObjects:list[Node], line_pos:float)
        """
        if not issubclass(diagram_type, ChartBase):
            raise AttributeError("DataPointSnappingMethodHolder.add_snapping_method(): The argument 'diagram_type' is not a subclass from 'ChartBase'!")

        key = (diagram_type, line_orientation)
        DataPointSnappingMethodHolder.__snapping_methods[key] = snapping_method

    @staticmethod
    def get_snapping_with_data_objects(diagram_type, line_orientation, data_objects, line_pos):
        """
        Calculates the nearest data point of an aid line for the snapping.

        :param diagram_type: The type of the diagram the data objects are from.
        :type diagram_type: type
        :param line_orientation: The orientation of the line that should be checked for the snapping.
        :type line_orientation: Orientation
        :param data_objects: The nodes of the data objects in the chart.
        :type data_objects: dict[str, Node]
        :param line_pos: The necessary position of the node of the line according to the orientation.
        :type line_pos: float
        :return: The nearest data point for the given aid line. If no method was found it will be None.
        :rtype: float
        """
        key = (diagram_type, line_orientation)
        if key not in DataPointSnappingMethodHolder.__snapping_methods:
            return None

        return DataPointSnappingMethodHolder.__snapping_methods[key](data_objects, line_pos)
