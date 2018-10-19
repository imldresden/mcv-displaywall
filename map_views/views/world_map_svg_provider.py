from libavg import avg
from enum import Enum


class WorldType(Enum):
    Low = 0,
    High = 1


class WorldMapProvider(object):
    __country_ids_europe = ["AL", "AD", "AT", "BA", "BE", "BG", "BY", "CH", "CY", "CZ", "DE", "DK", "EE", "ES", "FI",
                            "FO", "FR", "GB", "GI", "GR", "HR", "HU", "IE", "IM", "IS", "IT", "LI", "LT", "LU", "LV",
                            "MC", "MD", "ME", "MK", "MT", "RS", "NL", "NO", "PL", "PT", "RE", "RO", "RM", "RS", "RU",
                            "SE", "SI", "SK", "UA", "VA", "XK"]

    def __init__(self, world_type):
        self.__map_svg = None
        self.__country_ids = []
        self.__image_values = {}
        # left, top, right, bottom
        self.__current_offset = (0, 0)
        self.__current_scale_factor = 1.0
        self.__map_ratio = 1
        self.__world_type = world_type
        self.__load_svg(world_type=world_type)

    @property
    def country_ids(self):
        """
        :rtype: list[str]
        """
        return self.__country_ids

    @property
    def world_type(self):
        """
        :rtype: WorldType
        """
        return self.__world_type

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

    @staticmethod
    def get_country_ids_europe():
        """
        :return: Returns all country codes for countries in europe.
        :rtype: list[str]
        """
        return WorldMapProvider.__country_ids_europe

    def get_image_values(self):
        """
        :return: Returns the dimensions, min_mercator and max_mercator as well of currently used image
        :rtype: dict
        """
        return self.__image_values

    def __load_svg(self, world_type):
        """
        Loads the world map as a svg this class should provide.

        :param world_type: The type of the map that should be loaded.
        :type world_type: WorldType
        """
        if world_type is WorldType.Low:
            self.__map_svg = avg.SVG("assets/map_files/worldLow_mercator.svg", True)
            self.__country_ids = ["AE", "AF", "AL", "AM", "AO", "AR", "AT", "AU", "AZ", "BA", "BD", "BE", "BF", "BG",
                                  "BI", "BJ", "BN", "BO", "BR", "BS", "BT", "BW", "BY", "BZ", "CA", "CD", "CF", "CG",
                                  "CH", "CI", "CL", "CM", "CN", "CO", "CR", "CU", "CY", "CZ", "DE", "DJ", "DK", "DO",
                                  "DZ", "EC", "EE", "EG", "EH", "ER", "ES", "ET", "FK", "FI", "FJ", "FR", "GA", "GB",
                                  "GE", "GF", "GH", "GL", "GM", "GN", "GQ", "GR", "GT", "GW", "GY", "HN", "HR", "HT",
                                  "HU", "ID", "IE", "IL", "IN", "IQ", "IR", "IS", "IT", "JM", "JO", "JP", "KE", "KG",
                                  "KH", "KP", "KR", "XK", "KW", "KZ", "LA", "LB", "LK", "LR", "LS", "LT", "LU", "LV",
                                  "LY", "MA", "MD", "ME", "MG", "MK", "ML", "MM", "MN", "MR", "MW", "MX", "MY", "MZ",
                                  "NA", "NC", "NE", "NG", "NI", "NL", "NO", "NP", "NZ", "OM", "PA", "PE", "PG", "PH",
                                  "PL", "PK", "PR", "PS", "PT", "PY", "QA", "RO", "RS", "RU", "RW", "SA", "SB", "SD",
                                  "SE", "SI", "SJ", "SK", "SL", "SN", "SO", "SR", "SS", "SV", "SY", "SZ", "TD", "TF",
                                  "TG", "TH", "TJ", "TL", "TM", "TN", "TR", "TT", "TW", "TZ", "UA", "UG", "US", "UY",
                                  "UZ", "VE", "VN", "VU", "XK", "YE", "ZA", "ZM", "ZW"]
            self.__map_border_geo_coord = (-169.6, 83.68, 190.25, -55.55)
            self.__map_ratio = 2.53
            self.__image_values = {
                "dimensions": (946, 641),
                "min_geo": (-169.6, 83.68),
                "max_geo": (190.25, -55.55),
                "min_mercator": (-19000000.0, 18750960.304313),
                "max_mercator": (18900000.0, -7374732.600016)
            }
        else:
            self.__map_svg = avg.SVG("assets/map_files/worldHigh_mercator.svg", True)
            self.__country_ids = ["AD", "AE", "AF", "AG", "AI", "AL", "AM", "AO", "AR", "AS", "AT", "AU", "AW", "AX",
                                  "AZ", "BA", "BB", "BD", "BE", "BF", "BG", "BH", "BI", "BJ", "BL", "BN", "BO", "BM",
                                  "BQ", "BR", "BS", "BT", "BV", "BW", "BY", "BZ", "CA", "CC", "CD", "CF", "CG", "CH",
                                  "CI", "CK", "CL", "CM", "CN", "CO", "CR", "CU", "CV", "CW", "CX", "CY", "CZ", "DE",
                                  "DJ", "DK", "DM", "DO", "DZ", "EC", "EG", "EE", "EH", "ER", "ES", "ET", "FI", "FJ",
                                  "FK", "FM", "FO", "FR", "GA", "GB", "GE", "GD", "GF", "GG", "GH", "GI", "GL", "GM",
                                  "GN", "GO", "GP", "GQ", "GR", "GS", "GT", "GU", "GW", "GY", "HK", "HM", "HN", "HR",
                                  "HT", "HU", "ID", "IE", "IL", "IM", "IN", "IO", "IQ", "IR", "IS", "IT", "JE", "JM",
                                  "JO", "JP", "JU", "KE", "KG", "KH", "KI", "KM", "KN", "KP", "KR", "XK", "KW", "KY",
                                  "KZ", "LA", "LB", "LC", "LI", "LK", "LR", "LS", "LT", "LU", "LV", "LY", "MA", "MC",
                                  "MD", "MG", "ME", "MF", "MH", "MK", "ML", "MO", "MM", "MN", "MP", "MQ", "MR", "MS",
                                  "MT", "MU", "MV", "MW", "MX", "MY", "MZ", "NA", "NC", "NE", "NF", "NG", "NI", "NL",
                                  "NO", "NP", "NR", "NU", "NZ", "OM", "PA", "PE", "PF", "PG", "PH", "PK", "PL", "PM",
                                  "PN", "PR", "PS", "PT", "PW", "PY", "QA", "RE", "RO", "RS", "RU", "RW", "SA", "SB",
                                  "SC", "SD", "SE", "SG", "SH", "SI", "SJ", "SK", "SL", "SM", "SN", "SO", "SR", "SS",
                                  "ST", "SV", "SX", "SY", "SZ", "TC", "TD", "TF", "TG", "TH", "TJ", "TK", "TL", "TM",
                                  "TN", "TO", "TR", "TT", "TV", "TW", "TZ", "UA", "UG", "UM-DQ", "UM-FQ", "UM-HQ",
                                  "UM-JQ", "UM-MQ", "UM-WQ", "US", "UY", "UZ", "VA", "VC", "VE", "VG", "VI", "VN",
                                  "VU", "WF", "WS", "XK", "YE", "YT", "ZA", "ZM", "ZW"]
            self.__map_border_geo_coord = (-169.110266, 83.63001, 190.480712, -58.488473)
            self.__map_border_map_coord = (1, 0, 1011, 665)
            self.__map_ratio = 2.4277252
            # ToDo update size and mercator values according to HIGH (currently these are copied from LOW)
            self.__image_values = {
                "dimensions": (946, 641),
                "min_geo": (-169.110266, 83.63001),
                "max_geo": (190.480712, -58.488473),
                "min_mercator": (-19000000.0, 18750960.304313),
                "max_mercator": (18900000.0, -7574732.600016)
            }

            print "map svg loaded"

    def get_country_image(self, country_id, scale=1):
        """
        Get an image of a given country id. If the country id isn't available it will return null.

        :param country_id: The id for the country.
        :type country_id: str
        :param scale: The scale the image should be created with.
        :type scale: int
        :return: The image of the the wanted country. None if no image is available.
        :rtype: ImageNode
        """
        if country_id not in self.__country_ids:
            return None

        country_image = self.__map_svg.createImageNode(country_id, {}, scale)
        country_image.pos = self.__map_svg.getElementPos(country_id)
        country_image.size = self.__map_svg.getElementSize(country_id)
        return country_image

    def get_country_images(self, country_ids, scale=1):
        """
        Get all images of countries for the given ids. An image is none if the ids isn't available.

        :param country_ids: The ids for the countries.
        :type country_ids: list
        :param scale: The scale the images should be created with.
        :type scale: int
        :return: The images of the the wanted country. Is an image not available it will be none.
        :rtype: dict
        """
        country_images = {}
        for country_id in country_ids:
            country_images[country_id] = self.get_country_image(country_id=country_id, scale=scale)

        return country_images

    def place_scaled_country_images(self, country_list, parent, size):
        print "started loading individual countries"
        min_x = None
        min_y = None
        width = 0
        height = 0
        images = []

        for country_id in country_list:
            country_image = self.get_country_image(country_id=country_id, scale=1)
            if country_image is None:
                print "could not find country image for id:", country_id
                continue
            images.append(country_image)
            if min_x is None:
                min_x = country_image.x
                min_y = country_image.y
                width = country_image.size[0]
                height = country_image.size[1]
            else:
                min_x = min(min_x, country_image.x)
                min_y = min(min_y, country_image.y)
                width = max(width, country_image.x - min_x + country_image.size[0])
                height = max(height, country_image.y - min_y + country_image.size[1])

        self.__current_offset = (-min_x, -min_y)
        self.__current_scale_factor = size[0] / width if (size[0]/width < size[1]/height) else size[1]/height

        for image in images:
            image.x -= min_x
            image.y -= min_y
            image.x *= self.__current_scale_factor
            image.y *= self.__current_scale_factor
            image.size *= self.__current_scale_factor
            parent.appendChild(image)
