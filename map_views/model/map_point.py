from map_views.data_point import DataPoint
from libavg.avg import Color
from configs.visual_data import VisDefaults as defaults


class MapPoint(DataPoint):

    def __init__(self, latitude, longitude, name="", color=defaults.ITEM_COLOR, color_opacity=defaults.ITEM_OPACITY, country_code=-1, **kwargs):
        super(MapPoint, self).__init__(**kwargs)
        """
        :param data_object: The data object for this point.
        """
        self.__name = name if name != "" else self.data_object_id
        self.__color = color
        self.__color_opacity = color_opacity
        self.__latitude = latitude
        self.__longitude = longitude
        self.__country_code = country_code
        self.__texture = None

        self.__callbacks_coord_changed = []
        self.__callbacks_color_changed = []
        self.__callbacks_texture_changed = []

    @property
    def latitude(self):
        """
        :rtype: float
        """
        return self.__latitude

    @property
    def longitude(self):
        """
        :rtype: float
        """
        return self.__longitude

    @property
    def geo_coord(self):
        """
        :rtype: tuple[float, float]
        """
        return self.longitude, self.latitude

    @property
    def name(self):
        """
        :rtype: str
        """
        return self.__name

    @property
    def country_code(self):
        """
        :rtype: str
        """
        return self.__country_code

    @property
    def color(self):
        """
        :rtype: Color
        """
        return self.__color

    @color.setter
    def color(self, value):
        """
        :rtype: Color
        """
        self.__color = value
        for callback in self.__callbacks_color_changed:
            callback(sender=self, color=value)

    @property
    def color_opacity(self):
        return self.__color_opacity

    @property
    def texture(self):
        return self.__texture

    @texture.setter
    def texture(self, texture):
        self.__texture = texture
        for callback in self.__callbacks_texture_changed:
            callback(sender=self, texture=self.__texture)

    def start_listening(self, pos_changed=None, size_changed=None, selection_state_changed=None, visible_changed=None,
                        opacity_val_changed=None, color_changed=None, texture_changed=None,
                        level_of_detail_changed=None, coord_changed=None):
        super(MapPoint, self).start_listening(
            pos_changed=pos_changed,
            size_changed=size_changed,
            visible_changed=visible_changed,
            opacity_val_changed=opacity_val_changed,
            element_state_changed=selection_state_changed,
            level_of_detail_changed=level_of_detail_changed
        )
        events = [
            (coord_changed, self.__callbacks_coord_changed),
            (color_changed, self.__callbacks_color_changed),
            (texture_changed, self.__callbacks_texture_changed)
        ]
        for callback, call_list in events:
            if callback is not None and callback not in call_list:
                call_list.append(callback)

    def stop_listening(self, pos_changed=None, size_changed=None, selection_state_changed=None, visible_changed=None,
                       opacity_val_changed=None, color_changed=None, texture_changed=None,
                       level_of_detail_changed=None, coord_changed=None):
        super(MapPoint, self).stop_listening(
            pos_changed=pos_changed,
            size_changed=size_changed,
            visible_changed=visible_changed,
            opacity_val_changed=opacity_val_changed,
            element_state_changed=selection_state_changed,
            level_of_detail_changed=level_of_detail_changed
        )
        events = [
            (coord_changed, self.__callbacks_coord_changed),
            (color_changed, self.__callbacks_color_changed),
            (texture_changed, self.__callbacks_texture_changed)
        ]
        for callback, call_list in events:
            if callback is not None:
                call_list.remove(callback)
