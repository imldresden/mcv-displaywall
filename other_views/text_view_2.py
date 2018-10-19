from libavg import avg

from utils import colors


class TextView2(avg.DivNode):
    def __init__(self, text_elements, element_size, alignment="center",
                 font_size=13, background_color=colors.BLACK, font_colors=None, default_font_color=colors.WHITE_DARKEN_1,
                 element_offset=0, padding_top=0, padding_bottom=0,
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
        super(TextView2, self).__init__(**kwargs)
        self.registerInstance(self, parent)
        self.sensitive = False

        self.__text_elements = text_elements
        self.__element_size = element_size
        self.__font_size = font_size
        self.__font_color = None
        self.__background_color = None

        self.__element_offset = element_offset
        self.__padding_top = padding_top
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

        text_size = self.__element_size, self.size[1] - self.__padding_top - self.__padding_bottom
        inner_size = (text_size[0] * len(self.__text_elements) + self.__element_offset * (len(self.__text_elements) - 1),
                      self.size[1] - self.__padding_top - self.__padding_bottom)
        pos_offset = (self.size[0] - inner_size[0]) / 2
        pos = 0, self.__padding_top + (inner_size[1]) / 2

        for text, font_color in zip(self.__text_elements, self.__font_colors):
            text_node = avg.WordsNode(
                parent=self.__internal_view,
                size=text_size,
                text=text,
                rawtextmode=True,
                wrapmode="word",
                alignment="center" if len(self.__text_elements) == 1 else "left",
                color=font_color,
                fontsize=self.__font_size
            )
            text_node.pos = pos[0] + pos_offset, pos[1] - text_node.size[1] / 2
            if len(self.__text_elements) == 1:
                text_node.pos = text_node.pos[0] + text_node.size[0] / 2, text_node.pos[1]
            pos = pos[0] + self.__element_offset + text_size[0], pos[1]

            self.__text_nodes.append(text_node)
