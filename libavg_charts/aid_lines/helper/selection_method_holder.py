from enum import Enum
from libavg.avg import Node
from libavg_charts.charts.chart_basis.chart_base import ChartBase


class SelectionTypes(Enum):
    """
    The possible selection types through the aid line controller.
    """
    HorizontalLine = 0
    VerticalLine = 1
    Rectangle = 2
    Circle = 3
    Lasso = 4


class SelectionMethodHolder(object):
    # dict: key -> tuple[diagram type, selection type]     value -> function
    __selection_methods = {}

    @staticmethod
    def add_selection_method(diagram_type, selection_type, selection_method):
        """
        Adds a new method to the SelectionMethodHolder.

        :param diagram_type: The type of the diagram the data objects are from.
        :type diagram_type: type
        :param selection_type: The selection type that is used for this method.
        :type selection_type: SelectionTypes
        :param selection_method: The method that will be called with the other given parameter.
        :type selection_method: function(dataObjects:list[Node], ???)
        """
        if not issubclass(diagram_type, ChartBase):
            raise AttributeError("SelectionMethodHolder.add_selection_method(): The argument 'diagram_type' is not a subclass from 'ChartBase'!")

        key = (diagram_type, selection_type)
        SelectionMethodHolder.__selection_methods[key] = selection_method

    @staticmethod
    def get_selection_from_data_objects(diagram_type, selection_type, data_object_nodes, value1, value2):
        """
        Calculates all selected objects from a chart.

        :param diagram_type: The type of the diagram the data objects are from.
        :type diagram_type: type
        :param selection_type: The selection type that is used for this method.
        :type selection_type: SelectionTypes
        :param data_object_nodes: The nodes with their keys of the data objects in the chart.
        :type data_object_nodes: dict[str, Node]
        :param value1: The first value needed.
                       For a selection through a rectangle this is one side.
                       For a selection through a circle this is the pos of the circle.
                       For a selection through a lasso this is the polyline pos of the lasso.
        :type value1: object
        :param value2: The second value needed.
                       For a selection through a rectangle this is the parallel other side of its.
                       For a selection through a circle this is the radius of the circle.
                       For a selection through a lasso this is None.
        :type value2: object
        :return: All nodes that were selected.
        :rtype: dict[str, Node]
        """
        key = (diagram_type, selection_type)
        if key not in SelectionMethodHolder.__selection_methods:
            return {}

        return SelectionMethodHolder.__selection_methods[key](data_object_nodes, value1, value2)
