from libavg_charts.aid_lines.cursor_aid_line import CursorAidLine


class CursorHorizontalAidLine(CursorAidLine):
    def __init__(self, **kwargs):
        """
        :param kwargs: Other parameters for the base.
        """
        super(CursorHorizontalAidLine, self).__init__(**kwargs)

    def _draw_vertical_aid_line(self, pos):
        return None
