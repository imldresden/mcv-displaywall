from libavg_charts.configurations.text_label_configuration import TextMarkingConfiguration
from libavg_charts.utils.default_values import IntersectionDefaults


class IntersectionConfiguration(object):
    """
    A container that holds all values necessary for intersections
    """
    def __init__(self, show_intersections=IntersectionDefaults.SHOW_INTERSECTIONS, show_label=IntersectionDefaults.SHOW_LABEL,
                 radius=IntersectionDefaults.INTERSECTION_RADIUS, filled=IntersectionDefaults.INTERSECTION_FILLED,
                 color=IntersectionDefaults.INTERSECTION_COLOR, stroke_width=IntersectionDefaults.INTERSECTION_STROKE_WIDTH,
                 label_content_type=IntersectionDefaults.LABEL_CONTENT_TYPE, label_content=IntersectionDefaults.LABEL_CONTENT,
                 use_data_object_color_for_intersection_labels=IntersectionDefaults.INTERSECTION_LABEL_COLOR_USE_DATA_OBJECT_COLOR,
                 marking_text_config=None):
        """
        :param show_intersections: Should the intersections of the aid line and the data objects be shown?
        :type show_intersections: bool
        :param show_label: Should a label at the intersections be shown? This will only be used if intersection should be placed in the first place.
        :type show_label: bool
        :param radius: The radius of the intersection points.
        :type radius: float
        :param filled: Should the intersections be filled?
        :type filled: bool
        :param color: The color of the intersection circles.
        :type color: avg.Color
        :param stroke_width: The stroke width for the intersection labels.
        :type stroke_width: float
        :param label_content_type: It describes the content that should be shown on the intersection labels. Can be either 'axis' or 'data_object'.
        :type label_content_type: str
        :param label_content: Describes the key which should be used for the labels values. If the content_type is axis, it will take an 'axis' with the
                              same key. If the content_type is 'data_object' it will use a specific value from the data object the intersection is placed on.
                              If this is 'obj_name' and the content_type is 'data_object' the name of the object will be used.
        :type label_content: str
        :param use_data_object_color_for_intersection_labels: Should the here given color, or the color of the selected data object be used?
        :type use_data_object_color_for_intersection_labels: bool
        :param marking_text_config: An extra configuration for the label appearance.
        :type marking_text_config: TextMarkingConfiguration
        """
        self.show_intersections = show_intersections
        self.show_label = show_label
        self.radius = radius
        self.filled = filled
        self.color = color
        self.stroke_width = stroke_width
        self.label_content_type = label_content_type
        self.label_content = label_content
        self.use_data_object_color_for_intersection_labels = use_data_object_color_for_intersection_labels
        self.marking_text_config = marking_text_config if marking_text_config else TextMarkingConfiguration()
