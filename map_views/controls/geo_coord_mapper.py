from math import pi, log, tan, e
from pyproj import Proj, transform


class GeoCoordMapper(object):
    # Projection that will be used
    __proj_data = Proj("+init=EPSG:4326")
    __proj_merc = Proj("+init=EPSG:3857")
    __proj_equi = Proj(proj="eqc")

    def __init__(self):
        self.__map_coord_offset = (0, 0)
        self.__map_scale_factor = 1.0

        # from worldLow_mercator  # best would be calculating these values from map geo coord (see svg)
        #  - but errors occur because of high values (190), so these are approximations (using web maps)
        # these are set by map view according to (svg) image in the background
        self.__background_image_original_properties = {
            "dimensions": (946, 641),
            "min_mercator": (-19000000.0, 18750960.304313),
            "max_mercator": (18900000.0, -7374732.600016)
        }

    def set_map_coord_offset(self, offset):
        """
        Sets the offset of the mapper.

        :param offset: The offset of the mapper.
        :type offset: tuple
        """
        self.__map_coord_offset = offset

    def set_background_image_original_properties(self, value_dict):
        """
        :param value_dict:
        :type value_dict: dict
        """
        self.__background_image_original_properties = value_dict

    def set_map_scale_factor(self, factor):
        """
        Sets the scale of the mapper.

        :param factor: The scale of the mapper.
        :type factor: float
        """
        self.__map_scale_factor = factor

    @staticmethod
    def get_mercator_from_geo(geo_coord):
        return transform(GeoCoordMapper.__proj_data, GeoCoordMapper.__proj_merc, geo_coord[0], geo_coord[1])

    def get_map_pos_from_geo(self, geo_coord):
        max_mercator = self.__background_image_original_properties["max_mercator"]
        min_mercator = self.__background_image_original_properties["min_mercator"]
        img_size = self.__background_image_original_properties["dimensions"]

        x, y = transform(GeoCoordMapper.__proj_data, GeoCoordMapper.__proj_merc, geo_coord[0], geo_coord[1])

        # dimensions are used from underlying image
        scale_to_image_x = img_size[0] / (max_mercator[0] - min_mercator[0])
        scale_to_image_y = img_size[1] / (max_mercator[1] - min_mercator[1])

        x = (x - min_mercator[0]) * scale_to_image_x
        y = (y - min_mercator[1]) * scale_to_image_y

        x *= self.__map_scale_factor
        y *= self.__map_scale_factor

        x += self.__map_coord_offset[0]
        y += self.__map_coord_offset[1]

        # print "coordinates: ", x, y

        return x, y

    def geo_coord_to_map_coord_equi(self, geo_coord, img_size):
        """
        Transforms the geographic coordinates (longitude and latitude) in map coordinates (x and y)
        to use them in this application.
        It is used with equidistant cylindrical projection type maps.

        :param geo_coord: The geographical coordinates (longitude and latitude).
        :type geo_coord: float, float
        :param img_size: The size of the image this coordinates should be lying on.
        :type img_size: int, int
        :return: The coordinates of the geographical coordinates for this map.
        :rtype: int, int
        """
        # x = img_size[0] * (180.0 + geo_coord[0]) / 360
        # y = img_size[1] * (90.0 - geo_coord[1]) / 180
        # # Return x and y and apply offset to it
        # return x - GeoCoordMapper.__map_coord_offset[0], y - GeoCoordMapper.__map_coord_offset[1]
