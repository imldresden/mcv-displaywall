from libavg.avg import RectNode, CircleNode, PolyLineNode
from data_models.data_enums import DataSelectionState
from libavg_charts.aid_lines.helper.intersection_method_holder import IntersectionMethodHolder
from libavg_charts.axis.chart_axis_enums import Orientation
from libavg_charts.charts.bar_chart import BarChart
from libavg_charts.charts.bar_chart_special import *
from libavg_charts.charts.line_chart import LineChart
from libavg_charts.charts.parallel_coordinates_plot import ParallelCoordinatesPlot
from libavg_charts.charts.scatter_plot import ScatterPlot


def add_intersections_methods_to_method_holder():
    """
    Adds the default methods to the IntersectionMethodHolder.
    """
    IntersectionMethodHolder.add_intersection_method(LineChart, Orientation.Horizontal, get_intersection_line_chart_horizontal)
    IntersectionMethodHolder.add_intersection_method(LineChart, Orientation.Vertical, get_intersection_line_chart_vertical)
    IntersectionMethodHolder.add_intersection_method(BarChartBase, Orientation.Horizontal, get_intersection_bar_chart_horizontal)
    IntersectionMethodHolder.add_intersection_method(BarChartBase, Orientation.Vertical, get_intersection_bar_chart_vertical)
    IntersectionMethodHolder.add_intersection_method(BarChart, Orientation.Horizontal, get_intersection_bar_chart_horizontal)
    IntersectionMethodHolder.add_intersection_method(BarChart, Orientation.Vertical, get_intersection_bar_chart_vertical)
    IntersectionMethodHolder.add_intersection_method(BarChartManyObjects, Orientation.Horizontal, get_intersection_bar_chart_horizontal)
    IntersectionMethodHolder.add_intersection_method(BarChartManyObjects, Orientation.Vertical, get_intersection_bar_chart_vertical)
    IntersectionMethodHolder.add_intersection_method(BarChartOneObject, Orientation.Horizontal, get_intersection_bar_chart_horizontal)
    IntersectionMethodHolder.add_intersection_method(BarChartOneObject, Orientation.Vertical, get_intersection_bar_chart_vertical)
    IntersectionMethodHolder.add_intersection_method(ScatterPlot, Orientation.Horizontal, get_intersection_scatter_plot_horizontal)
    IntersectionMethodHolder.add_intersection_method(ScatterPlot, Orientation.Vertical, get_intersection_scatter_plot_vertical)
    IntersectionMethodHolder.add_intersection_method(ParallelCoordinatesPlot, Orientation.Horizontal, get_intersection_parallel_coordinates_plot_horizontal)
    IntersectionMethodHolder.add_intersection_method(ParallelCoordinatesPlot, Orientation.Vertical, get_intersection_parallel_coordinates_plot_vertical)


def get_intersection_line_chart_horizontal(data_objects, data_object_nodes, line_pos, only_at_data_points):
    """
    Calculates the intersection of objects from a line chart with an horizontal line.

    :param data_objects: The data objects on the chart.
    :type data_objects: dict[str, DataObject]
    :param data_object_nodes: The nodes of the data object nodes in the chart.
    :type data_object_nodes: dict[str, PolyLineNode]
    :param line_pos: The necessary position of the node of the line according to the orientation.
    :type line_pos: float
    :param only_at_data_points: Only return intersection that are lying on data points on a item (if true).
    :type: bool
    :return: All nodes that were intersect through the line and the positions according to the line orientation of the intersections.
    :rtype: dict[str, list[tuple[float, float]]]
    """
    def line_part(y):
        """
        The method for the part of the line between two indices.

        :type y: float
        :return: The x value.
        :rtype: float
        """
        m = (current_pos[1] - last_pos[1]) / (current_pos[0] - last_pos[0])
        return (y - last_pos[1]) / m + last_pos[0]

    results = {}
    for key, node in data_object_nodes.iteritems():
        if only_at_data_points:
            results[key] = [p for p in node.pos if p[1] == line_pos]
        else:
            for i in range(1, len(node.pos)):
                last_pos = node.pos[i - 1]
                current_pos = node.pos[i]
                if not (last_pos[1] <= line_pos <= current_pos[1] or current_pos[1] <= line_pos <= last_pos[1]):
                    continue

                if key not in results:
                    results[key] = []
                results[key].append((line_part(line_pos), line_pos))

    return results


def get_intersection_line_chart_vertical(data_objects, data_object_nodes, line_pos, only_at_data_points):
    """
    Calculates the intersection of objects from a line chart with an horizontal line.

    :param data_objects: The data objects on the chart.
    :type data_objects: dict[str, DataObject]
    :param data_object_nodes: The nodes of the data object nodes in the chart.
    :type data_object_nodes: dict[str, PolyLineNode]
    :param line_pos: The necessary position of the node of the line according to the orientation.
    :type line_pos: float
    :param only_at_data_points: Only return intersection that are lying on data points on a item (if true).
    :type: bool
    :return: All nodes that were intersect through the line and the positions according to the line orientation of the intersections.
    :rtype: dict[str, list[tuple[float, float]]]
    """
    def line_part(x):
        """
        The method for the part of the line between two indices.

        :type x: float
        :return: The y value.
        :rtype: float
        """
        m = (current_pos[1] - last_pos[1]) / (current_pos[0] - last_pos[0])
        return m * (x - last_pos[0]) + last_pos[1]

    results = {}
    for key, node in data_object_nodes.iteritems():
        if only_at_data_points:
            results[key] = [p for p in node.pos if p[0] == line_pos]
        else:
            for i in range(1, len(node.pos)):
                last_pos = node.pos[i - 1]
                current_pos = node.pos[i]
                if not (last_pos[0] <= line_pos <= current_pos[0] or current_pos[0] <= line_pos <= last_pos[0]):
                    continue

                if key not in results:
                    results[key] = []
                results[key].append((line_pos, line_part(line_pos)))

    return results


def get_intersection_bar_chart_horizontal(data_objects, data_object_nodes, line_pos, only_at_data_points):
    """
    Calculates the intersection of objects from a line chart with an horizontal line.

    :param data_objects: The data objects on the chart.
    :type data_objects: dict[str, DataObject]
    :param data_object_nodes: The nodes of the data object nodes in the chart.
    :type data_object_nodes: dict[str, RectNode]
    :param line_pos: The necessary position of the node of the line according to the orientation.
    :type line_pos: float
    :param only_at_data_points: Only return intersection that are lying on data points on a item (if true).
    :type: bool
    :return: All nodes that were intersect through the line and the positions according to the line orientation of the intersections.
             The positions will be the centre of the bar on the x axes and the top on the y axes.
    :rtype: dict[str, list[tuple[float, float]]]
    """
    results = {}
    for key, node in data_object_nodes.iteritems():
        if data_objects[key].selection_state is DataSelectionState.Selected:
            continue
        if not node.pos[1] < line_pos < node.pos[1] + node.size[1]:
            continue

        if key not in results:
            results[key] = []
        results[key].append((node.pos[0] + node.size[0] / 2, node.pos[1]))

    return results


def get_intersection_bar_chart_vertical(data_objects, data_object_nodes, line_pos, only_at_data_points):
    """
    Calculates the intersection of objects from a line chart with an horizontal line.

    :param data_objects: The data objects on the chart.
    :type data_objects: dict[str, DataObject]
    :param data_object_nodes: The nodes of the data object nodes in the chart.
    :type data_object_nodes: dict[str, RectNode]
    :param line_pos: The necessary position of the node of the line according to the orientation.
    :type line_pos: float
    :param only_at_data_points: Only return intersection that are lying on data points on a item (if true).
    :type: bool
    :return: All nodes that were intersect through the line and the positions according to the line orientation of the intersections.
             The position will be the top of the bar (on the y axes) and the center on the x axes.
    :rtype: dict[str, list[tuple[float, float]]]
    """
    results = {}
    for key, node in data_object_nodes.iteritems():
        if data_objects[key].selection_state is DataSelectionState.Selected:
            continue
        if not node.pos[0] < line_pos < node.pos[0] + node.size[0]:
            continue

        if key not in results:
            results[key] = []
        results[key].append((node.pos[0] + node.size[0], node.pos[1] + node.size[1] / 2))

    return results


def get_intersection_scatter_plot_horizontal(data_objects, data_object_nodes, line_pos, only_at_data_points):
    """
    Calculates the intersection of objects from a line chart with an horizontal line.

    :param data_objects: The data objects on the chart.
    :type data_objects: dict[str, DataObject]
    :param data_object_nodes: The nodes of the data object nodes in the chart.
    :type data_object_nodes: dict[str, Node]
    :param line_pos: The necessary position of the node of the line according to the orientation.
    :type line_pos: float
    :param only_at_data_points: Only return intersection that are lying on data points on a item (if true).
    :type: bool
    :return: All nodes that were intersect through the line and the positions according to the line orientation of the intersections.
             The position will always be the center of the node.
    :rtype: dict[str, list[tuple[float, float]]]
    """
    results = {}
    for key, node in data_object_nodes.iteritems():
        if data_objects[key].selection_state is DataSelectionState.Selected:
            continue

        r = node.r if isinstance(node, CircleNode) else (node.size[0] / 2)
        if isinstance(node, CircleNode):
            pos_top = node.pos[1] - r
            pos_bottom = node.pos[1] + r
        else:
            pos_top = node.pos[1]
            pos_bottom = node.pos[1] + r * 2

        if not pos_top < line_pos < pos_bottom:
            continue

        if key not in results:
            results[key] = []
        pos = node.pos if isinstance(node, CircleNode) else (node.pos[0] + r, node.pos[1] + r)
        results[key].append(pos)

    return results


def get_intersection_scatter_plot_vertical(data_objects, data_object_nodes, line_pos, only_at_data_points):
    """
    Calculates the intersection of objects from a line chart with an horizontal line.

    :param data_objects: The data objects on the chart.
    :type data_objects: dict[str, DataObject]
    :param data_object_nodes: The nodes of the data object nodes in the chart.
    :type data_object_nodes: dict[str, Node]
    :param line_pos: The necessary position of the node of the line according to the orientation.
    :type line_pos: float
    :param only_at_data_points: Only return intersection that are lying on data points on a item (if true).
    :type: bool
    :return: All nodes that were intersect through the line and the positions according to the line orientation of the intersections.
             The position will always be the center of the node.
    :rtype: dict[str, list[tuple[float, float]]]
    """
    results = {}
    for key, node in data_object_nodes.iteritems():
        if data_objects[key].selection_state is DataSelectionState.Selected:
            continue

        r = node.r if isinstance(node, CircleNode) else (node.size[0] / 2)
        if isinstance(node, CircleNode):
            pos_left = node.pos[0] - r
            pos_right = node.pos[0] + r
        else:
            pos_left = node.pos[0]
            pos_right = node.pos[0] + r * 2

        if not pos_left < line_pos < pos_right:
            continue

        if key not in results:
            results[key] = []
        pos = node.pos if isinstance(node, CircleNode) else (node.pos[0] + r, node.pos[1] + r)
        results[key].append(pos)

    return results


def get_intersection_parallel_coordinates_plot_horizontal(data_objects, data_object_nodes, line_pos, only_at_data_points):
    """
    Calculates the intersection of objects from a parallel coordinates plot with an horizontal line.

    :param data_objects: The data objects on the chart.
    :type data_objects: dict[str, DataObject]
    :param data_object_nodes: The nodes of the data object nodes in the chart.
    :type data_object_nodes: dict[str, PolyLineNode]
    :param line_pos: The necessary position of the node of the line according to the orientation.
    :type line_pos: float
    :param only_at_data_points: Only return intersection that are lying on data points on a item (if true).
    :type: bool
    :return: All nodes that were intersect through the line and the positions according to the line orientation of the intersections.
    :rtype: dict[str, list[tuple[float, float]]]
    """
    return get_intersection_line_chart_horizontal(data_objects=data_objects, data_object_nodes=data_object_nodes, line_pos=line_pos, only_at_data_points=only_at_data_points)


def get_intersection_parallel_coordinates_plot_vertical(data_objects, data_object_nodes, line_pos, only_at_data_points):
    """
    Calculates the intersection of objects from a parallel coordinates plot with an horizontal line.

    :param data_objects: The data objects on the chart.
    :type data_objects: dict[str, DataObject]
    :param data_object_nodes: The nodes of the data object nodes in the chart.
    :type data_object_nodes: dict[str, PolyLineNode]
    :param line_pos: The necessary position of the node of the line according to the orientation.
    :type line_pos: float
    :param only_at_data_points: Only return intersection that are lying on data points on a item (if true).
    :type: bool
    :return: All nodes that were intersect through the line and the positions according to the line orientation of the intersections.
    :rtype: dict[str, list[tuple[float, float]]]
    """
    return get_intersection_line_chart_vertical(data_objects=data_objects, data_object_nodes=data_object_nodes, line_pos=line_pos, only_at_data_points=only_at_data_points)
