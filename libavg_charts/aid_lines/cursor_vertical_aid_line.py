from libavg_charts.aid_lines.cursor_aid_line import CursorAidLine


class CursorVerticalAidLine(CursorAidLine):
    def __init__(self, **kwargs):
        """
        :param kwargs: Other parameters for the base.
        """
        super(CursorVerticalAidLine, self).__init__(**kwargs)

    def _draw_horizontal_aid_line(self, pos):
        return None
