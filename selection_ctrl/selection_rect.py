from libavg import avg
from selection import Selection
import configs.visual_data as vs_config
# from ui_elements.view.linerectnode import LineRectNode


class SelectionRect(Selection):
    def __init__(self, parent):
        """
        This class draws a rectangle without content that is used to indicate a selection area.

        Args:
            parent (avg.DivNode): Node that contains the rectangle.
        """

        self.__node = avg.RectNode(
            parent=parent,
            strokewidth=3,
            color=vs_config.SELECTION_FEEDBACK_COLOR,
            sensitive=False
        )

    def polygon(self, relative_div=None):
        """
            To be used to get the points that define the rectangle.

            Returns (list): A list of the rectangle corners.

            """
        if self.__node is None:
            return []

        a = self.__node.pos
        b = (self.__node.pos[0] + self.__node.size[0], self.__node.pos[1])
        c = (self.__node.pos[0] + self.__node.size[0], self.__node.pos[1] + self.__node.size[1])
        d = (self.__node.pos[0], self.__node.pos[1] + self.__node.size[1])

        if relative_div is not None:
            return [a-relative_div.pos, b-relative_div.pos, c-relative_div.pos, d-relative_div.pos, a-relative_div.pos]
        return [a, b, c, d, a]

    def update(self, pos=None, size=None):
        """
        Updates the position and size of the rectangle.

        Args:
            pos (tuple): New position of the rectangle, defined by the upper left corner.
            size (tuple): New size of the rectangle, used to compute the other corners.

        """
        self.__node.pos = (pos[0]-size[0]/2, pos[1]-size[1]/2)
        self.__node.size = size

    def clear(self):
        # Remove the rectangle from the parent node.
        if self.__node is not None:
            self.__node.unlink()

    def flash(self):
        # print "flash"
        self.__node.fillcolor='bfd571'
        anim = avg.LinearAnim(
            node=self.__node,
            attrName="fillopacity",
            duration=200,
            startValue=0.0,
            endValue=1.0,
            stopCallback=self.__unflash
        )
        anim.start()

    def __unflash(self):
        anim = avg.LinearAnim(
            node=self.__node,
            attrName="fillopacity",
            duration=200,
            startValue=1.0,
            endValue=0.0,
        )
        anim.start()
