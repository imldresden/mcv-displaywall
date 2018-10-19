

COLOR_THEME = "green"


class VisDefaults(object):
    ITEM_COLOR = '007a99'
    if COLOR_THEME == "green":
        ITEM_COLOR = '006600'
    ITEM_OPACITY = 0.45
    ITEM_OPACITY_SELECTED = 1.0
    ITEM_OPACITY_HIGHLIGHTED = 0.5

    GRAPH_NODE_COLOR_FROM_TYPE = {
        "premise_name": ITEM_COLOR,
        "crime_type_name": ITEM_COLOR,
        "weapon_name": '00b8e6',
        "district_name": '00b8e6',
        "neighborhood_name": ITEM_COLOR
    }
    if COLOR_THEME == "green":
        GRAPH_NODE_COLOR_FROM_TYPE["weapon_name"] = '86b300'
        GRAPH_NODE_COLOR_FROM_TYPE["district_name"] = '86b300'

    EDGE_COLOR = 'aaa'
    LABEL_FONT_SIZE = 13
    DEFAULT_SELECTION_COLOR = 'ff8f00'
    DEFAULT_HIGHLIGHTED_COLOR = '003300'
    GRAPH_BACKGROUND_COLOR = 'f2f2f2'


if COLOR_THEME == "dark":
    # general
    BACKGROUND_COLOR = '000'
    # graph
    DEFAULT_NODE_COLOR = 'a6bddb'
    SELECTED_NODE_COLOR = 'ff72ca'
    DEFAULT_EDGE_COLOR = 'FCFCF4'
    NODE_LABEL_BACKGROUND = '000'
    # selection
    SELECTION_FEEDBACK_COLOR = 'fff'

else:  # "light"
    # general
    BACKGROUND_COLOR = 'FFFFFF'  # 'FCFCF4'
    # graph
    DEFAULT_NODE_COLOR = '587211'
    SELECTED_NODE_COLOR = 'ff8f00'
    DEFAULT_EDGE_COLOR = '404060'
    NODE_LABEL_BACKGROUND = '83ab10'
    # selection
    SELECTION_FEEDBACK_COLOR = '006600'


ADJACENCY_EDGE_COLOR = 'a7a8d4'
MIN_MAX_NODE_SIZE_IN_CM = (1.5, 9)
MIN_MAX_EDGE_WIDTH_IN_CM = (0.1, 2)
MIN_MAX_MAP_POINT_SIZE_IN_CM = (2, 15)
NODE_SIZE_ATTRIBUTE = "count"

# level of detail shown
# # attribute value belonging to the upper x percent (currently 0.8) are always shown
LOD_ATTRIBUTE = "count"  # ""edge_count"
LOD_SHOW_ALWAYS_ATTRIBUTE_VALUE = 0.15
LOD_MAXIMUM_ATTRIBUTE_DISTANCE = 70
LOD_TEXT_SIZE_UPDATE_DIVISOR = 40


# MAP
MAP_POINT_COLOR_ATTRIBUTE = {"name": 'energy_2000_MWh', "min": 0.0, "max": 10000000,
                             # "start_color": "ccddff", "end_color": "4d88ff"}
                            "start_color": "ffff99", "end_color": "ff9900"}
MAP_POINT_SIZE_ATTRIBUTE = {"name": 'count', "min": 100.0, "max": 4500.0}
MAP_POINT_ATTRIBUTE_KEYS = {
    "CO2 in kg": ('CO2_kg_2000', 'CO2_kg_2007', 'CO2_kg_2020'),
    "energy in MWh": ('energy_2000_MWh', 'energy_2007_MWh', 'energy_2020_MWh'),
    "intensity": ('intensity_2000', 'intensity_2007', 'intensity_2020')
}

CRIME_DESCRIPTION_COLOR = {
    'RAPE': 'b2182b',
    'SHOOTING': 'd6604d',
    'ARSON': 'f4a582',

    'AGG. ASSAULT': '762a83',
    'COMMON ASSAULT': '9970ab',
    'ASSAULT BY THREAT': 'c2a5cf',
    'BURGLARY': 'e7d4e8',

    'ROBBERY - COMMERCIAL': 'd9f0d3',
    'ROBBERY - RESIDENCE': 'a6dba0',
    'ROBBERY - STREET': '5aae61',
    'ROBBERY - CARJACKING': '1b7837',

    'AUTO THEFT': '2166ac',
    'LARCENY FROM AUTO': '4393c3',
    'LARCENY': '92c5de'
}

