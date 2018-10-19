from libavg_charts.axis.chart_axis_enums import *
from libavg_charts.configurations.text_label_configuration import *
from libavg_charts.utils.default_values import AxisDefaults


class ChartAxisConfiguration(object):
    def __init__(self,
                 bottom_offset=AxisDefaults.BOTTOM_OFFSET, top_offset=AxisDefaults.TOP_OFFSET, axis_orientation=AxisDefaults.ORIENTATION, axis_width=AxisDefaults.WIDTH,
                 data_direction=AxisDefaults.DATA_DIRECTION, tick_side=AxisDefaults.TICK_SIDE, marking_side=AxisDefaults.MARKING_SIDE, marking_steps=AxisDefaults.MARKING_STEPS,
                 data_steps=AxisDefaults.DATA_STEPS, show_label=AxisDefaults.SHOW_LABEL, show_scale_unit=AxisDefaults.SHOW_SCALE_UNIT, label_pos=AxisDefaults.LABEL_POS,
                 axis_color=AxisDefaults.COLOR, tick_overhang=AxisDefaults.TICK_OVERHANG, label_text_config=None, marking_text_config=None, tick_width=AxisDefaults.TICK_WIDTH,
                 marking_orientation=AxisDefaults.MARKING_ORIENTATION, show_grid_line=AxisDefaults.SHOW_GRID_LINE,
                 axis_background_side=AxisDefaults.AXIS_BACKGROUND_SIDE, axis_background_size=AxisDefaults.AXIS_BACKGROUND_SIZE):
        """
        :param bottom_offset: Should there be an offset between the beginning of the axis and the first value tick.
        :type bottom_offset: float
        :param top_offset: Should there be an offset between the end of the axis and the last value tick.
        :type top_offset: float
        :param axis_orientation: In which direction should this axis be placed.
        :type axis_orientation: Orientation
        :param axis_width: The width of the axis.
        :type axis_width: float
        :param data_direction: In which direction should the data be placed on the axis.
                               Positive means that the smallest value is at the base of the axis.
        :type data_direction: DataDirection
        :param tick_side: On which side of the axis should the ticks be. If this is not 'Center' the 'marking_side' has no effect.
        :type tick_side: TickSide
        :param marking_side: On which side of the axis the markings for the ticks should be placed. It has no effect if the 'tick_side' is not 'Center'.
        :type marking_side: MarkingSide
        :param marking_steps: What is the distance between markings on the ticks. The first and last tick are always with a marking.
        :type marking_steps: int
        :param data_steps: The number of steps between the highest and the lowest value of this axis.
                           Will be ignored if the data type is String and will be automatically calculated.
        :type data_steps: int
        :param show_label: Should the label be displayed?
        :type show_label: bool
        :param show_scale_unit: Should the scale unit be displayed?
        :type show_scale_unit: bool
        :param label_pos: Where should the label be positioned. Top in the vertical axis alignment is on the right side.
        :type label_pos: LabelPosition
        :param axis_color: The color for the axis.
        :type axis_color: Color
        :param tick_overhang: The extra width of the ticks on both sites of the axis.
        :type tick_overhang: float
        :param label_text_config: The configuration for all text for marking on this axis.
        :type label_text_config: TextLabelConfiguration
        :param marking_text_config: The configuration for all text for labels on this axis.
        :type marking_text_config: TextLabelConfiguration
        :param marking_orientation: The orientation of the markings.
        :type marking_orientation: Orientation
        :param show_grid_line: Should be fine grid lines be shown at specific positions?
        :type show_grid_line: GridLines
        :param axis_background_side: The side on which the axis background is placed.
        :type axis_background_side: TickSide
        :param axis_background_size: The size in the orthogonal direction of the axis for the background.
        :type axis_background_size: tuple[float, float]
        """
        self.bottom_offset = bottom_offset
        self.top_offset = top_offset
        self.axis_orientation = axis_orientation
        self.axis_width = axis_width
        self.data_direction = data_direction
        self.tick_side = tick_side
        self.marking_orientation = marking_orientation
        self.marking_side = marking_side if tick_side is TickSide.Center else (MarkingSide.Left if tick_side is TickSide.Left else MarkingSide.Right)
        self.marking_steps = marking_steps
        self.data_steps = data_steps
        self.show_label = show_label
        self.show_scale_unit = show_scale_unit
        self.label_pos = label_pos
        self.axis_color = axis_color
        self.tick_overhang = tick_overhang
        self.label_text_config = label_text_config if label_text_config else TextLabelConfiguration()
        self.marking_text_config = marking_text_config if marking_text_config else TextMarkingConfiguration()
        self.tick_width = tick_width
        self.show_grid_lines = show_grid_line
        self.axis_background_side = axis_background_side
        self.axis_background_size = axis_background_size
