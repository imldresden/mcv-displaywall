from libavg_charts.aid_lines.aid_line_enums import AidLineType
from libavg_charts.aid_lines.axis_drag_aid_line import AxisDragAidLine
from libavg_charts.aid_lines.circle_selection_aid_line import CircleSelectionAidLine
from libavg_charts.aid_lines.cursor_aid_line import CursorAidLine
from libavg_charts.aid_lines.cursor_horizontal_aid_line import CursorHorizontalAidLine
from libavg_charts.aid_lines.cursor_vertical_aid_line import CursorVerticalAidLine
from libavg_charts.aid_lines.factory.aid_line_controller_factory import AidLineControllerFactory
from libavg_charts.aid_lines.selection_aid_line import SelectionAidLine
from libavg_charts.aid_lines.selection_horizontal_aid_line import SelectionHorizontalAidLine
from libavg_charts.aid_lines.selection_vertical_aid_line import SelectionVerticalAidLine
from libavg_charts.aid_lines.lasso_selection_aid_line import LassoSelectionAidLine
from libavg_charts.aid_lines.deposit_aid_line import DepositAidLine
from libavg_charts.aid_lines.deposit_horizontal_aid_line import DepositHorizontalAidLine
from libavg_charts.aid_lines.deposit_vertical_aid_line import DepositVerticalAidLine
from libavg_charts.axis.chart_axis_enums import Orientation


def add_aid_lines_to_factory():
    """
    Adds all possible aid line controller to the factory.
    """
    AidLineControllerFactory.add_aid_line_method(
        AidLineType.AxisDragX, lambda chart, aid_line_area, **kwargs:
        AxisDragAidLine(chart=chart, orientation=Orientation.Horizontal, aid_line_area=aid_line_area, **kwargs))
    AidLineControllerFactory.add_aid_line_method(
        AidLineType.AxisDragY, lambda chart, aid_line_area, **kwargs:
        AxisDragAidLine(chart=chart, orientation=Orientation.Vertical, aid_line_area=aid_line_area, **kwargs))
    AidLineControllerFactory.add_aid_line_method(
        AidLineType.Cursor, lambda chart, aid_line_area, **kwargs:
        CursorAidLine(chart=chart, aid_line_area=aid_line_area, **kwargs))
    AidLineControllerFactory.add_aid_line_method(
        AidLineType.CursorHorizontal, lambda chart, aid_line_area, **kwargs:
        CursorHorizontalAidLine(chart=chart, aid_line_area=aid_line_area, **kwargs))
    AidLineControllerFactory.add_aid_line_method(
        AidLineType.CursorVertical, lambda chart, aid_line_area, **kwargs:
        CursorVerticalAidLine(chart=chart, aid_line_area=aid_line_area, **kwargs))
    AidLineControllerFactory.add_aid_line_method(
        AidLineType.Selection, lambda chart, aid_line_area, **kwargs:
        SelectionAidLine(chart=chart, aid_line_area=aid_line_area, **kwargs))
    AidLineControllerFactory.add_aid_line_method(
        AidLineType.SelectionHorizontal, lambda chart, aid_line_area, **kwargs:
        SelectionHorizontalAidLine(chart=chart, aid_line_area=aid_line_area, **kwargs))
    AidLineControllerFactory.add_aid_line_method(
        AidLineType.SelectionVertical, lambda chart, aid_line_area, **kwargs:
        SelectionVerticalAidLine(chart=chart, aid_line_area=aid_line_area, **kwargs))
    AidLineControllerFactory.add_aid_line_method(
        AidLineType.CircleSelection, lambda chart, aid_line_area, **kwargs:
        CircleSelectionAidLine(chart=chart, aid_line_area=aid_line_area, **kwargs))
    AidLineControllerFactory.add_aid_line_method(
        AidLineType.Lasso, lambda chart, aid_line_area, **kwargs:
        LassoSelectionAidLine(chart=chart, aid_line_area=aid_line_area, **kwargs))
    AidLineControllerFactory.add_aid_line_method(
        AidLineType.Deposit, lambda chart, aid_line_area, **kwargs:
        DepositAidLine(chart=chart, aid_line_area=aid_line_area, **kwargs))
    AidLineControllerFactory.add_aid_line_method(
        AidLineType.DepositHorizontal, lambda chart, aid_line_area, **kwargs:
        DepositHorizontalAidLine(chart=chart, aid_line_area=aid_line_area, **kwargs))
    AidLineControllerFactory.add_aid_line_method(
        AidLineType.DepositVertical, lambda chart, aid_line_area, **kwargs:
        DepositVerticalAidLine(chart=chart, aid_line_area=aid_line_area, **kwargs))
