from selection_ctrl.utils.default_values import SelectionColorMapperDefaults


class SelectionColorMapper(object):
    # key -> selection id     value -> color
    __selection_color_for_id = {}
    __selection_color_count = [0] * len(SelectionColorMapperDefaults.COLORS)

    @staticmethod
    def get_next_selection_color(selection_set_id):
        """
        Returns the color for the given selection id.

        :param selection_set_id: The id for the selection the color is for.
        :type selection_set_id: str
        :return: The color.
        :rtype: avg.Color
        """
        if selection_set_id not in SelectionColorMapper.__selection_color_for_id:
            index = SelectionColorMapper.__selection_color_count.index(min(SelectionColorMapper.__selection_color_count))
            SelectionColorMapper.__selection_color_count[index] += 1
            color = SelectionColorMapperDefaults.COLORS[index]
            SelectionColorMapper.__selection_color_for_id[selection_set_id] = color

        return SelectionColorMapper.__selection_color_for_id[selection_set_id]

    @staticmethod
    def get_selection_color_for(selection_set_id):
        """
        Searches for a color for a given selection set id.

        :param selection_set_id: The id for the selection the color is for.
        :type selection_set_id: str
        :return: The color.
        :rtype: avg.Color
        """
        if selection_set_id not in SelectionColorMapper.__selection_color_for_id:
            return None

        return SelectionColorMapper.__selection_color_for_id[selection_set_id]

    @staticmethod
    def remove_selection_id(selection_set_id):
        """
        Removes a selection id from this mapper.

        :param selection_set_id: The selection id that should be removed.
        :type selection_set_id: str
        """
        if selection_set_id not in SelectionColorMapper.__selection_color_for_id:
            return

        color = SelectionColorMapper.__selection_color_for_id.pop(selection_set_id)
        SelectionColorMapper.__selection_color_count[SelectionColorMapperDefaults.COLORS.index(color)] -= 1
