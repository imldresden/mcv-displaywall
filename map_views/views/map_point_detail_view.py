from math import pi

from libavg import avg, gesture

from configs import config_app
from configs.config_recognizer import CommonRecognizerDefaults
from data_models.attribute import Attribute
from data_models.data_desciption import DataDescription
from data_models.data_enums import DataType
from data_models.data_object import DataObject
from divico_ctrl.translation import T
from libavg_charts.axis.chart_axis_enums import Orientation
from libavg_charts.charts.bar_chart import BarChart
from libavg_charts.configurations.chart_axis_configuration import ChartAxisConfiguration, TextChartLabelConfiguration
from libavg_charts.configurations.chart_configuration import ChartConfiguration
from libavg_charts.utils.default_values import TextChartLabelDefaults
from logging_base.study_logging import StudyLog
from map_views.utils.default_values import MapPointDetailViewDefaults as Defaults


# TODO: Create a base class and create specialized detail views. The type should be a parameter for the map view.
from utils import colors


class MapPointDetailView(avg.DivNode):
    def __init__(self, map_point_view, parent=None, **kwargs):
        """
        :param map_point_view: The view this detail view is connected with.
        :type map_point_view: MapPointView
        :type parent: DivNode
        :param kwargs: Other parameters for the div node.
        """
        super(MapPointDetailView, self).__init__(size=(Defaults.SIZE_CM[0] * config_app.pixel_per_cm,
                                                       Defaults.SIZE_CM[1] * config_app.pixel_per_cm),
                                                 **kwargs)
        self.registerInstance(self, parent)

        self.__map_point_view = map_point_view

        self.__tap_recognizers = gesture.TapRecognizer(
            node=self,
            maxTime=CommonRecognizerDefaults.TAP_MAX_TIME,
            maxDist=CommonRecognizerDefaults.TAP_MAX_DIST,
            detectedHandler=self.__on_tap
        )

        self.__triangle_div = avg.DivNode(
            parent=self,
            size=(self.size[0] / 24, self.size[0] / (24 * 1.4)),
            crop=True
        )
        self.__triangle_rect = avg.RectNode(
            parent=self.__triangle_div,
            strokewidth=0,
            fillcolor=colors.GREY,
            fillopacity=1,
            angle=pi/4,
            size=(self.size[0] / Defaults.TRIANGLE_RATIO, self.size[0] / Defaults.TRIANGLE_RATIO),
            pos=(0, -self.size[0] / (Defaults.TRIANGLE_RATIO * 2))
        )
        self.__triangle_div.pos = (self.size[0] - self.__triangle_rect.size[0]) / 2, self.size[1] - 1
        self.__background_rect = avg.RectNode(
            parent=self,
            strokewidth=Defaults.BORDER_WIDTH,
            color=colors.GREY,
            fillcolor=Defaults.BACKGROUND_COLOR,
            fillopacity=Defaults.BACKGROUND_OPACITY,
            size=self.size
        )

        values = zip(self.__map_point_view.point_model.attribute_dict["crime_types"], self.__map_point_view.point_model.attribute_dict["crime_types_count"])
        data_objects = [DataObject(ctn, [Attribute("crime_type_name", DataType.String, [ctn]), Attribute("crimes_count", DataType.Integer, [ctc])]) for ctn, ctc in values]
        x_data_desc = DataDescription.generate_from_data_objects(data_objects=data_objects, description_name="crimes_count")
        x_data_desc.data = [0, x_data_desc.data[1]]
        y_data_desc = DataDescription.generate_from_data_objects(data_objects=data_objects, description_name="crime_type_name")
        # TODO: Use default values.
        self.__crime_types_view = BarChart(
            parent=self,
            size=(self.size[0], self.size[1] * Defaults.CHART_RATIO / Defaults.CHART_TEXT_RATIO),
            data=data_objects,
            data_keys_for_selection=["crime_type_name"],
            label=T.tl("Crimes / Types") + "           ",
            orientation=Orientation.Horizontal,
            axis_cross_offset=0,
            bar_spacing=2,
            x_axis_data=x_data_desc,
            x_axis_config=ChartAxisConfiguration(data_steps=5, bottom_offset=0,
                                                 marking_text_config=TextChartLabelConfiguration(font_size=Defaults.MARKING_FONT_SIZE, offset_to_other_element=Defaults.OFFSET_TO_OTHER),
                                                 label_text_config=TextChartLabelConfiguration(font_size=Defaults.LABEL_FONT_SIZE, offset_to_other_element=Defaults.OFFSET_TO_OTHER)),
            y_axis_data=y_data_desc,
            y_axis_config=ChartAxisConfiguration(show_label=False, bottom_offset=10, top_offset=10,
                                                 marking_text_config=TextChartLabelConfiguration(font_size=Defaults.MARKING_FONT_SIZE, offset_to_other_element=Defaults.OFFSET_TO_OTHER),
                                                 label_text_config=TextChartLabelConfiguration(font_size=Defaults.LABEL_FONT_SIZE, offset_to_other_element=Defaults.OFFSET_TO_OTHER)),
            chart_config=ChartConfiguration(padding_left=Defaults.CHART_P_LEFT, padding_top=Defaults.CHART_P_TOP, padding_right=Defaults.CHART_P_RIGHT, padding_bottom=Defaults.CHART_P_BOTTOM,
                                            label_text_config=TextChartLabelConfiguration(font_size=Defaults.TITLE_FONT_SIZE, offset_to_other_element=Defaults.OFFSET_TO_OTHER))
        )
        self.__crime_types_view.draw_chart()

        self.__districts_view = avg.DivNode(
            parent=self,
            pos=(0, self.size[1] * Defaults.CHART_RATIO / Defaults.CHART_TEXT_RATIO),
            size=(self.size[0], self.size[1] / Defaults.CHART_TEXT_RATIO)
        )
        self.__district_label_node = avg.WordsNode(
            parent=self.__districts_view,
            text="{}:".format(T.tl("Districts")),
            alignment="left",
            rawtextmode=True,
            fontsize=Defaults.TITLE_FONT_SIZE,
            color=TextChartLabelDefaults.COLOR
        )
        self.__district_label_node.pos = Defaults.OFFSET_TO_OTHER * 2, (self.__districts_view.size[1] - self.__district_label_node.size[1]) / 2
        self.__districts_node = avg.WordsNode(
            parent=self.__districts_view,
            text=", ".join(self.__map_point_view.point_model.attribute_dict["districts"]),
            alignment="left",
            rawtextmode=True,
            fontsize=Defaults.MARKING_FONT_SIZE,
            color=TextChartLabelDefaults.COLOR
        )
        self.__districts_node.pos = (self.__district_label_node.pos[0] + self.__district_label_node.size[0] + Defaults.OFFSET_TO_OTHER * 2,
                                     self.__district_label_node.pos[1] + float(self.__district_label_node.size[1] - self.__districts_node.size[1]) / 2)

        close_size = self.size[0] / Defaults.CLOSE_BUTTON_RATIO
        self.__close_div = avg.DivNode(
            parent=self,
            pos=(self.size[0] - close_size - Defaults.BORDER_WIDTH, Defaults.BORDER_WIDTH),
            size=(close_size, close_size),
            crop=True
        )
        avg.LineNode(
            parent=self.__close_div,
            pos1=(0, 0),
            pos2=(close_size, close_size),
            strokewidth=Defaults.CLOSE_BUTTON_STROKE_WIDTH,
            color=Defaults.CLOSE_BUTTON_COLOR
        )
        avg.LineNode(
            parent=self.__close_div,
            pos1=(close_size, 0),
            pos2=(0, close_size),
            strokewidth=Defaults.CLOSE_BUTTON_STROKE_WIDTH,
            color=Defaults.CLOSE_BUTTON_COLOR
        )

        self.__close_button_recognizer = gesture.TapRecognizer(
            node=self.__close_div,
            maxTime=CommonRecognizerDefaults.TAP_MAX_TIME,
            maxDist=CommonRecognizerDefaults.TAP_MAX_DIST,
            detectedHandler=self.__on_close_button_clicked
        )

    @property
    def map_point_view(self):
        """
        :rtype: MapPointView
        """
        return self.__map_point_view

    def set_border_color(self, color):
        """
        Sets the color of the border of the background.

        :param color: The new color for the border.
        :type color: avg.Color
        """
        self.__background_rect.color = color
        self.__triangle_rect.fillcolor = color

    def __on_tap(self):
        """
        Called when a tap on the detail view has happened.
        """
        self.__map_point_view.parent.reorderChild(self.__map_point_view, self.__map_point_view.parent.getNumChildren() - 1)
        self.parent.reorderChild(self, self.parent.getNumChildren() - 1)

    def __on_close_button_clicked(self):
        """
        Called when a tap on the close button has happened.
        """
        self.__map_point_view.show_detail_view(False)
        StudyLog.get_instance().write_event_log('A DoD was closed (by close button).')
