from libavg_charts.utils.default_values import TextLabelDefaults, TextMarkingDefaults, TextChartLabelDefaults


class TextLabelConfiguration(object):
    def __init__(self, color=TextLabelDefaults.COLOR, font_size=TextLabelDefaults.FONT_SIZE,
                 offset_to_other_element=TextLabelDefaults.OFFSET_TO_OTHER_ELEMENT,
                 font_variant=TextLabelDefaults.FONT_VARIANT):
        """
        :param color: The color fo the text to show.
        :type color: avg.Color
        :param font_size: The size of the font for the text.
        :type font_size: int
        :param offset_to_other_element: The space between the text itself and the element it is connected with.
        :type offset_to_other_element: int
        :param font_variant: The variant (like 'bold') for the text. It is at default '' (empty).
        :type font_variant: str
        """
        self.color = color
        self.font_size = font_size
        self.offset_to_other_element = offset_to_other_element
        self.font_variant = font_variant


class TextMarkingConfiguration(TextLabelConfiguration):
    def __init__(self, color=TextMarkingDefaults.COLOR, font_size=TextMarkingDefaults.FONT_SIZE,
                 offset_to_other_element=TextMarkingDefaults.OFFSET_TO_OTHER_ELEMENT,
                 font_variant=TextMarkingDefaults.FONT_VARIANT):
        """
        :param color: The color fo the text to show.
        :type color: avg.Color
        :param font_size: The size of the font for the text.
        :type font_size: int
        :param offset_to_other_element: The space between the text itself and the element it is connected with.
        :type offset_to_other_element: int
        :param font_variant: The variant (like 'bold') for the text. It is at default '' (empty).
        :type font_variant: str
        """
        super(TextMarkingConfiguration, self).__init__(
            color=color,
            font_size=font_size,
            offset_to_other_element=offset_to_other_element,
            font_variant=font_variant
        )


class TextChartLabelConfiguration(TextLabelConfiguration):
    def __init__(self, color=TextChartLabelDefaults.COLOR, font_size=TextChartLabelDefaults.FONT_SIZE,
                 offset_to_other_element=TextChartLabelDefaults.OFFSET_TO_OTHER_ELEMENT,
                 font_variant=TextChartLabelDefaults.FONT_VARIANT):
        """
        :param color: The color fo the text to show.
        :type color: avg.Color
        :param font_size: The size of the font for the text.
        :type font_size: int
        :param offset_to_other_element: The space between the text itself and the element it is connected with.
        :type offset_to_other_element: int
        :param font_variant: The variant (like 'bold') for the text. It is at default '' (empty).
        :type font_variant: str
        """
        super(TextChartLabelConfiguration, self).__init__(
            color=color,
            font_size=font_size,
            offset_to_other_element=offset_to_other_element,
            font_variant=font_variant
        )
