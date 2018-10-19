from data_models.csv_provider.data_provider import get_data_from_csv_file
from map_views.model.map import Map
from map_views.model.map_point import MapPoint


def create_map_from_file(filename, separation_key, country_list=None, with_settings=True):
    """
    Creates from a csv file (data for the map), a txt file (settings for the map) a map object for this application.

    :param filename: The data for this map. This should be a *.csv file.
    :type filename: str
    :param separation_key: The key that will separate the data.
    :type separation_key: str
    :param search_key_values: Specific values in the key.
    :type search_key_values: list[object]
    :param with_settings: Should a setting file with the same name and the extension .setting be used?
    :type with_settings: bool
    :return: The created map.
    :rtype: MapModel
    """
    value_ranges, data = get_data_from_csv_file(filename=filename, with_settings=with_settings)
    new_map = Map()

    if len(data) < 1:
        return

    key_lat = "latitude"
    key_long = "longitude"
    for key in data[0].keys():
        if key.lower() == "lat" or key.lower() == "latitude":
            key_lat = key
        elif key.lower() == "long" or key.lower() == "longitude":
            key_long = key

    # create map Points
    for data_point in data:
        if separation_key in data_point and key_lat in data_point and key_long in data_point:
            key = data_point[separation_key]
            lat = data_point[key_lat]
            long = data_point[key_long]
            country_code = data_point["country_code"] if "country_code" in data_point else -1
            if country_list is None or country_code in country_list:
                new_map.add_point(
                    MapPoint(
                        name=key, latitude=lat, longitude=long, country_code=country_code, data_objects=data_point)
                )
    return new_map


def create_map_from_data(data_object_list):
    if len(data_object_list) < 1:
        return

    new_map = Map()
    key_lat = "latitude"
    key_long = "longitude"
    for key in data_object_list[0].keys():
        if key.lower() == "lat" or key.lower() == "latitude":
            key_lat = key
        elif key.lower() == "long" or key.lower() == "lng" or key.lower() == "longitude":
            key_long = key

    for data_object in data_object_list:
        country_code = data_object["country_code"] if "country_code" in data_object else -1
        attributes = data_object["attributes"] if "attributes" in data_object else {}

        # if one of the lat or long values are inf, ignore this item
        if data_object[key_lat] == float('-inf') or data_object[key_long] == float('-inf'):
            continue

        new_map.add_point(
            MapPoint(
                data_object_id=data_object["obj_id"],
                latitude=data_object[key_lat],
                longitude=data_object[key_long],
                country_code=country_code,
                attribute_dict=attributes
            )
        )
    return new_map


def get_data_from_file(filename, separation_key, search_key_values=None, with_settings=True):
    """
    Creates a new dict from the given files.

    :param filename: The file for the data. It should be a .csv file.
    :type filename: str
    :param separation_key: The key that will separate the data.
    :type separation_key: str
    :param search_key_values: Specific values in the key.
    :type search_key_values: list[object]
    :param with_settings: Should a setting file with the same name and the extension .setting be used?
    :type with_settings: bool
    :return: New dict of data generate from the given file
    :rtype: dict
    """
    keys, data_objects = get_data_from_csv_file(filename=filename, with_settings=with_settings)
    # return generate_data_object_from_key_and_data(separation_key=separation_key, search_key_values=search_key_values, orig_data=data_objects)
    return []
