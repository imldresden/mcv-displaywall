from libavg import avg, gesture

from configs.config_recognizer import CommonRecognizerDefaults
from configs.visual_data import VisDefaults as defaults
from data_models.data_enums import DataSelectionState
from logging_base.study_logging import StudyLog
from point_visuals.colored_circle_view import ColoredCircleView
from map_views.views.map_point_detail_view import MapPointDetailView


class MapPointView(avg.DivNode):

    def __init__(self, point_model, geo_coord_mapper, detail_parent=None, parent=None, **kwargs):
        """
        :param point_model: The point this view should represent.
        :type point_model: MapPoint
        :param scale_factor: The factor the point position should be scaled in the view.
        :type scale_factor: tuple
        :param parent: The parent node this point is embedded in.
        :type parent: DivNode
        """
        super(MapPointView, self).__init__(**kwargs)
        self.registerInstance(self, parent)
        self.subscribe(avg.Node.KILLED, self.__on_self_killed)

        self.__detail_parent = detail_parent or parent

        self.__label_rect_node = None
        self.__label_words_node = None
        self.__detail_view = None
        self.__detail_view_active = False

        self.__point_model = point_model
        self.__point_model.start_listening(
            level_of_detail_changed=self.__on_level_of_detail_changed,
            size_changed=self.__on_model_size_changed,
            visible_changed=self.__on_model_visible_changed,
            texture_changed=self.__on_model_texture_changed,
            opacity_val_changed=self.__on_model_opacity_changed,
            color_changed=self.__on_model_color_changed,
            selection_state_changed=self.__on_model_state_changed
        )
        self.__visual = ColoredCircleView(point_model=point_model, parent=self)
        if self.__point_model.texture is not None:
            self.__additional_texture_visual = avg.ImageNode(
                parent=self,
                href=self.__point_model.texture,
                size=(self.__point_model.width, self.__point_model.height),
                opacity=self.__point_model.color_opacity
            )
        else:
            self.__additional_texture_visual = None

        self.__geo_coord_mapper = geo_coord_mapper
        self.update_position(geo_coord_mapper)

        self.__was_tap_before = False
        self.__tap_recognizer = gesture.TapRecognizer(
            node=self,
            maxTime=CommonRecognizerDefaults.TAP_MAX_TIME,
            maxDist=CommonRecognizerDefaults.TAP_MAX_DIST,
            detectedHandler=self.__on_tap
        )
        self.__double_tap_recognizer = gesture.DoubletapRecognizer(
            node=self,
            maxTime=CommonRecognizerDefaults.DOUBLE_TAP_MAX_TIME,
            maxDist=CommonRecognizerDefaults.DOUBLE_TAP_MAX_DIST,
            failHandler=self.__on_double_tap_failed,
            detectedHandler=self.__on_double_tap
        )

    def __on_self_killed(self):
        """
        Called when this node itself was killed through unlink(True).
        """
        self.__point_model.stop_listening(
            level_of_detail_changed=self.__on_level_of_detail_changed,
            size_changed=self.__on_model_size_changed,
            visible_changed=self.__on_model_visible_changed,
            texture_changed=self.__on_model_texture_changed,
            opacity_val_changed=self.__on_model_opacity_changed,
            color_changed=self.__on_model_color_changed,
            selection_state_changed=self.__on_model_state_changed
        )

        if self.__label_words_node:
            self.__label_rect_node.unlink(True)
            self.__label_words_node.unlink(True)
        if self.__detail_view:
            self.__detail_view.unlink(True)

        self.__visual.unlink(True)
        if self.__additional_texture_visual:
            self.__additional_texture_visual.unlink(True)
        self.__tap_recognizer = None
        self.__double_tap_recognizer = None

    @property
    def point_model(self):
        """
        :rtype: MapPoint
        """
        return self.__point_model

    @property
    def pos_x(self):
        """
        :rtype: int
        """
        return self.pos[0]

    @property
    def pos_y(self):
        """
        :rtype: int
        """
        return self.pos[1]

    @property
    def detail_view(self):
        """
        :rtype: DivNode
        """
        return self.__detail_view

    @avg.DivNode.active.setter
    def active(self, value):
        avg.DivNode.active.fset(self, value)
        if self.__detail_view:
            self.__detail_view.active = value if not value else self.__detail_view_active

    def update_position(self, geo_coord_mapper):
        self.pos = geo_coord_mapper.get_map_pos_from_geo(self.__point_model.geo_coord)
        self.__point_model.pos_x = self.pos[0]
        self.__point_model.pos_y = self.pos[1]

    def update_scale(self, scale_factor):
        self.__visual.update_scale(scale_factor)
        self.__update_label(self.__label_words_node.active if self.__label_words_node else False)
        self.__update_detail_view(self.__detail_view.active if self.__detail_view else False)
        if self.__additional_texture_visual is not None and self.__visual is not None:
            self.__additional_texture_visual.pos = (-self.__visual.size[0]/2, -self.__visual.size[1]/2)
            self.__additional_texture_visual.size = self.__visual.size

    def __on_level_of_detail_changed(self, sender, level_of_detail):
        # self.__visual.change_level_of_detail(level_of_detail)
        if level_of_detail == 0:
            self.__update_label(True if self.__point_model.element_state is DataSelectionState.Selected else False)
            self.__update_detail_view(False)
        else:
            self.__update_label(True)
            self.__update_detail_view(True)

            self.parent.reorderChild(self, self.parent.getNumChildren() - 1)

    def __on_model_size_changed(self, sender, width, height):
        # here: size change; BUT: visual is not dependent on model size BUT on attribute value
        # size = avg.Point2D(width, height)
        # self.__visual.pos = size / -2
        # self.__visual.size = size
        # if self.__label_node is not None:
        #     self.update_label(
        #         show=self.__label_node.active, font_size=self.__label_node.fontsize, font_color=self.__label_node.color)
        self.__update_label(self.__label_words_node.active if self.__label_words_node else False)

    def __on_model_visible_changed(self, sender, visible):
        self.active = visible

    def __on_model_opacity_changed(self, sender, opacity_val):
        self.opacity = opacity_val

    def __on_model_texture_changed(self, sender, texture):
        if texture is None:
            if self.__additional_texture_visual is not None:
                self.__additional_texture_visual.active = False
            return

        # set texture href
        if self.__additional_texture_visual is None:
            self.__additional_texture_visual = avg.ImageNode(
                parent=self,
                pos=(-self.__visual.size[0]/2, -self.__visual.size[1]/2),
                size=self.__visual.size,
                opacity=self.__point_model.color_opacity
            )
        self.__additional_texture_visual.active=True
        self.__additional_texture_visual.href = texture

    def __on_model_color_changed(self, sender, color):
        self.__visual.color = color

    def __on_tap(self):
        """
        Called when a tap was recognized.
        """
        self.__was_tap_before = True

    def __on_double_tap(self, outer_call=False):
        """
        Called when double tap was recognized.

        :param outer_call: If this double tap was caused from an call outside this class.
        :type outer_call: bool
        """
        if not outer_call:
            StudyLog.get_instance().write_event_log('A DoD was {} (by double tap).'.format("opened" if self.__point_model.level_of_detail == 0 else "closed"))
        self.__point_model.level_of_detail = 1 if self.__point_model.level_of_detail == 0 else 0
        self.__was_tap_before = False

    def __on_double_tap_failed(self):
        """
        Called when a double tap has failed. It will act as a substitute for a normal tap.
        """
        if self.__was_tap_before:
            self.__point_model.element_state = DataSelectionState.Selected if self.__point_model.element_state is not DataSelectionState.Selected else DataSelectionState.Nothing
        self.__was_tap_before = False

    def __on_model_state_changed(self, sender, element_state, highlight_color=None):
        if element_state is DataSelectionState.Selected:
            if highlight_color is None:
                highlight_color = defaults.DEFAULT_SELECTION_COLOR
            self.__visual.set_visual_props(highlight_color, defaults.ITEM_OPACITY_SELECTED)
            self.__update_label(True, font_color=highlight_color)

            if self.__detail_view:
                self.__detail_view.set_border_color(highlight_color)
        elif element_state is DataSelectionState.Highlighted:
            if highlight_color is None:
                highlight_color = defaults.DEFAULT_HIGHLIGHTED_COLOR
            self.__visual.set_visual_props(highlight_color, defaults.ITEM_OPACITY_HIGHLIGHTED)
            self.__update_label(True, font_color=highlight_color)

            if self.__detail_view:
                self.__detail_view.set_border_color(highlight_color)
        else:
            self.__visual.set_visual_props(self.point_model.color, defaults.ITEM_OPACITY)
            self.__update_label(False if self.__point_model.level_of_detail == 0 else True)

            if self.__detail_view:
                self.__detail_view.set_border_color(self.__visual.color)

    def __update_label(self, show, font_size=defaults.LABEL_FONT_SIZE, font_color=None, offset_to_other_element=5):
        """
        Updates the label that is shown by this map point.

        :param show: Should the label be shown?
        :type show: bool
        :param font_size: Then size of the font for the label.
        :type font_size: float
        :param font_color: The color of the text.
        :type font_color: avg.Color
        :param offset_to_other_element: The offset between the map point and the label.
        :type offset_to_other_element: float
        """
        # init node
        if not self.__label_words_node and show:
            self.__label_rect_node = avg.RectNode(
                parent=self,
                strokewidth=0,
                fillopacity=0.75,
                fillcolor="fff"
            )
            text = self.__point_model.data_object_id
            if "count" in self.__point_model.attribute_dict:
                text += " ({})".format(self.__point_model.attribute_dict["count"])
            self.__label_words_node = avg.WordsNode(
                parent=self,
                text=text,
                alignment="center",
                rawtextmode=True
            )

        if self.__label_words_node:
            self.__label_words_node.active = show
            self.__label_words_node.fontsize = font_size
            self.__label_words_node.color = font_color or self.__visual.color
            self.__label_words_node.pos = 0, offset_to_other_element + self.__visual.size.y / 2

            self.__label_rect_node.active = show
            self.__label_rect_node.size = self.__label_words_node.size[0] * 1.1, self.__label_words_node.size[1] * 1.1
            self.__label_rect_node.pos = (self.__label_words_node.pos[0] - self.__label_rect_node.size[0] / 2,
                                          self.__label_words_node.pos[1])

    def show_detail_view(self, show):
        """
        Shows or hides the detail view for this map point view.

        :param show: Should the detail view be shown?
        :type show: bool
        """
        if self.__point_model.level_of_detail == 0 and show or self.__point_model.level_of_detail == 1 and not show:
            self.__on_double_tap(outer_call=True)

    def __update_detail_view(self, show, offset=10):
        """
        Updates the label that is shown by this map point.

        :param show: Should the label be shown?
        :type show: bool
        :param offset: The offset between the map point and the label.
        :type offset: float
        """
        # Only allow a update of the detail view if the map point itself is shown.
        if not self.active:
            return

        if not self.__detail_view and show:
            self.__detail_view = MapPointDetailView(
                parent=self.__detail_parent,
                map_point_view=self
            )

        if self.__detail_view:
            self.__detail_view_active = show
            self.__detail_view.active = show
            self.__detail_view.set_border_color(self.__visual.color)
            self.__detail_view.pos = (self.pos[0] - self.__detail_view.size[0] / 2,
                                      self.pos[1] - self.__visual.size.y / 2 - self.__detail_view.size[1] - offset)
            if show:
                self.__detail_view.parent.reorderChild(self.__detail_view, self.__detail_view.parent.getNumChildren() - 1)
