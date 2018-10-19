from libavg import avg, gesture

from configs import config_app
from map_views.controls.geo_coord_mapper import GeoCoordMapper


class ImageMapProvider(object):
    def __init__(self, filename, img_dimensions, min_geo, max_geo):

        self.__filename = filename
        min_mercator = GeoCoordMapper.get_mercator_from_geo(min_geo)
        max_mercator = GeoCoordMapper.get_mercator_from_geo(max_geo)

        self.__image_values = {
            "dimensions": img_dimensions,
            "min_geo": min_geo,
            "max_geo": max_geo,
            "min_mercator": min_mercator,
            "max_mercator": max_mercator
        }
        self.__map_image = None
        self.__recognizer = None
        self.__current_scale_factor = 1.0
        self.__current_offset = (0.0, 0.0)

        self.__callback_image_moved = []

    @property
    def current_offset(self):
        """
        :rtype: tuple[float, float]
        """
        return self.__current_offset

    @property
    def current_scale_factor(self):
        """
        :rtype: float
        """
        return self.__current_scale_factor

    def get_image_values(self):
        return self.__image_values

    def place_image(self, parent, size):
        self.__map_image = avg.ImageNode(
            parent=parent,
            href=self.__filename
        )
        if self.__map_image.size != size:
            factor_x = size[0] / self.__map_image.size[0]
            factor_y = size[1] / self.__map_image.size[1]
            self.__current_scale_factor = factor_x if factor_x > factor_y else factor_y
            self.__map_image.size *= self.__current_scale_factor
            self.__current_offset = (avg.Point2D(size)-self.__map_image.size)/2
            self.__map_image.pos = self.__current_offset

    def resize(self, size):
        if self.__map_image is None:
            return
        scale_factor = (size[0]/self.__map_image.size[0], size[1]/self.__map_image.size[1])
        transform_scale = scale_factor[0] if scale_factor[0] > scale_factor[1] else scale_factor[1]
        self.__scale(transform_scale)
        self.__map_image.pos = self.__current_offset

        for callback in self.__callback_image_moved:
            callback(sender=self, offset=self.__current_offset, scale_factor=self.__current_scale_factor)

    def transform(self, scale, translation, pivot):
        """
        Transforms (zoom and pan) the image.

        :param scale: The scale that should be used.
        :type scale: float
        :param translation: The translation that should be applied.
        :type translation: tuple[float, float]
        :param pivot: The pivot point of the transform.
        :type pivot: tuple[float, float]
        """
        self.__on_transform(gesture.Transform(trans=translation, scale=scale, pivot=pivot))

    def __on_transform(self, transform):
        # translate by panning
        self.__current_offset = (self.__current_offset[0] + transform.trans.x, self.__current_offset[1] + transform.trans.y)
        # scale
        if transform.scale != 1.0:
            old_scale_factor = self.__current_scale_factor
            self.__scale(transform.scale)
            # move by pivot offset incl. scale
            if old_scale_factor != self.__current_scale_factor:
                self.__current_offset = (self.__current_offset[0] - (transform.pivot.x * self.__current_scale_factor / old_scale_factor) + transform.pivot.x,
                                         self.__current_offset[1] - (transform.pivot.y * self.__current_scale_factor / old_scale_factor) + transform.pivot.y)

        self.__map_image.pos = self.__current_offset

        for callback in self.__callback_image_moved:
            callback(sender=self, offset=self.__current_offset, scale_factor=self.__current_scale_factor)

    def __scale(self, transform_scale):
        if transform_scale == 1.0:
            return

        old_scale_factor = self.__current_scale_factor
        self.__current_scale_factor *= transform_scale
        if self.__current_scale_factor < config_app.min_map_scale_factor:
            self.__current_scale_factor = config_app.min_map_scale_factor
        elif self.__current_scale_factor > config_app.max_map_scale_factor:
            self.__current_scale_factor = config_app.max_map_scale_factor

        self.__map_image.size *= self.__current_scale_factor / old_scale_factor

        # scale original offset
        self.__current_offset = (self.__current_offset[0] * self.__current_scale_factor / old_scale_factor,
                                 self.__current_offset[1] * self.__current_scale_factor / old_scale_factor)

    def start_listening(self, image_moved):
        if image_moved is not None and image_moved not in self.__callback_image_moved:
            self.__callback_image_moved.append(image_moved)

    def stop_listening(self, image_moved):
        if image_moved is not None:
            self.__callback_image_moved.remove(image_moved)
