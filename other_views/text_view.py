from libavg import avg
from libavg_charts.axis.chart_axis_enums import Orientation


class TextView(avg.DivNode):
    def __init__(self, text_elements, font_size=13, text_alignment="left", order_orientation=Orientation.Horizontal,
                 background_color=colors.BLACK, font_colors=None, default_font_color=colors.WHITE_DARKEN_1,
                 element_offset=0, padding_left=0, padding_top=0, padding_right=0, padding_bottom=0,
                 parent=None, **kwargs):
        """
        :param text_elements: List of all text elements that should be shown in this view.
        :type text_elements: list[str]
        :param element_offset: The offset between each text element.
        :type element_offset: float
        :param font_size: The size of the font.
        :type font_size: float
        :type parent: DivNode
        :param kwargs: Other parameters for the view.
        """
        super(TextView, self).__init__(**kwargs)
        self.registerInstance(self, parent)
        self.sensitive = False

        self.__order_orientation = order_orientation
        self.__text_elements = text_elements
        self.__font_size = font_size
        self.__text_alignment = text_alignment
        self.__font_color = None
        self.__background_color = None

        self.__element_offset = element_offset
        self.__padding_left = padding_left
        self.__padding_top = padding_top
        self.__padding_right = padding_right
        self.__padding_bottom = padding_bottom

        self.__default_font_color = default_font_color
        self.__font_colors = font_colors or [default_font_color] * len(self.__text_elements)
        self.__background_color = background_color

        self.__internal_view = avg.DivNode(parent=self)
        self.__background_rect = None
        self.__text_nodes = []
        self.draw()

    @property
    def text_elements(self):
        """
        :rtype: list[str]
        """
        return self.__text_elements

    @text_elements.setter
    def text_elements(self, value):
        """
        :type value: list[str]
        """
        if len(self.__font_colors) < len(value):
            for i in range(len(value) - len(self.__font_colors)):
                self.__font_colors.append(self.__default_font_color)
        self.__font_colors = self.__font_colors[:len(value)]

        self.__text_elements = value

    @property
    def default_font_color(self):
        """
        :rtype: avg.Color
        """
        return self.__default_font_color

    @property
    def font_colors(self):
        """
        :rtype: list[avg.Color]
        """
        return self.__font_colors

    @font_colors.setter
    def font_colors(self, value):
        """
        :type value: list[avg.Color]
        """
        if len(value) < len(self.__text_elements):
            for i in range(len(self.__text_elements) - len(value)):
                value.append(self.__default_font_color)

        self.__font_colors = value

    @property
    def text_alignment(self):
        """
        :rtype: str
        """
        return self.__text_alignment

    @text_alignment.setter
    def text_alignment(self, value):
        """
        :type value: str
        """
        self.__text_alignment = value

    def draw(self):
        """
        Draws itself.
        """
        if self.__background_rect is None:
            self.__background_rect = avg.RectNode(
                parent=self.__internal_view,
                size=self.size,
                strokewidth=0,
                fillopacity=1,
                fillcolor=self.__background_color
            )
        self.__draw_text()

    def __draw_text(self):
        """
        Draws only the text.
        """
        for text_node in self.__text_nodes:
            text_node.unlink(True)
        self.__text_nodes = []

        if len(self.__text_elements) == 0:
            return

        inner_size = self.size[0] - self.__padding_left - self.__padding_right, self.size[1] - self.__padding_top - self.__padding_bottom
        element_offset = float(self.__element_offset * (len(self.__text_elements) - 1)) / len(self.__text_elements)

        if self.__order_orientation is Orientation.Horizontal:
            text_size = inner_size[0], inner_size[1] / len(self.__text_elements) - element_offset
            pos_offset = 0, text_size[1] + self.__element_offset
            pos = self.__padding_left + (inner_size[0]) / 2, self.__padding_top
        else:
            text_size = inner_size[0] / len(self.__text_elements) - element_offset, inner_size[1]
            pos_offset = text_size[0] + self.__element_offset, 0
            pos = self.__padding_left, self.__padding_top + (inner_size[1]) / 2

        for text, font_color in zip(self.__text_elements, self.__font_colors):
            text_node = avg.WordsNode(
                parent=self.__internal_view,
                size=text_size,
                text=text,
                rawtextmode=True,
                wrapmode="word",
                alignment=self.__text_alignment,
                color=font_color,
                fontsize=self.__font_size
            )
            if self.__order_orientation is Orientation.Horizontal:
                text_node.pos = pos[0] - text_node.size[0] / 2, pos[1]
                if self.__text_alignment == "center":
                    text_node.pos = text_node.pos[0], text_node.pos[1] + text_node.size[1] / 2
            else:
                text_node.pos = pos[0], pos[1] - text_node.size[1] / 2
                if self.__text_alignment == "center":
                    text_node.pos = text_node.pos[0] + text_node.size[0] / 2, text_node.pos[1]

            pos = pos[0] + pos_offset[0], pos[1] + pos_offset[1]

            self.__text_nodes.append(text_node)
