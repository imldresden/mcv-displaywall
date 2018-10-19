from libavg_charts.aid_lines.selection_aid_line import SelectionAidLine


class SelectionVerticalAidLine(SelectionAidLine):
    def __init__(self, **kwargs):
        """
        :param kwargs: Other parameters for the base.
        """
        super(SelectionVerticalAidLine, self).__init__(**kwargs)

    def _draw_horizontal_aid_line(self, pos):
        return None

    def _draw_horizontal_selection_line(self, pos):
        return None
