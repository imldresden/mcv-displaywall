from libavg_charts.aid_lines.selection_aid_line import SelectionAidLine


class SelectionHorizontalAidLine(SelectionAidLine):
    def __init__(self, **kwargs):
        """
        :param kwargs: Other parameters for the base.
        """
        super(SelectionHorizontalAidLine, self).__init__(**kwargs)

    def _draw_vertical_aid_line(self, pos):
        return None

    def _draw_vertical_selection_line(self, pos):
        return None
