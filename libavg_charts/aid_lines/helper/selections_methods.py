from libavg_charts.charts.bar_chart_special import *
from libavg_charts.charts.bar_chart import BarChart
from libavg_charts.charts.line_chart import LineChart
from libavg_charts.charts.parallel_coordinates_plot import ParallelCoordinatesPlot
from libavg_charts.charts.scatter_plot import ScatterPlot
from libavg.avg import RectNode, CircleNode, PolyLineNode, Point2D
from libavg_charts.aid_lines.helper.selection_method_holder import SelectionMethodHolder, SelectionTypes


def add_selection_methods_to_method_holder():
    """
    Adds the default methods to the SelectionMethodHolder.
    """
    SelectionMethodHolder.add_selection_method(LineChart, SelectionTypes.HorizontalLine, get_selection_line_chart_horizontal_rect)
    SelectionMethodHolder.add_selection_method(LineChart, SelectionTypes.VerticalLine, get_selection_line_chart_vertical_rect)
    SelectionMethodHolder.add_selection_method(LineChart, SelectionTypes.Rectangle, get_selection_line_chart_rect)
    SelectionMethodHolder.add_selection_method(LineChart, SelectionTypes.Lasso, get_selection_line_chart_lasso)
    SelectionMethodHolder.add_selection_method(BarChartBase, SelectionTypes.HorizontalLine, get_selection_bar_chart_horizontal_rect)
    SelectionMethodHolder.add_selection_method(BarChartBase, SelectionTypes.VerticalLine, get_selection_bar_chart_vertical_rect)
    SelectionMethodHolder.add_selection_method(BarChartBase, SelectionTypes.Rectangle, get_selection_bar_chart_rect)
    SelectionMethodHolder.add_selection_method(BarChartBase, SelectionTypes.Lasso, get_selection_bar_chart_lasso)
    SelectionMethodHolder.add_selection_method(BarChart, SelectionTypes.HorizontalLine, get_selection_bar_chart_horizontal_rect)
    SelectionMethodHolder.add_selection_method(BarChart, SelectionTypes.VerticalLine, get_selection_bar_chart_vertical_rect)
    SelectionMethodHolder.add_selection_method(BarChart, SelectionTypes.Rectangle, get_selection_bar_chart_rect)
    SelectionMethodHolder.add_selection_method(BarChart, SelectionTypes.Lasso, get_selection_bar_chart_lasso)
    SelectionMethodHolder.add_selection_method(BarChartManyObjects, SelectionTypes.HorizontalLine, get_selection_bar_chart_horizontal_rect)
    SelectionMethodHolder.add_selection_method(BarChartManyObjects, SelectionTypes.VerticalLine, get_selection_bar_chart_vertical_rect)
    SelectionMethodHolder.add_selection_method(BarChartManyObjects, SelectionTypes.Rectangle, get_selection_bar_chart_rect)
    SelectionMethodHolder.add_selection_method(BarChartManyObjects, SelectionTypes.Lasso, get_selection_bar_chart_lasso)
    SelectionMethodHolder.add_selection_method(BarChartOneObject, SelectionTypes.HorizontalLine, get_selection_bar_chart_horizontal_rect)
    SelectionMethodHolder.add_selection_method(BarChartOneObject, SelectionTypes.VerticalLine, get_selection_bar_chart_vertical_rect)
    SelectionMethodHolder.add_selection_method(BarChartOneObject, SelectionTypes.Rectangle, get_selection_bar_chart_rect)
    SelectionMethodHolder.add_selection_method(BarChartOneObject, SelectionTypes.Lasso, get_selection_bar_chart_lasso)
    SelectionMethodHolder.add_selection_method(ScatterPlot, SelectionTypes.HorizontalLine, get_selection_scatter_plot_horizontal_rect)
    SelectionMethodHolder.add_selection_method(ScatterPlot, SelectionTypes.VerticalLine, get_selection_scatter_plot_vertical_rect)
    SelectionMethodHolder.add_selection_method(ScatterPlot, SelectionTypes.Rectangle, get_selection_scatter_plot_rect)
    SelectionMethodHolder.add_selection_method(ScatterPlot, SelectionTypes.Circle, get_selection_scatter_plot_circle)
    SelectionMethodHolder.add_selection_method(ScatterPlot, SelectionTypes.Lasso, get_selection_scatter_plot_lasso)
    # TODO: Fix selection with pcp.
    SelectionMethodHolder.add_selection_method(ParallelCoordinatesPlot, SelectionTypes.HorizontalLine, get_selection_parallel_coordinates_plot_horizontal_rect)
    SelectionMethodHolder.add_selection_method(ParallelCoordinatesPlot, SelectionTypes.VerticalLine, get_selection_parallel_coordinates_plot_vertical_rect)
    SelectionMethodHolder.add_selection_method(ParallelCoordinatesPlot, SelectionTypes.Rectangle, get_selection_parallel_coordinates_plot_rect)
    SelectionMethodHolder.add_selection_method(ParallelCoordinatesPlot, SelectionTypes.Lasso, get_selection_parallel_coordinates_plot_lasso)


def __pos_in_poly(poly_line, pos):
    """
    Checks if a pos is in a poly line area.

    :param poly_line: The poly line positions.
    :type poly_line: list[Point2D]
    :param pos: The position to check for.
    :type pos: tuple[float, float]
    :return: If the pos is inside of the polyline.
    :rtype: bool
    """
    length = len(poly_line)
    in_poly = False

    j = length - 1
    for i in range(length):
        if ((poly_line[i][1] > pos[1]) != (poly_line[j][1] > pos[1])) and \
                (pos[0] < (poly_line[j][0] - poly_line[i][0]) * (pos[1] - poly_line[i][1]) / (poly_line[j][1] - poly_line[i][1]) + poly_line[i][0]):
            in_poly = not in_poly
        j = i
    return in_poly


def get_selection_line_chart_horizontal_rect(data_objects_nodes, value1, value2):
    """
    Calculates the selection that is in the horizontal rect.

    :param data_objects_nodes: The nodes of the data objects in the chart.
    :type data_objects_nodes: dict[str, PolyLineNode]
    :param value1: The first side of the rect.
    :type value1: float
    :param value2: The second side of the rect.
    :type value2: float
    :return: All nodes that are inside.
    :rtype: dict[str, PolyLineNode]
    """
    if value1 < value2:
        smaller_val, higher_val = value1, value2
    else:
        smaller_val, higher_val = value2, value1

    results = {}
    for key, node in data_objects_nodes.iteritems():
        max_pos, min_pos = float('-inf'), float('inf')
        for pos in node.pos:
            if pos[1] < min_pos:
                min_pos = pos[1]
            if pos[1] > max_pos:
                max_pos = pos[1]

            if (smaller_val < max_pos < higher_val or smaller_val < min_pos < higher_val or
                    min_pos < smaller_val < max_pos or min_pos < higher_val < max_pos):
                results[key] = node

    return results


def get_selection_line_chart_vertical_rect(data_objects_nodes, value1, value2):
    """
    Calculates the selection that is in the vertical rect.

    :param data_objects_nodes: The nodes of the data objects in the chart.
    :type data_objects_nodes: dict[str, PolyLineNode]
    :param value1: The first side of the rect.
    :type value1: float
    :param value2: The second side of the rect.
    :type value2: float
    :return: All nodes that are inside.
    :rtype: dict[str, PolyLineNode]
    """
    if value1 < value2:
        smaller_val, higher_val = value1, value2
    else:
        smaller_val, higher_val = value2, value1

    results = {}
    for key, node in data_objects_nodes.iteritems():
        max_pos, min_pos = float('-inf'), float('inf')
        for pos in node.pos:
            if pos[0] < min_pos:
                min_pos = pos[0]
            if pos[0] > max_pos:
                max_pos = pos[0]

            if (smaller_val < max_pos < higher_val or smaller_val < min_pos < higher_val or
                    min_pos < smaller_val < max_pos or min_pos < higher_val < max_pos):
                results[key] = node

    return results


def get_selection_line_chart_rect(data_objects_nodes, value1, value2):
    """
    Calculates the selection that is in the rect.

    :param data_objects_nodes: The nodes of the data objects in the chart.
    :type data_objects_nodes: dict[str, PolyLineNode]
    :param value1: One corner of the rectangle.
    :type value1: tuple[float, float]
    :param value2: The other corner of the rectangle.
    :type value2: tuple[float, float]
    :return: All nodes that are inside.
    :rtype: dict[str, PolyLineNode]
    """
    if value1[0] < value2[0]:
        smaller_x, higher_x = value1[0], value2[0]
    else:
        smaller_x, higher_x = value2[0], value1[0]
    if value1[1] < value2[1]:
        smaller_y, higher_y = value1[1], value2[1]
    else:
        smaller_y, higher_y = value2[1], value1[1]
    pre_selection = get_selection_line_chart_horizontal_rect(data_objects_nodes=data_objects_nodes, value1=value1[1], value2=value2[1])

    results = {}
    for key, node in pre_selection.iteritems():
        max_x, min_x = float('-inf'), float('inf')
        for pos in node.pos:
            if smaller_y < pos[1] < higher_y:
                if pos[0] < min_x:
                    min_x = pos[0]
                if pos[0] > max_x:
                    max_x = pos[0]

            if (smaller_x < max_x < higher_x or smaller_x < min_x < higher_x or
                    min_x < smaller_x < max_x or min_x < higher_x < max_x):
                results[key] = node

    return results


def get_selection_line_chart_lasso(data_objects_nodes, value1, value2=None):
    """
    Calculates the selection that is in the lasso.

    :param data_objects_nodes: The nodes of the data objects in the chart.
    :type data_objects_nodes: dict[str, PolyLineNode]
    :param value1: The line of the lasso.
    :type value1: list[Point2D]
    :param value2: Nothing.
    :return: All nodes that are inside.
    :rtype: dict[str, PolyLineNode]
    """
    results = {}
    for key, node in data_objects_nodes.iteritems():
        for pos in node.pos:
            if __pos_in_poly(poly_line=value1, pos=pos):
                results[key] = node
                break

    return results


def get_selection_bar_chart_horizontal_rect(data_objects_nodes, value1, value2):
    """
    Calculates the selection that is in the horizontal rect.

    :param data_objects_nodes: The nodes of the data objects in the chart.
    :type data_objects_nodes: dict[str, RectNode]
    :param value1: The first side of the rect.
    :type value1: float
    :param value2: The second side of the rect.
    :type value2: float
    :return: All nodes that are inside.
    :rtype: dict[str, RectNode]
    """
    results = {}
    for key, node in data_objects_nodes.iteritems():
        pos_top = node.pos[1] + node.size[1]
        if pos_top < value1 < node.pos[1] or pos_top < value2 < node.pos[1]:
            results[key] = node

    return results


def get_selection_bar_chart_vertical_rect(data_objects_nodes, value1, value2):
    """
    Calculates the selection that is in the vertical rect.

    :param data_objects_nodes: The nodes of the data objects in the chart.
    :type data_objects_nodes: dict[str, RectNode]
    :param value1: The first side of the rect.
    :type value1: float
    :param value2: The second side of the rect.
    :type value2: float
    :return: All nodes that are inside.
    :rtype: dict[str, RectNode]
    """
    if value1 < value2:
        smaller_val, higher_val = value1, value2
    else:
        smaller_val, higher_val = value2, value1

    results = {}
    for key, node in data_objects_nodes.iteritems():
        pos_right = node.pos[0] + node.size[0]
        if (smaller_val < node.pos[0] < higher_val or smaller_val < pos_right < higher_val or
                node.pos[0] < value1 < pos_right or node.pos[0] < value2 < pos_right):
            results[key] = node

    return results


def get_selection_bar_chart_rect(data_objects_nodes, value1, value2):
    """
    Calculates the selection that is in the rect.

    :param data_objects_nodes: The nodes of the data objects in the chart.
    :type data_objects_nodes: dict[str, RectNode]
    :param value1: One corner of the rectangle.
    :type value1: tuple[float, float]
    :param value2: The other corner of the rectangle.
    :type value2: tuple[float, float]
    :return: All nodes that are inside.
    :rtype: dict[str, RectNode]
    """
    results = get_selection_bar_chart_horizontal_rect(data_objects_nodes=data_objects_nodes, value1=value1[1], value2=value2[1])
    results = get_selection_bar_chart_vertical_rect(data_objects_nodes=results, value1=value1[0], value2=value2[0])
    return results


def get_selection_bar_chart_lasso(data_objects_nodes, value1, value2=None):
    """
    Calculates the selection that is in the lasso.

    :param data_objects_nodes: The nodes of the data objects in the chart.
    :type data_objects_nodes: dict[str, RectNode]
    :param value1: The line of the lasso.
    :type value1: list[Point2D]
    :param value2: Nothing.
    :return: All nodes that are inside.
    :rtype: dict[str, RectNode]
    """
    if len(value1) < 1:
        return {}

    results = {}
    for key, node in data_objects_nodes.iteritems():
        centroid = node.pos[0] + node.size[0] / 2, node.pos[1] + node.size[1] / 2
        # Check if the middle of the bar chart lies in the polyline.
        if __pos_in_poly(value1, centroid):
            results[key] = node
            continue

        left, top, right, bottom = node.pos[0], node.pos[1], node.pos[0] + node.size[0], node.pos[1] + node.size[1]

        x1, y1 = value1[0]
        inside = False
        for x2, y2 in (value1 + [value1[0]])[1:]:
            # Check if a pos of the polyline is inside the bar.
            if left <= x2 <= right and top <= y2 <= bottom:
                inside = True
                break

            # Check if a vertex point lies in the polyline.
            for pos in [(left, top), (right, top), (right, bottom), (left, bottom)]:
                if __pos_in_poly(value1, pos):
                    inside = True
                    break
            if inside:
                break

            min_x, max_x = (x1, x2) if x1 < x2 else (x2, x1)
            min_y, max_y = (y1, y2) if y1 < y2 else (y2, y1)
            # Check if a side of the bar intersects with a line in the poly line.
            if ((min_y <= top <= max_y and min_y <= bottom <= max_y) and
                (left <= x1 <= right and left <= x2 <= right)):
                inside = True
                break
            elif ((min_x <= left <= max_x and min_x <= right <= max_x) and
                  (left <= y1 <= bottom and top <= y2 <= bottom)):
                inside = True
                break

            x1, y1 = x2, y2

        if inside:
            results[key] = node

    return results


def get_selection_scatter_plot_horizontal_rect(data_objects_nodes, value1, value2):
    """
    Calculates the selection that is in the horizontal rect.

    :param data_objects_nodes: The nodes of the data objects in the chart.
    :type data_objects_nodes: dict[str, CircleNode]
    :param value1: The first side of the rect.
    :type value1: float
    :param value2: The second side of the rect.
    :type value2: float
    :return: All nodes that are inside.
    :rtype: dict[str, CircleNode]
    """
    results = {}
    for key, node in data_objects_nodes.iteritems():
        pos = node.pos[1] + node.r
        if value1 < pos < value2 or value2 < pos < value1:
            results[key] = node

    return results


def get_selection_scatter_plot_vertical_rect(data_objects_nodes, value1, value2):
    """
    Calculates the selection that is in the vertical rect.

    :param data_objects_nodes: The nodes of the data objects in the chart.
    :type data_objects_nodes: dict[str, CircleNode]
    :param value1: The first side of the rect.
    :type value1: float
    :param value2: The second side of the rect.
    :type value2: float
    :return: All nodes that are inside.
    :rtype: dict[str, CircleNode]
    """
    results = {}
    for key, node in data_objects_nodes.iteritems():
        pos = node.pos[0] + node.r
        if value1 < pos < value2 or value2 < pos < value1:
            results[key] = node

    return results


def get_selection_scatter_plot_rect(data_objects_nodes, value1, value2):
    """
    Calculates the selection that is in the rect.

    :param data_objects_nodes: The nodes of the data objects in the chart.
    :type data_objects_nodes: dict[str, CircleNode]
    :param value1: One corner of the rectangle.
    :type value1: tuple[float, float]
    :param value2: The other corner of the rectangle.
    :type value2: tuple[float, float]
    :return: All nodes that are inside.
    :rtype: dict[str, CircleNode]
    """
    results = get_selection_scatter_plot_horizontal_rect(data_objects_nodes=data_objects_nodes, value1=value1[1], value2=value2[1])
    results = get_selection_scatter_plot_vertical_rect(data_objects_nodes=results, value1=value1[0], value2=value2[0])
    return results


def get_selection_scatter_plot_circle(data_objects_nodes, value1, value2):
    """
    Calculates the selection that is in a circle.

    :param data_objects_nodes: The nodes of the data objects in the chart.
    :type data_objects_nodes: dict[str, CircleNode]
    :param value1: The position of the circle.
    :type value1: tuple[float, float]
    :param value2: The radius of the circle.
    :type value2: float
    :return: All nodes that are inside.
    :rtype: dict[str, CircleNode]
    """
    results = {}
    for key, node in data_objects_nodes.iteritems():
        pos_x, pos_y = node.pos[0] + node.r, node.pos[1] + node.r
        if (pos_x - value1[0]) ** 2 + (pos_y - value1[1]) ** 2 < value2 ** 2:
            results[key] = node

    return results


def get_selection_scatter_plot_lasso(data_objects_nodes, value1, value2=None):
    """
    Calculates the selection that is in the lasso.

    :param data_objects_nodes: The nodes of the data objects in the chart.
    :type data_objects_nodes: dict[str, CircleNode]
    :param value1: The line of the lasso.
    :type value1: list[Point2D]
    :param value2: Nothing.
    :return: All nodes that are inside.
    :rtype: dict[str, CircleNode]
    """
    results = {}
    for key, node in data_objects_nodes.iteritems():
        if __pos_in_poly(poly_line=value1, pos=node.pos):
            results[key] = node

    return results


def get_selection_parallel_coordinates_plot_horizontal_rect(data_objects_nodes, value1, value2):
    """
    Calculates the selection that is in the horizontal rect.

    :param data_objects_nodes: The nodes of the data objects in the chart.
    :type data_objects_nodes: dict[str, PolyLineNode]
    :param value1: The first side of the rect.
    :type value1: float
    :param value2: The second side of the rect.
    :type value2: float
    :return: All nodes that are inside.
    :rtype: dict[str, PolyLineNode]
    """
    return get_selection_line_chart_horizontal_rect(data_objects_nodes=data_objects_nodes, value1=value1, value2=value2)


def get_selection_parallel_coordinates_plot_vertical_rect(data_objects_nodes, value1, value2):
    """
    Calculates the selection that is in the vertical rect.

    :param data_objects_nodes: The nodes of the data objects in the chart.
    :type data_objects_nodes: dict[str, PolyLineNode]
    :param value1: The first side of the rect.
    :type value1: float
    :param value2: The second side of the rect.
    :type value2: float
    :return: All nodes that are inside.
    :rtype: dict[str, PolyLineNode]
    """
    return get_selection_line_chart_vertical_rect(data_objects_nodes=data_objects_nodes, value1=value1, value2=value2)


def get_selection_parallel_coordinates_plot_rect(data_objects_nodes, value1, value2):
    """
    Calculates the selection that is in the rect.

    :param data_objects_nodes: The nodes of the data objects in the chart.
    :type data_objects_nodes: dict[str, PolyLineNode]
    :param value1: One corner of the rectangle.
    :type value1: tuple[float, float]
    :param value2: The other corner of the rectangle.
    :type value2: tuple[float, float]
    :return: All nodes that are inside.
    :rtype: dict[str, PolyLineNode]
    """
    return get_selection_line_chart_rect(data_objects_nodes=data_objects_nodes, value1=value1, value2=value2)


def get_selection_parallel_coordinates_plot_lasso(data_objects_nodes, value1, value2=None):
    """
    Calculates the selection that is in the lasso.

    :param data_objects_nodes: The nodes of the data objects in the chart.
    :type data_objects_nodes: dict[str, PolyLineNode]
    :param value1: The line of the lasso.
    :type value1: list[Point2D]
    :param value2: Nothing.
    :return: All nodes that are inside.
    :rtype: dict[str, PolyLineNode]
    """
    return get_selection_line_chart_lasso(data_objects_nodes=data_objects_nodes, value1=value1, value2=value2)
