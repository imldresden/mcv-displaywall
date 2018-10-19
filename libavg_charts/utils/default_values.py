import utils.colors as colors
from configs import config_app
from configs.visual_data import VisDefaults
from libavg_charts.aid_lines.aid_line_enums import *
from libavg_charts.axis.chart_axis_enums import *
from libavg_charts.charts.chart_enums import LabelPosition


class AidLineDefaults(object):
    SHOW_LABEL = False
    EXTRA_LENGTH = 12
    INNER_LINE_WIDTH = 1
    OUTER_LINE_WIDTH = 51
    OUTER_LINE_OPACITY = 0.06
    LINE_COLOR = colors.BLUE_GREY_DARKEN_2
    TO_AXIS_OFFSET = 9
    CIRCLE_RADIUS = 35
    LABEL_POS = AidLineLabelPos.Bottom
    LABEL_CONTENT_AXIS_INDEX = 0
    DATA_POINT_SNAPPING_RANGE_CM = 1


class SelectionLineDefaults(object):
    EXTRA_LENGTH = 12
    LINE_WIDTH = 2
    LINE_COLOR = colors.BLUE_GREY_DARKEN_1


class IntersectionDefaults(object):
    SHOW_INTERSECTIONS = False
    SHOW_LABEL = False
    LABEL_CONTENT_TYPE = "axis"
    LABEL_CONTENT = "crimes_count"
    INTERSECTION_COLOR = colors.BLUE_GREY_DARKEN_1
    INTERSECTION_RADIUS = 3
    INTERSECTION_FILLED = True
    INTERSECTION_STROKE_WIDTH = 0
    INTERSECTION_LABEL_COLOR_USE_DATA_OBJECT_COLOR = True


class ChartDefaults(object):
    AXIS_WIDTH = 3
    LABEL_POS = LabelPosition.Top
    SHOW_LABEL = True
    PADDING_LEFT = 48
    PADDING_TOP = 25
    PADDING_RIGHT = 45
    PADDING_BOTTOM = 30

    LINE_CHART_DATA_LINE_WIDTH = 3
    SCATTER_PLOT_DATA_OBJECT_RADIUS = 3
    BAR_CHART_BAR_LINE_WIDTH = 0
    BAR_CHART_BAR_SPACING = 5
    BAR_CHART_BAR_WIDTH = None


class TwoAxisChartDefaults(object):
    AXIS_CROSS_OFFSET = 0
    GRID_LINE_COLOR = colors.GREY_LIGHTEN_1
    GRID_LINE_WIDTH = 1
    GRID_LINE_OPACITY = 0.5


class AxisDefaults(object):
    BOTTOM_OFFSET = 26.0
    TOP_OFFSET = 14.0
    ORIENTATION = Orientation.Vertical
    WIDTH = 2.0
    DATA_DIRECTION = DataDirection.Positive
    TICK_SIDE = TickSide.Center
    TICK_WIDTH = 1.0
    MARKING_ORIENTATION = Orientation.Horizontal
    MARKING_SIDE = MarkingSide.Left
    MARKING_STEPS = 1.0
    DATA_STEPS = 5
    SHOW_LABEL = True
    SHOW_SCALE_UNIT = False
    LABEL_POS = LabelPosition.Top
    COLOR = "999"
    TICK_OVERHANG = 7.0
    SHOW_GRID_LINE = GridLines.Nothing

    AXIS_BACKGROUND_SIDE = TickSide.Center
    AXIS_BACKGROUND_SIZE = 2.0 * config_app.pixel_per_cm


class TextLabelDefaults(object):
    COLOR = "555"
    FONT_SIZE = 11
    FONT_VARIANT = "Regular"
    OFFSET_TO_OTHER_ELEMENT = 3


class TextMarkingDefaults(object):
    COLOR = "555"
    FONT_SIZE = 11
    FONT_VARIANT = "Regular"
    OFFSET_TO_OTHER_ELEMENT = 1


class TextChartLabelDefaults(object):
    COLOR = TextLabelDefaults.COLOR
    FONT_SIZE = 18
    OFFSET_TO_OTHER_ELEMENT = 3
    FONT_VARIANT = "Regular"


class DataDefaults(object):
    COLOR = VisDefaults.ITEM_COLOR
    COLOR_SELECTED = colors.AMBER_DARKEN_3
    COLOR_HIGHLIGHTED = "002200"
