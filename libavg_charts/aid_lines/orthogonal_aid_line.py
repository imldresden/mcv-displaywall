from libavg import avg

from configs import config_app
from data_models.data_enums import DataSelectionState
from libavg_charts.aid_lines.aid_line_controller_base import AidLineControllerBase
from libavg_charts.aid_lines.helper.data_point_snapping_method_holder import DataPointSnappingMethodHolder
from libavg_charts.aid_lines.helper.intersection_method_holder import IntersectionMethodHolder
from libavg_charts.axis.chart_axis_enums import Orientation
from libavg_charts.axis.interactive_div_node import InteractiveDivNode
from libavg_charts.utils.default_values import AidLineDefaults


class OrthogonalAidLine(AidLineControllerBase):
    def __init__(self, aid_line_to_axis_offset=AidLineDefaults.TO_AXIS_OFFSET, **kwargs):
        """
        :param aid_line_to_axis_offset: The area at the inner border of the aid line area where the aid lines should be deleted if the movements ends there.
        :type aid_line_to_axis_offset: float
        :param kwargs: Other parameters for the base.
        """
        self._aid_line_to_axis_offset = aid_line_to_axis_offset

        super(OrthogonalAidLine, self).__init__(**kwargs)

    def _draw_horizontal_aid_line(self, pos, with_outer=True):
        """
        Draws a horizontal aid line.

        :param pos: The position of the cursor.
        :type pos: tuple[float, float]
        :param with_outer: If the outer part of the line should be drawn.
        :type with_outer: bool
        :return: The created aid line.
        :rtype: InteractiveDivNode
        """
        aid_line = InteractiveDivNode(
            parent=self._aid_lines_div,
            pos=(0, pos[1])
        )
        if with_outer:
            avg.LineNode(
                parent=aid_line,
                pos1=(self._aid_line_area[0] - self._aid_line_config.extra_length, 0),
                pos2=(self._aid_line_area[2] + self._aid_line_config.extra_length, 0),
                color=self._aid_line_config.color,
                opacity=self._aid_line_config.outer_line_opacity,
                strokewidth=self._aid_line_config.outer_line_width
            )
        avg.LineNode(
            parent=aid_line,
            pos1=(self._aid_line_area[0] - self._aid_line_config.extra_length, 0),
            pos2=(self._aid_line_area[2] + self._aid_line_config.extra_length, 0),
            color=self._aid_line_config.color,
            strokewidth=self._aid_line_config.inner_line_width
        )

        return aid_line

    def _draw_vertical_aid_line(self, pos, with_outer=True):
        """
        Draws a vertical aid line.

        :param pos: The position of the cursor.
        :type pos: tuple[float, float]
        :param with_outer: If the outer part of the line should be drawn.
        :type with_outer: bool
        :return: The created aid line.
        :rtype: InteractiveDivNode
        """
        aid_line = InteractiveDivNode(
            parent=self._aid_lines_div,
            pos=(pos[0], 0)
        )
        if with_outer:
            avg.LineNode(
                parent=aid_line,
                pos1=(0, self._aid_line_area[1] - self._aid_line_config.extra_length),
                pos2=(0, self._aid_line_area[3] + self._aid_line_config.extra_length),
                color=self._aid_line_config.color,
                opacity=self._aid_line_config.outer_line_opacity,
                strokewidth=self._aid_line_config.outer_line_width
            )
        avg.LineNode(
            parent=aid_line,
            pos1=(0, self._aid_line_area[1] - self._aid_line_config.extra_length),
            pos2=(0, self._aid_line_area[3] + self._aid_line_config.extra_length),
            color=self._aid_line_config.color,
            strokewidth=self._aid_line_config.inner_line_width
        )

        return aid_line

    def _check_aid_line_pos(self, aid_line_pos, orientation):
        """
        Checks if the aid line is still in the chart.

        :param aid_line_pos: The pos of the aid line to check.
        :type aid_line_pos: tuple[float, float]
        :return: The new position for the aid line if it was outside or on the border of the chart. None if it was inside.
                 And a bool if the position lies on the border (calculated with the extra offset).
        :rtype: tuple[tuple[float, float], bool]
        """
        pos = None
        in_border_area = False

        if orientation is Orientation.Horizontal:
            # Is the aid line greater or less the top and bottom border with respect to the offset?
            if aid_line_pos[1] > self._aid_line_area[3] - self._aid_line_to_axis_offset:
                in_border_area = True
                # Would the line be outside of the area?
                if aid_line_pos[1] >= self._aid_line_area[3]:
                    pos = aid_line_pos[0], self._aid_line_area[3]
            if aid_line_pos[1] < self._aid_line_area[1] + self._aid_line_to_axis_offset:
                in_border_area = True
                # Would the line be outside of the area?
                if aid_line_pos[1] <= self._aid_line_area[1]:
                    pos = aid_line_pos[0], self._aid_line_area[1]
        else:
            # Is the aid line greater or less the left and right border with respect to the offset?
            if aid_line_pos[0] > self._aid_line_area[2] - self._aid_line_to_axis_offset:
                in_border_area = True
                # Would the line be outside of the area?
                if aid_line_pos[0] >= self._aid_line_area[2]:
                    pos = self._aid_line_area[2], aid_line_pos[1]
            if aid_line_pos[0] < self._aid_line_area[0] + self._aid_line_to_axis_offset:
                in_border_area = True
                # Would the line be outside of the area?
                if aid_line_pos[0] <= self._aid_line_area[0]:
                    pos = self._aid_line_area[0], aid_line_pos[1]

        return pos, in_border_area

    def _check_for_snapping(self, pos, orientation):
        """
        Checks if a given pos needs to be moved to a snapping position.

        :param pos: The new pos for the given aid line.
        :type pos: tuple[float, float]
        :param orientation: The orientation the aid line is placed on.
        :type orientation: Orientation
        :return: The new pos if snapping is activated or the old if not.
        :rtype: tuple[float, float]
        """
        if self._use_tick_snapping:
            return self.__get_tick_snapping_pos(pos, orientation)
        if self._use_data_point_snapping:
            return self.__get_data_point_snapping_pos(pos, orientation)
        return pos

    def __get_tick_snapping_pos(self, pos, orientation):
        """
        Calculates a new position for the tick snapping.

        :param pos: The new pos for the given aid line.
        :type pos: tuple[float, float]
        :param orientation: The orientation the aid line is placed on.
        :type orientation: Orientation
        :return: The new pos if tick snapping is activated or the old if not.
        :rtype: tuple[float, float]
        """
        if orientation is Orientation.Horizontal:
            # TODO: Use not the first index for the axis either a index given from the user.
            axis = self._chart.vertical_axis_views.values()[0]
            tick_index = self._get_next_tick_index(
                tick_positions=axis.tick_positions,
                aid_line_pos=(pos[0], pos[1] - axis.pos[1]),
                coordinate=1
            )
            tick_pos = (pos[0], axis.tick_positions[tick_index] + axis.pos[1])
        else:  # if orientation is Orientation.Vertical:
            # TODO: Use not the first index for the axis either a index given from the user.
            axis = self._chart.horizontal_axis_views.values()[0]
            tick_index = self._get_next_tick_index(
                tick_positions=axis.tick_positions,
                aid_line_pos=(pos[0] - axis.pos[0], pos[1]),
                coordinate=0
            )
            tick_pos = (axis.tick_positions[tick_index] + axis.pos[0], pos[1])

        return tick_pos

    def __get_data_point_snapping_pos(self, pos, orientation):
        """
        Calculates a new position for the data point snapping.

        :param pos: The new pos for the given aid line.
        :type pos: tuple[float, float]
        :param orientation: The orientation the aid line is placed on.
        :type orientation: Orientation
        :return: The new pos if tick snapping is activated or the old if not.
        :rtype: tuple[float, float]
        """
        nearest_pos = DataPointSnappingMethodHolder.get_snapping_with_data_objects(
            diagram_type=type(self._chart),
            line_orientation=orientation,
            data_objects=self._chart.data_object_nodes,
            line_pos=pos[0] if orientation is Orientation.Vertical else pos[1]
        )

        if nearest_pos is not None:
            dist = abs(nearest_pos - (pos[0] if orientation is Orientation.Vertical else pos[1]))
            if dist < AidLineDefaults.DATA_POINT_SNAPPING_RANGE_CM * config_app.pixel_per_cm:
                pos = (nearest_pos, pos[1]) if orientation is Orientation.Vertical else (pos[0], nearest_pos)

        return pos

    def _get_intersections(self, aid_line_positions, aid_line_orientations, data_object_nodes=None):
        """
        Calculates the intersections.

        :param aid_line_positions: The position of the aid line.
        :type aid_line_positions: list[tuple[float, float]]
        :param aid_line_orientations: The orientation of the aid line.
        :type aid_line_orientations: list[Orientation]
        :param data_object_nodes: The data object nodes to check for.
        :type data_object_nodes: dict[str, Node]
        :return: The intersected nodes and their positions.
        :rtype: dict[str, list[tuple[float, float]]]
        """
        all_intersections = {}
        for pos, orientation in zip(aid_line_positions, aid_line_orientations):
            results = IntersectionMethodHolder.get_intersections_with_data_objects(
                diagram_type=type(self._chart),
                line_orientation=orientation,
                data_objects=self._chart.data_objects,
                data_object_nodes=self._chart.data_object_nodes,
                line_pos=pos[1] if orientation is Orientation.Horizontal else pos[0],
                only_at_data_points=self._labels_only_at_data_points
            )

            for obj_id, intersections in results.iteritems():
                if obj_id not in all_intersections:
                    all_intersections[obj_id] = []

                for intersection_pos in intersections:
                    if intersection_pos in all_intersections[obj_id]:
                        continue
                    all_intersections[obj_id].append(intersection_pos)

        return all_intersections
