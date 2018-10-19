import datetime
import time
from math import pi

from libavg import avg
from libavg.avg import DivNode

from data_models.data_enums import DataType
from libavg_charts.axis.chart_axis_base import ChartAxisBase
from libavg_charts.axis.chart_axis_enums import *
from libavg_charts.charts.chart_enums import LabelPosition


class ChartAxis(ChartAxisBase):
    """
    An representation for an axis. The values and markings for this axis will be created from top/right to bottom/left.
    So it's necessary to invert the value in the calculations!
    """
    # TODO: If the data type is Integer only allow ticks and marking that are a integer itself (division without a rest).
    # TODO: Add the use of the unit if wished.

    def __init__(self, data_desc, axis_length, axis_config=None, parent=None, **kwargs):
        """
        :param data_desc: The description of the data that will be placed on this axis.
        :type data_desc: DataDescription
        :param axis_config: The configuration for this axis.
        :type axis_config: ChartAxisConfiguration
        :param axis_length: The length of the axis itself.
        :type axis_length: float
        :type parent: DivNode
        :param kwargs: All other parameter for the div node.
        """
        if 'size' in kwargs:
            kwargs.pop('size')
        super(ChartAxis, self).__init__(parent=parent, **kwargs)

        self._data_desc = data_desc
        self._axis_config = axis_config
        self._axis_length = axis_length
        # self._complete_length_as_axis_length = complete_length_as_axis_length

        self.size = (0, 0)
        self.__axis_size = (0, 0)

        self._label_node = None
        self._tick_positions = []
        self._marking_positions = []
        # key -> the shown text     value -> the marking node
        self._markings = {}

        # The distance between each tick.
        # If only one data step is wished, use the middle of the axis.
        if self._axis_config.data_steps > 1:
            self._tick_distance = float(self._axis_length - self._axis_config.bottom_offset - self._axis_config.top_offset) / (self._axis_config.data_steps - 1)
        else:
            self._tick_distance = (axis_length - self._axis_config.bottom_offset - self._axis_config.top_offset) / 2
        # Generate the step between ticks for the Float and Integer data type
        self._value_step = 0
        if self._axis_config.data_steps > 1:
            if DataType.is_number(self._data_desc.data_type):
                self._value_step = float(self._data_desc.data[1] - self._data_desc.data[0]) / (self._axis_config.data_steps - 1)
            elif DataType.is_datetime(self._data_desc.data_type):
                self._value_step = (self._data_desc.data[1] - self._data_desc.data[0]) / (self._axis_config.data_steps - 1)

        self._create_view()

    @property
    def tick_distance(self):
        """
        :rtype: float
        """
        return self._tick_distance

    @property
    def tick_positions(self):
        """
        :rtype: list[float]
        """
        return self._tick_positions

    @property
    def marking_positions(self):
        """
        :rtype: list[float]
        """
        return self._marking_positions

    @property
    def markings(self):
        """
        :rtype: dict[str, avg.WordsNode]
        """
        return self._markings

    @property
    def axis_length(self):
        """
        :rtype: float
        """
        return self._axis_length

    @property
    def axis_size(self):
        """
        :return: The axis size without the label.
        :rtype: tuple[float, float]
        """
        return self.__axis_size

    # TODO: Could be deleted? Not really sure.
    @property
    def complete_axis_size(self):
        """
        :return: The axis size with the label.
        :rtype: tuple[float, float]
        """
        return self.__complete_axis_size

    @property
    def data_desc(self):
        """
        :rtype: DataDescription
        """
        return self._data_desc

    @property
    def orientation(self):
        """
        :rtype: Orientation
        """
        return self._axis_config.axis_orientation

    @property
    def show_grid_lines(self):
        """
        :rtype: GridLines
        """
        return self._axis_config.show_grid_lines

    def get_pos_from_data_value(self, date_value, add_to_pos=True):
        """
        Calculates the position of a value point on this axis. 
        This calculation will use all the offsets and labels and stuff and will give the exact position of the value on the whole axis.
        
        :param date_value: The value that should be on this axis.
        :type date_value: object
        :param add_to_pos: Should the value automatically added to the position of this axis?
        :type add_to_pos: bool
        :return: The position on the axis of the given value. None if the value is not on the axis.
        :rtype: float
        """
        if not self._check_data_type(date_value):
            return None

        pure_axis_length = self._axis_length - self._axis_config.top_offset - self._axis_config.bottom_offset

        pixel_value = 0
        # Check the data type of the displayed data:
        # Get from the value the correct pixel value.
        if DataType.is_number(self._data_desc.data_type):
            data_range = self._data_desc.data[1] - self._data_desc.data[0]
            # If only one data step is wished, use the middle of the axis.
            if data_range != 0:
                pixel_value = (pure_axis_length * (date_value - self._data_desc.data[0])) / data_range
            else:
                pixel_value = self._tick_distance
        elif DataType.is_string(self._data_desc.data_type):
            step = self._data_desc.data.index(date_value)
            pixel_value = step * self._tick_distance
        elif self._data_desc.data_type is DataType.DateTime or self._data_desc.data_type is DataType.Day:
            data = time.mktime(self._data_desc.data[0].timetuple()), time.mktime(self._data_desc.data[1].timetuple())
            data_range = data[1] - data[0]
            # If only one data step is wished, use the middle of the axis.
            if data_range != 0:
                pixel_value = (pure_axis_length * (time.mktime(date_value.timetuple()) - data[0])) / data_range
            else:
                pixel_value = self._tick_distance
        elif self._data_desc.data_type is DataType.Date:
            data_range = (self._data_desc.data[1] - self._data_desc.data[0]).days
            # If only one data step is wished, use the middle of the axis.
            if data_range != 0:
                pixel_value = (int(pure_axis_length) * (date_value - self._data_desc.data[0]).days) / data_range
            else:
                pixel_value = self._tick_distance
        elif self._data_desc.data_type is DataType.Time:
            data_range = (self._data_desc.data[1] - self._data_desc.data[0])
            data_range = data_range.days * 24 * 60 + data_range.seconds / 60
            # If only one data step is wished, use the middle of the axis.
            if data_range != 0:
                delta_time = (date_value - self._data_desc.data[0])
                delta_time = delta_time.days * 24 * 60 + delta_time.seconds / 60
                pixel_value = (pure_axis_length * delta_time) / data_range
            else:
                pixel_value = self._tick_distance

        # Check in which direction the data should go.
        if self._axis_config.data_direction is DataDirection.Negative:
            pixel_value = pure_axis_length - pixel_value

        axis_value_start = self._axis_config.bottom_offset
        # Check if a label is shown and on which position it is.
        if self._axis_config.show_label:
            axis_value_start += self._axis_config.label_text_config.offset_to_other_element
            axis_value_start += self._label_node.size[0] if self._axis_config.axis_orientation is Orientation.Horizontal else self._label_node.size[1]

        # Check in which direction the axis should go
        if self._axis_config.axis_orientation is Orientation.Vertical:
            result = self.__complete_axis_size[1] - (axis_value_start + pixel_value)
            if add_to_pos:
                result += self.pos[1]
        else:
            result = self._axis_length - (self.__complete_axis_size[0] - (axis_value_start + pixel_value))
            if add_to_pos:
                result += self.pos[0]

        return result

    def get_data_value_from_pos(self, pos, subtract_from_pos=True):
        """
        Calculates the value of a position on this axis.
        This calculation will use all the offsets and labels and stuff and will give the exact value of the position on the whole axis.

        :param pos: The value that should be on this axis.
        :type pos: float
        :param subtract_from_pos: Should the pos automatically be subtracted from the position of this axis?
        :type subtract_from_pos: bool
        :return: The value of the position on the axis. None if the position is not on the axis.
        :rtype: object
        """
        # TODO: Fix this if the axis only has one tick.
        if subtract_from_pos:
            pos -= self.pos[0] if self._axis_config.axis_orientation is Orientation.Horizontal else self.pos[1]

        axis_value_start = self._axis_config.bottom_offset
        # Check if a label is shown and on which position it is.
        if self._axis_config.show_label:
            axis_value_start += self._axis_config.label_text_config.offset_to_other_element
            axis_value_start += self._label_node.size[0] if self._axis_config.axis_orientation is Orientation.Horizontal else self._label_node.size[1]

        # Check in which orientation the axis has.
        if self._axis_config.axis_orientation is Orientation.Vertical:
            pixel_value = self.__complete_axis_size[1] - pos - axis_value_start
        else:
            pixel_value = pos - self._axis_length + self.__complete_axis_size[0] - axis_value_start

        pure_axis_length = self._axis_length - self._axis_config.top_offset - self._axis_config.bottom_offset
        # Check in which direction the data should go.
        if self._axis_config.data_direction is DataDirection.Negative:
            pixel_value = pure_axis_length - pixel_value

        data_value = None
        # Check the data type of the displayed data:
        # Get from the pixel value to the correct value.
        if DataType.is_number(self._data_desc.data_type):
            data_range = self._data_desc.data[1] - self._data_desc.data[0]
            data_value = ((pixel_value * data_range) / pure_axis_length) + self._data_desc.data[0]
            # Check if the data value is inside of the possible data for this axis.
            if not self._data_desc.data[0] <= data_value <= self._data_desc.data[1]:
                data_value = None
        elif DataType.is_string(self._data_desc.data_type):
            step = pixel_value / self._tick_distance
            step = int(round(step))
            # Check if the step is inside of the data for this axis.
            if 0 <= step < len(self._data_desc.data):
                data_value = self._data_desc.data[step]
        elif self._data_desc.data_type is DataType.DateTime or self._data_desc.data_type is DataType.Day:
            data = time.mktime(self._data_desc.data[0].timetuple()), time.mktime(self._data_desc.data[1].timetuple())
            data_range = data[1] - data[0]
            data_value = ((pixel_value * data_range) / pure_axis_length) + data[0]
            # Check if the data value is inside of the possible data for this axis.
            data_value = None if not data[0] <= data_value <= data[1] else datetime.datetime.fromtimestamp(data_value)
        elif self._data_desc.data_type is DataType.Date:
            data_range = (self._data_desc.data[1] - self._data_desc.data[0]).days
            data_value = self._data_desc.data[0] + datetime.timedelta(days=(pixel_value * data_range) / pure_axis_length)
            if not self._data_desc.data[0] <= data_value <= self._data_desc.data[1]:
                data_value = None
        elif self._data_desc.data_type is DataType.Time:
            data_range = (self._data_desc.data[1] - self._data_desc.data[0])
            data_range = data_range.days * 24 * 60 + data_range.seconds / 60
            data_value = self._data_desc.data[0] + datetime.timedelta(minutes=(pixel_value * data_range) / pure_axis_length)
            if not self._data_desc.data[0] <= data_value <= self._data_desc.data[1]:
                data_value = None

        # TODO: Make this check for the other data types too.
        if data_value is not None and self._data_desc.data_type is DataType.Integer:
            data_value = int(data_value)

        return data_value

    def reset_markings(self, marking=None):
        """
        Reset a given or all markings to their original font variant.

        :param marking: A marking on this axis. If None all markings will be used.
        :type marking: WordsNode
        """
        if marking is not None and marking not in self._markings.keys():
            return

        if marking:
            marking.variant = self._axis_config.marking_text_config.font_variant
        else:
            for m in self._markings.values():
                m.variant = self._axis_config.marking_text_config.font_variant

    def _create_view(self):
        """
        Creates the complete view for this axis.
        """
        self._create_axis_view()
        self._create_ticks_view()
        if self._axis_config.show_label and not self._label_node:
            self._create_label_view()

        self.__complete_axis_size = self._calc_axis_complete_size()

    def _create_axis_view(self):
        """
        Creates the view for the axis and the touch able background.
        """
        if self._axis_config.axis_background_side is TickSide.Left:
            left_overhang = self._axis_config.axis_background_size
            right_overhang = 0
        elif self._axis_config.axis_background_side is TickSide.Right:
            left_overhang = 0
            right_overhang = self._axis_config.axis_background_size
        else:
            left_overhang = self._axis_config.axis_background_size / 2
            right_overhang = self._axis_config.axis_background_size / 2

        # # Check in which direction the axis should go:
        # # Set the end position of the axis.
        if self._axis_config.axis_orientation is Orientation.Vertical:
            axis_pos2 = 0, self._axis_length
            background_pos1 = (right_overhang - left_overhang) / 2, 0
            background_pos2 = (right_overhang - left_overhang) / 2, self.axis_length
        else:
            axis_pos2 = self._axis_length, 0
            background_pos1 = 0, (right_overhang - left_overhang) / 2
            background_pos2 = self._axis_length, (right_overhang - left_overhang) / 2

        avg.LineNode(
            parent=self._axis_and_tick_div,
            pos1=background_pos1,
            pos2=background_pos2,
            color="fff",
            opacity=0,
            strokewidth=self._axis_config.axis_width + left_overhang + right_overhang
        )
        avg.LineNode(
            parent=self._axis_and_tick_div,
            pos1=(0, 0),
            pos2=axis_pos2,
            color=self._axis_config.axis_color,
            strokewidth=self._axis_config.axis_width
        )
        self.__axis_size = axis_pos2

    def _create_ticks_view(self):
        """
        Creates the view for all ticks with possible markings.
        """
        tick_positions = self._calc_tick_positions()
        left_overhang = self._axis_config.tick_overhang if self._axis_config.tick_side is not TickSide.Right else 0
        right_overhang = self._axis_config.tick_overhang if self._axis_config.tick_side is not TickSide.Left else 0

        # Variables to calculate the size of the whole axis.
        max_marking_size = float('-inf'), float('-inf')

        count = 0
        for pos_value, marking in tick_positions:
            # Check in which direction the axis should go:
            # Decide where a line starts and ends.
            if self._axis_config.axis_orientation is Orientation.Vertical:
                pos1 = -left_overhang, pos_value
                pos2 = right_overhang, pos_value
            else:
                pos_value = self._axis_length - pos_value
                pos1 = pos_value, -left_overhang
                pos2 = pos_value, right_overhang

            # Create the tick.
            avg.LineNode(
                parent=self._axis_and_tick_div,
                pos1=pos1,
                pos2=pos2,
                color=self._axis_config.axis_color,
                strokewidth=self._axis_config.tick_width
            )

            if marking:
                value = self._generate_axis_marking_value(count)
                marking = self._create_marking_view(pos1, pos2, value)
                max_marking_size = (marking.size[0] if marking.size[0] > max_marking_size[0] else max_marking_size[0],
                                    marking.size[1] if marking.size[1] > max_marking_size[1] else max_marking_size[1])
                self._marking_positions.append(pos_value)
                self._markings[value] = marking

            self._tick_positions.append(pos_value)
            count += 1
        self._tick_positions = sorted(self._tick_positions)
        self._marking_positions = sorted(self._marking_positions)

        # Set the size for this axis.
        if self._axis_config.axis_orientation is Orientation.Vertical:
            self.__axis_size = (self.__axis_size[0] + max_marking_size[0] + 2 * (self._axis_config.tick_overhang - 1),
                                self.__axis_size[1])
        else:
            self.__axis_size = (self.__axis_size[0],
                                self.__axis_size[1] + max_marking_size[1] + 2 * (self._axis_config.tick_overhang - 1))

    def _create_marking_view(self, left_top_pos, right_bottom_pos, value):
        """
        Creates the view for the marking.
        :param left_top_pos: The left or upper position of the tick.
        :type left_top_pos: tuple[float, float]
        :param right_bottom_pos: The right or lower position of the tick.
        :type right_bottom_pos: tuple[float, float]
        :param value: The value that should be placed in the marking.
        :type value: str
        :return: The new created marking.
        :rtype: WordsNode
        """
        # Check on which side the marking should be placed:
        # Decide which parameter position is used and some other variables.
        if self._axis_config.marking_side is MarkingSide.Left:
            text_pos = left_top_pos
            text_offset = -1
        else:
            text_pos = right_bottom_pos
            text_offset = 1
        if self._axis_config.axis_orientation is Orientation.Horizontal:
            if self._axis_config.marking_orientation is Orientation.Horizontal:
                text_pos = (text_pos[0] + text_offset * self._axis_config.tick_width / 2,
                            text_pos[1])
            else:
                text_pos = (text_pos[0],
                            text_pos[1] + text_offset * self._axis_config.tick_width / 2)


        if (self._axis_config.axis_orientation is Orientation.Horizontal and self._axis_config.marking_orientation is Orientation.Vertical or
            self._axis_config.axis_orientation is Orientation.Vertical and self._axis_config.marking_orientation is Orientation.Horizontal):
            angle = 0 if self._axis_config.axis_orientation is Orientation.Vertical else pi / 2
            if self._axis_config.marking_side is MarkingSide.Left:
                text_alignment = "right"
            else:
                text_alignment = "left"
        else:
            angle = 0
            text_alignment = "center"

        # Create the marking.
        new_marking = avg.WordsNode(
            parent=self._marking_div,
            text=value,
            alignment=text_alignment,
            pivot=(0, 0),
            angle=angle,
            fontsize=self._axis_config.marking_text_config.font_size,
            color=self._axis_config.marking_text_config.color,
            rawtextmode=True,
            variant=self._axis_config.marking_text_config.font_variant
        )

        # Check in which direction the axis should go:
        # Add the size of the word and the tick width to the position.
        if self._axis_config.axis_orientation is Orientation.Vertical and self._axis_config.marking_orientation is Orientation.Horizontal:
            new_marking.pos = (text_pos[0] + text_offset * self._axis_config.marking_text_config.offset_to_other_element,
                               text_pos[1] - new_marking.size[1] / 2)
        elif self._axis_config.axis_orientation is Orientation.Horizontal and self._axis_config.marking_orientation is Orientation.Vertical:
            new_marking.pos = (text_pos[0] + new_marking.size[1] / 2,
                               text_pos[1] + text_offset * self._axis_config.marking_text_config.offset_to_other_element)
        elif self._axis_config.axis_orientation is Orientation.Vertical and self._axis_config.marking_orientation is Orientation.Vertical:
            new_marking.pos = (text_pos[0] + text_offset * (new_marking.size[0] / 2 + self._axis_config.marking_text_config.offset_to_other_element),
                               text_pos[1] - text_offset * self._axis_config.tick_width / 2)
        elif self._axis_config.axis_orientation is Orientation.Horizontal and self._axis_config.marking_orientation is Orientation.Horizontal:
            new_marking.pos = (text_pos[0] - text_offset * self._axis_config.tick_width / 2,
                               text_pos[1] - new_marking.size[1] / 2 + text_offset * (new_marking.size[1] / 2 + self._axis_config.marking_text_config.offset_to_other_element))

        return new_marking

    def _create_label_view(self):
        """
        Creates the view for the label of this axis.
        """
        # Check in which direction the axis should go:
        if self._axis_config.axis_orientation is Orientation.Vertical:
            alignment = "center"
        else:
            alignment = "left" if self._axis_config.label_pos is LabelPosition.Top else "right"

        self._label_node = avg.WordsNode(
            parent=self._label_and_unit_div,
            text=self._data_desc.label,
            alignment=alignment,
            fontsize=self._axis_config.label_text_config.font_size,
            color=self._axis_config.label_text_config.color,
            rawtextmode=True,
            variant=self._axis_config.label_text_config.font_variant
        )

        # Check in which direction the axis should go:
        if self._axis_config.axis_orientation is Orientation.Vertical:
            # Check on which side the label should be
            if self._axis_config.label_pos is LabelPosition.Top:
                self._label_node.pos = 0, -(self._axis_config.label_text_config.offset_to_other_element + self._label_node.size[1])
            else:
                self._label_node.pos = 0, self._axis_length + self._axis_config.label_text_config.offset_to_other_element
        else:
            # Check on which side the label should be
            if self._axis_config.label_pos is LabelPosition.Top:
                self._label_node.pos = self._axis_length + self._axis_config.label_text_config.offset_to_other_element, -self._label_node.size[1] / 2
            else:
                self._label_node.pos = -self._axis_config.label_text_config.offset_to_other_element, -self._label_node.size[1] / 2

    def _calc_tick_positions(self):
        """
        Calculate all the tick positions on the axis.
        
        :return: A list of all positions for the ticks and if the tick will get a marking.
        :rtype: list[tuple[float, bool]]
        """
        # Check in which direction the data should go:
        # Make the offset negative to calculate the position in the other direction.
        tick_distance = self._tick_distance
        if self._axis_config.data_direction is DataDirection.Negative:
            tick_distance *= -1

        tick_positions = []
        for i in range(0, self._axis_config.data_steps):
            # Get the start value according to the alignment of the data.
            # The start position is the opposite of the direction: positive -> top/right, negative -> bottom/left.
            start = self._axis_config.top_offset if self._axis_config.data_direction is DataDirection.Positive else self._axis_length - self._axis_config.bottom_offset
            # If only one data step is wished use the first tick.
            pos = start + tick_distance * (i if self._axis_config.data_steps > 1 else 1)
            marking = False
            # Only apply a marking at the firs and last element and an element that was given through the data_tick_step.
            if self._axis_config.marking_steps == 0:
                marking = False
            elif i is 0 or i is self._axis_config.data_steps - 1 or (i % self._axis_config.marking_steps) == 0:
                marking = True
            tick_positions.append((pos, marking))

        return tick_positions

    def _generate_axis_marking_value(self, step):
        """
        Calculates the value as a string at the step position.
        
        :param step: The position of the value to convert.
        :type step: int
        :return: The correct value for the step.
        :rtype: str
        """
        marking = "None"
        # Check the data type of the displayed data:
        # Create the right marking.
        if DataType.is_number(self._data_desc.data_type):
            value = self._data_desc.data[1] - step * self._value_step
            # Convert the marking correctly.
            marking = "%i" % value if self._data_desc.data_type is DataType.Integer else "%.2f" % value
        elif DataType.is_string(self._data_desc.data_type):
            value = self._data_desc.data[-step - 1]
            marking = "%s" % value
        elif self._data_desc.data_type is DataType.DateTime:
            value = self._data_desc.data[1] - step * self._value_step
            marking = value.strftime("%d.%m.%Y %H:%M:%S")
        elif self._data_desc.data_type is DataType.Date:
            value = self._data_desc.data[1] - step * self._value_step
            marking = value.strftime("%d.%m.%Y")
        elif self._data_desc.data_type is DataType.Time:
            value = self._data_desc.data[1] - step * self._value_step
            marking = value.strftime("%H:%M:%S")
        elif self._data_desc.data_type is DataType.Day:
            value = self._data_desc.data[1] - step * self._value_step
            marking = value.strftime("%d.%m.")

        return marking

    def _check_data_type(self, value):
        """
        Checks of a gotten value matches with the given data.
        
        :param value: The value to check.
        :type value: object
        :return: True if the value is usable on this axis.
        :rtype: bool
        """
        # Catch all cases if the value has not the right data type and the value is not in the data set.
        if self._data_desc.data_type is DataType.Integer or self._data_desc.data_type is DataType.IntegerSum:
            if not isinstance(value, int) or self._data_desc.data[0] > value > self._data_desc.data[1]:
                return False
        elif self._data_desc.data_type is DataType.Float or self._data_desc.data_type is DataType.FloatSum:
            if not isinstance(value, float) or self._data_desc.data[0] > value > self._data_desc.data[1]:
                return False
        elif DataType.is_string(self._data_desc.data_type):
            if not (isinstance(value, str) or isinstance(value, unicode)) or value not in self._data_desc.data:
                return False
        elif DataType.is_datetime(self._data_desc.data_type):
            if not isinstance(value, datetime.datetime) or self._data_desc.data[0] > value > self._data_desc.data[1]:
                return False

        return True

    def _calc_axis_complete_size(self):
        """
        Calculates the complete size with the label and the ticks of the axis.

        :return: The size of the axis.
        :rtype: float
        """
        if not self._axis_config.show_label:
            return self.__axis_size

        # Check in which direction the axis should go:
        if self._axis_config.axis_orientation is Orientation.Vertical:
            return (self.__axis_size[0] if self.__axis_size[0] > self._label_node.size[0] else self._label_node.size[0],
                    self.__axis_size[1] + self._axis_config.label_text_config.offset_to_other_element + self._label_node.size[1])
        else:
            return (self.__axis_size[0] + self._axis_config.label_text_config.offset_to_other_element + self._label_node.size[0],
                    self.__axis_size[1] if self.__axis_size[1] > self._label_node.size[1] else self._label_node.size[1])
