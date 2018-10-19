from libavg_charts.aid_lines.deposit_aid_line import DepositAidLine


class DepositHorizontalAidLine(DepositAidLine):
    def __init__(self, **kwargs):
        """
        :param kwargs: Other parameters for the base.
        """
        super(DepositHorizontalAidLine, self).__init__(**kwargs)

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
        return None
