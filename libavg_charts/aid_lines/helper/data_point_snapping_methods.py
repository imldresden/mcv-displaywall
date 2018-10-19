from libavg.avg import RectNode, CircleNode, PolyLineNode
from libavg_charts.aid_lines.helper.data_point_snapping_method_holder import DataPointSnappingMethodHolder
from libavg_charts.axis.chart_axis_enums import Orientation
from libavg_charts.charts.bar_chart import BarChart
from libavg_charts.charts.bar_chart_special import *
from libavg_charts.charts.line_chart import LineChart
from libavg_charts.charts.parallel_coordinates_plot import ParallelCoordinatesPlot
from libavg_charts.charts.scatter_plot import ScatterPlot


def add_snapping_methods_to_method_holder():
    """
    Adds the default methods to the DataPointSnappingMethodHolder.
    """
    DataPointSnappingMethodHolder.add_snapping_method(LineChart, Orientation.Horizontal, get_snapping_pos_line_chart_horizontal)
    DataPointSnappingMethodHolder.add_snapping_method(LineChart, Orientation.Vertical, get_snapping_pos_line_chart_vertical)


def get_snapping_pos_line_chart_horizontal(data_objects, line_pos):
    """
    Calculates the nearest pos of and objects from a line chart with an horizontal line.

    :param data_objects: The nodes of the data objects in the chart.
    :type data_objects: dict[str, PolyLineNode]
    :param line_pos: The necessary position of the node of the line according to the orientation.
    :type line_pos: float
    :return: The nearest pos (y) of an data object in the given chart.
    :rtype: float
    """
    nearest_pos = []
    for node in data_objects.itervalues():
        nearest_pos.append(sorted(node.pos, key=lambda pos: abs(line_pos - pos[1]))[0])
    return sorted(nearest_pos, key=lambda pos: abs(line_pos - pos[1]))[0][1]


def get_snapping_pos_line_chart_vertical(data_objects, line_pos):
    """
    Calculates the nearest pos of and objects from a line chart with an vertical line.

    :param data_objects: The nodes of the data objects in the chart.
    :type data_objects: dict[str, PolyLineNode]
    :param line_pos: The necessary position of the node of the line according to the orientation.
    :type line_pos: float
    :return: The nearest pos (x) of an data object in the given chart.
    :rtype: float
    """
    nearest_pos = []
    for node in data_objects.itervalues():
        nearest_pos.append(sorted(node.pos, key=lambda pos: abs(line_pos - pos[0]))[0])
    return sorted(nearest_pos, key=lambda pos: abs(line_pos - pos[0]))[0][0]
