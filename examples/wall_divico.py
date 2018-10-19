import pickle

import time

from data_models.data_desciption import DataDescription
from data_models.data_object import DataObject
from divico_ctrl.divico_control import DivicoControl
from libavg_charts.aid_lines.aid_line_enums import AidLineType
from libavg_charts.axis.chart_axis_enums import *
from libavg_charts.charts.bar_chart import BarChart
from libavg_charts.charts.line_chart import LineChart
from libavg_charts.charts.scatter_plot import ScatterPlot
from libavg_charts.configurations.chart_axis_configuration import ChartAxisConfiguration
from libavg_charts.configurations.chart_configuration import ChartConfiguration
from libavg_charts.configurations.intersection_configuration import IntersectionConfiguration
from libavg_charts.configurations.text_label_configuration import TextMarkingConfiguration
from multi_view_ctrl.example_multi_div_nodes import ExampleMultiDivNode3
from map_views.map_vis_view import MapImageInfo, GeoCoord, MapVisView
from utils import colors


class WallDivico(object):
    def __init__(self, parent, size, map_image_info,
                 data_file, grid_groups, grid_labels):
        """        
        :param parent: The parent the divico-app for the wall is integrated in.
        :type parent: DivNode
        :param size: The size of the app.
        :type size: tuple[float, float]
        :param map_image_info: All infos for the map.
        :type map_image_info: dict[str, ]
        :param data_file: The path to the results, that are used to create this view.
        :type data_file: str
        :param grid_groups: A list of all groups (also lists) of grid elements that should be added to this.
        :type grid_groups: list[list[int]]
        :param grid_labels: All labels for all the grids.
        :type grid_labels: dict[int, str]
        """
        self.__parent = parent
        self.__map_image_info = map_image_info
        self.__grid_groups = grid_groups
        self.__grid_labels = grid_labels

        with open(data_file, 'rb') as f:
            self.__input_data = pickle.load(f)

        self.__divico_control = None
        self.__multi_div_node = ExampleMultiDivNode3(
            parent=self.__parent,
            size=size,
            background_color=colors.BLUE_GREY_LIGHTEN_4
        )

        self.draw()
        self.__divico_control.start_server()

    @property
    def divico_control(self):
        return self.__divico_control

    @property
    def multi_div_node(self):
        return self.__multi_div_node
        
    def draw(self):
        charts = {}
        # Go through all groups.
        for grid_group in self.__grid_groups:
            data_values, data_schemes = {}, {}
            # Get all data values in this group.
            for grid_id in grid_group:
                data_values[grid_id], data_schemes[grid_id] = self.__input_data[str(grid_id)]

            desc_data_values = []
            if len(data_values) > 1:
                # Combine the data values to ensure that all axis have the same scale.
                for values in data_values.itervalues():
                    desc_data_values.extend(values)

            for grid_id in grid_group:
                data_objects = DataObject.generate_from_sql_results(data_values[grid_id], data_schemes[grid_id])

                if 0 <= grid_id <= 3:
                    data_desc_y = DataDescription.generate_from_data_objects(data_objects, "crime_type_name")
                    data_desc_x = DataDescription.generate_from_values_and_scheme(data_values.values(), data_schemes.values(), "crimes_count", values_to_add=[0])

                    charts[grid_id] = BarChart(
                        data=data_objects,
                        data_keys_for_selection=["crime_type_name"],
                        orientation=Orientation.Horizontal,
                        label=self.__grid_labels[grid_id],
                        bar_width=23,
                        x_axis_data=data_desc_x,
                        x_axis_config=ChartAxisConfiguration(data_steps=5, bottom_offset=0, show_grid_line=GridLines.Markings),
                        y_axis_data=data_desc_y,
                        y_axis_config=ChartAxisConfiguration(show_label=False, bottom_offset=20, top_offset=20, marking_steps=1 if grid_id == 33 else 0),
                        chart_config=ChartConfiguration(padding_left=140 if grid_id == 33 else 25),
                        selection_label_text_config=TextMarkingConfiguration(offset_to_other_element=3)
                    )
                elif 4 <= grid_id <= 10:
                    data_desc_x = DataDescription.generate_from_values_and_scheme(data_values.values(), data_schemes.values(), "crimes_count")
                    data_desc_x.data = [0, data_desc_x.data[1]]
                    data_desc_y = DataDescription.generate_from_data_objects(data_objects, "district_name")
                    charts[grid_id] = BarChart(
                        data=data_objects,
                        data_keys_for_selection=["district_name"],
                        label=self.__grid_labels[grid_id],
                        bar_width=15,
                        orientation=Orientation.Horizontal,
                        x_axis_data=data_desc_x,
                        x_axis_config=ChartAxisConfiguration(data_steps=5, bottom_offset=0, show_grid_line=GridLines.Markings),
                        y_axis_data=data_desc_y,
                        y_axis_config=ChartAxisConfiguration(show_label=False, bottom_offset=15),
                        chart_config=ChartConfiguration(padding_left=30),
                        selection_label_text_config=TextMarkingConfiguration(offset_to_other_element=3)
                    )
                elif grid_id == 11:
                    data_objects = DataObject.combine_at(data_objects, "neighborhood_name")
                    data_desc_x = DataDescription.generate_from_data_objects(data_objects, "month")
                    data_desc_y = DataDescription.generate_from_data_objects(data_objects, "crimes_count")
                    charts[grid_id] = LineChart(
                        data=data_objects,
                        data_keys_for_selection=["neighborhood_name"],
                        label=self.__grid_labels[grid_id],
                        x_axis_data=data_desc_x,
                        x_axis_config=ChartAxisConfiguration(data_steps=12, show_grid_line=GridLines.Markings),
                        y_axis_data=data_desc_y,
                        y_axis_config=ChartAxisConfiguration(show_grid_line=GridLines.Markings),
                        chart_config=ChartConfiguration(),
                        selection_label_text_config=TextMarkingConfiguration(offset_to_other_element=3)
                    )
                elif grid_id == 12:
                    data_desc_x = DataDescription.generate_from_data_objects(data_objects, "district_name")
                    data_desc_y = DataDescription.generate_from_data_objects(data_objects, "crime_type_name")
                    charts[grid_id] = ScatterPlot(
                        data=data_objects,
                        data_keys_for_selection=["district_name", "crime_type_name"],
                        label=self.__grid_labels[grid_id],
                        size_key="crimes_count",
                        selection_key="crimes_count",
                        x_axis_data=data_desc_x,
                        x_axis_config=ChartAxisConfiguration(show_label=False),
                        y_axis_data=data_desc_y,
                        y_axis_config=ChartAxisConfiguration(show_label=False, bottom_offset=15),
                        chart_config=ChartConfiguration(padding_left=150, padding_right=35),
                        selection_label_text_config=TextMarkingConfiguration(offset_to_other_element=3)
                    )
                elif grid_id == 13:
                    data_objects = DataObject.combine_at(data_objects, "weapon_name")
                    data_desc_x = DataDescription.generate_from_data_objects(data_objects, "hour")
                    data_desc_y = DataDescription.generate_from_data_objects(data_objects, "crimes_count")
                    charts[grid_id] = LineChart(
                        data=data_objects,
                        data_keys_for_selection=["weapon_name"],
                        label=self.__grid_labels[grid_id],
                        x_axis_data=data_desc_x,
                        x_axis_config=ChartAxisConfiguration(data_steps=24, show_grid_line=GridLines.Markings),
                        y_axis_data=data_desc_y,
                        y_axis_config=ChartAxisConfiguration(data_steps=5, show_grid_line=GridLines.Markings),
                        chart_config=ChartConfiguration(padding_right=50),
                        selection_label_text_config=TextMarkingConfiguration(offset_to_other_element=3)
                    )
                elif grid_id == 16:
                    data_desc_x = DataDescription.generate_from_data_objects(data_objects, "premise_name")
                    data_desc_y = DataDescription.generate_from_data_objects(data_objects, "crimes_count")
                    data_desc_y.data = [0, data_desc_y.data[1]]
                    charts[grid_id] = BarChart(
                        data=data_objects,
                        data_keys_for_selection=["premise_name"],
                        label=self.__grid_labels[grid_id],
                        bar_spacing=3,
                        x_axis_data=data_desc_x,
                        x_axis_config=ChartAxisConfiguration(show_label=False, top_offset=20, marking_orientation=Orientation.Vertical),
                        y_axis_data=data_desc_y,
                        y_axis_config=ChartAxisConfiguration(data_steps=5, bottom_offset=0, show_grid_line=GridLines.Markings),
                        chart_config=ChartConfiguration(padding_bottom=120, padding_right=20),
                        selection_label_text_config=TextMarkingConfiguration(offset_to_other_element=3)
                    )
                elif grid_id == 17:
                    data_objects = DataObject.combine_at(data_objects, "weapon_name")
                    data_desc_x = DataDescription.generate_from_data_objects(data_objects, "weekday")
                    data_desc_y = DataDescription.generate_from_data_objects(data_objects, "crimes_count")
                    charts[grid_id] = LineChart(
                        data=data_objects,
                        data_keys_for_selection=["weapon_name"],
                        label=self.__grid_labels[grid_id],
                        x_axis_data=data_desc_x,
                        x_axis_config=ChartAxisConfiguration(show_label=False, show_grid_line=GridLines.Markings),
                        y_axis_data=data_desc_y,
                        y_axis_config=ChartAxisConfiguration(data_steps=5, show_grid_line=GridLines.Markings),
                        chart_config=ChartConfiguration(padding_right=20),
                        selection_label_text_config=TextMarkingConfiguration(offset_to_other_element=3)
                    )
                elif grid_id == 22:
                    data_objects = DataObject.combine_at(data_objects, "crime_type_name")
                    data_desc_x = DataDescription.generate_from_data_objects(data_objects, "datetime")
                    data_desc_y = DataDescription.generate_from_data_objects(data_objects, "crimes_count")
                    charts[grid_id] = LineChart(
                        data=data_objects,
                        data_keys_for_selection=["crime_type_name"],
                        label=self.__grid_labels[grid_id],
                        x_axis_data=data_desc_x,
                        x_axis_config=ChartAxisConfiguration(data_steps=65),
                        y_axis_data=data_desc_y,
                        y_axis_config=ChartAxisConfiguration(data_steps=5, show_grid_line=GridLines.Markings),
                        chart_config=ChartConfiguration(padding_right=32),
                        selection_label_text_config=TextMarkingConfiguration(offset_to_other_element=3)
                    )
                elif grid_id == 23:
                    data_objects = DataObject.combine_at(data_objects, "district_name")
                    data_desc_x = DataDescription.generate_from_data_objects(data_objects, "year")
                    data_desc_y = DataDescription.generate_from_data_objects(data_objects, "crimes_count")
                    charts[grid_id] = LineChart(
                        data=data_objects,
                        data_keys_for_selection=["district_name"],
                        label=self.__grid_labels[grid_id],
                        x_axis_data=data_desc_x,
                        x_axis_config=ChartAxisConfiguration(data_steps=data_desc_x.data[1] - data_desc_x.data[0] + 1, show_grid_line=GridLines.Markings),
                        y_axis_data=data_desc_y,
                        y_axis_config=ChartAxisConfiguration(data_steps=5, show_grid_line=GridLines.Markings),
                        chart_config=ChartConfiguration(padding_right=30),
                        selection_label_text_config=TextMarkingConfiguration(offset_to_other_element=3)
                    )
                elif grid_id == 24:
                    data_objects = DataObject.combine_at(data_objects, "district_name")
                    data_desc_x = DataDescription.generate_from_data_objects(data_objects, "month")
                    data_desc_y = DataDescription.generate_from_data_objects(data_objects, "crimes_count")
                    charts[grid_id] = LineChart(
                        data=data_objects,
                        data_keys_for_selection=["district_name"],
                        label=self.__grid_labels[grid_id],
                        x_axis_data=data_desc_x,
                        x_axis_config=ChartAxisConfiguration(data_steps=12, show_grid_line=GridLines.Markings),
                        y_axis_data=data_desc_y,
                        y_axis_config=ChartAxisConfiguration(data_steps=5, show_grid_line=GridLines.Markings),
                        selection_label_text_config=TextMarkingConfiguration(offset_to_other_element=3)
                    )
                elif grid_id == 25:
                    data_desc_x = DataDescription.generate_from_data_objects(data_objects, "crimes_count")
                    data_desc_x.data = [0, data_desc_x.data[1]]
                    data_desc_y = DataDescription.generate_from_data_objects(data_objects, "neighborhood_name")
                    charts[grid_id] = BarChart(
                        data=data_objects,
                        data_keys_for_selection=["neighborhood_name"],
                        label=self.__grid_labels[grid_id],
                        bar_spacing=3,
                        orientation=Orientation.Horizontal,
                        x_axis_data=data_desc_x,
                        x_axis_config=ChartAxisConfiguration(data_steps=5, bottom_offset=0, show_grid_line=GridLines.Markings),
                        y_axis_data=data_desc_y,
                        y_axis_config=ChartAxisConfiguration(show_label=False, data_direction=DataDirection.Negative, bottom_offset=25, top_offset=30),
                        chart_config=ChartConfiguration(padding_left=175),
                        selection_label_text_config=TextMarkingConfiguration(offset_to_other_element=3)
                    )
                elif grid_id == 26:
                    data_objects = DataObject.combine_at(data_objects, "weapon_name")
                    data_desc_x = DataDescription.generate_from_data_objects(data_objects, "month")
                    data_desc_y = DataDescription.generate_from_data_objects(data_objects, "crimes_count")
                    charts[grid_id] = LineChart(
                        data=data_objects,
                        data_keys_for_selection=["weapon_name"],
                        label=self.__grid_labels[grid_id],
                        x_axis_data=data_desc_x,
                        x_axis_config=ChartAxisConfiguration(data_steps=12, show_grid_line=GridLines.Markings),
                        y_axis_data=data_desc_y,
                        y_axis_config=ChartAxisConfiguration(data_steps=5, show_grid_line=GridLines.Markings),
                        selection_label_text_config=TextMarkingConfiguration(offset_to_other_element=3)
                    )
                elif grid_id == 27:
                    data_objects = DataObject.combine_at(data_objects, "weapon_name")
                    data_desc_x = DataDescription.generate_from_data_objects(data_objects, "year")
                    data_desc_y = DataDescription.generate_from_data_objects(data_objects, "crimes_count")
                    charts[grid_id] = LineChart(
                        data=data_objects,
                        data_keys_for_selection=["weapon_name"],
                        label=self.__grid_labels[grid_id],
                        x_axis_data=data_desc_x,
                        x_axis_config=ChartAxisConfiguration(data_steps=data_desc_x.data[1] - data_desc_x.data[0] + 1, show_grid_line=GridLines.Markings),
                        y_axis_data=data_desc_y,
                        y_axis_config=ChartAxisConfiguration(data_steps=5, show_grid_line=GridLines.Markings),
                        chart_config=ChartConfiguration(padding_right=30),
                        selection_label_text_config=TextMarkingConfiguration(offset_to_other_element=3)
                    )
                elif grid_id == 32:
                    data_objects = DataObject.combine_at(data_objects, "neighborhood_name")
                    data_desc_x = DataDescription.generate_from_data_objects(data_objects, "crime_type_name")
                    data_desc_x.fit_data_objects_to(data_objects, ["crimes_count"])
                    data_desc_y = DataDescription.generate_from_data_objects(data_objects, "crimes_count")
                    charts[grid_id] = LineChart(
                        data=data_objects,
                        orientation=Orientation.Vertical,
                        data_keys_for_selection=["neighborhood_name"],
                        label=self.__grid_labels[grid_id],
                        y_axis_data=data_desc_x,
                        y_axis_config=ChartAxisConfiguration(show_label=False, show_grid_line=GridLines.Markings),
                        x_axis_data=data_desc_y,
                        x_axis_config=ChartAxisConfiguration(data_steps=5, show_grid_line=GridLines.Markings),
                        chart_config=ChartConfiguration(padding_left=150),
                        selection_label_text_config=TextMarkingConfiguration(offset_to_other_element=3)
                    )
                elif grid_id == 33:
                    data_desc_x = DataDescription.generate_from_data_objects(data_objects, "crimes_count")
                    data_desc_x.data = [0, data_desc_x.data[1]]
                    data_desc_y = DataDescription.generate_from_data_objects(data_objects, "crime_type_name")
                    charts[grid_id] = BarChart(
                        data=data_objects,
                        data_keys_for_selection=["crime_type_name"],
                        orientation=Orientation.Horizontal,
                        label=self.__grid_labels[grid_id],
                        bar_width=23,
                        x_axis_data=data_desc_x,
                        x_axis_config=ChartAxisConfiguration(data_steps=5, bottom_offset=0, show_grid_line=GridLines.Markings),
                        y_axis_data=data_desc_y,
                        y_axis_config=ChartAxisConfiguration(show_label=False, bottom_offset=20, top_offset=20, marking_steps=1),
                        chart_config=ChartConfiguration(padding_left=150),
                        selection_label_text_config=TextMarkingConfiguration(offset_to_other_element=3)
                    )
                elif grid_id == 34:
                    data_objects = DataObject.combine_at(data_objects, "year")
                    data_desc_x = DataDescription.generate_from_data_objects(data_objects, "month")
                    data_desc_y = DataDescription.generate_from_data_objects(data_objects, "crimes_count")
                    charts[grid_id] = LineChart(
                        data=data_objects,
                        data_keys_for_selection=["year"],
                        label=self.__grid_labels[grid_id],
                        x_axis_data=data_desc_x,
                        x_axis_config=ChartAxisConfiguration(data_steps=12, show_grid_line=GridLines.Markings),
                        y_axis_data=data_desc_y,
                        y_axis_config=ChartAxisConfiguration(data_steps=5, show_grid_line=GridLines.Markings),
                        selection_label_text_config=TextMarkingConfiguration(offset_to_other_element=3)
                    )
                elif grid_id == 35:
                    data_objects = DataObject.combine_at(data_objects, "year")
                    data_desc_x = DataDescription.generate_from_data_objects(data_objects, "weekday")
                    data_desc_y = DataDescription.generate_from_data_objects(data_objects, "crimes_count")
                    charts[grid_id] = LineChart(
                        data=data_objects,
                        data_keys_for_selection=["year"],
                        label=self.__grid_labels[grid_id],
                        x_axis_data=data_desc_x,
                        x_axis_config=ChartAxisConfiguration(show_label=False, show_grid_line=GridLines.Markings),
                        y_axis_data=data_desc_y,
                        y_axis_config=ChartAxisConfiguration(data_steps=5, show_grid_line=GridLines.Markings),
                        chart_config=ChartConfiguration(padding_right=20),
                        selection_label_text_config=TextMarkingConfiguration(offset_to_other_element=3)
                    )
                elif grid_id == 36:
                    data_desc_x = DataDescription.generate_from_data_objects(data_objects, "year")
                    data_desc_y = DataDescription.generate_from_data_objects(data_objects, "crimes_count")
                    data_desc_y.data = [0, data_desc_y.data[1]]
                    charts[grid_id] = BarChart(
                        data=data_objects,
                        data_keys_for_selection=["year"],
                        label=self.__grid_labels[grid_id],
                        x_axis_data=data_desc_x,
                        x_axis_config=ChartAxisConfiguration(data_steps=data_desc_x.data[1] - data_desc_x.data[0] + 1, bottom_offset=65, top_offset=55),
                        y_axis_data=data_desc_y,
                        y_axis_config=ChartAxisConfiguration(data_steps=5, bottom_offset=0, show_grid_line=GridLines.Markings),
                        chart_config=ChartConfiguration(padding_right=30),
                        selection_label_text_config=TextMarkingConfiguration(offset_to_other_element=3)
                    )
                elif grid_id == 37:
                    data_desc_x = DataDescription.generate_from_data_objects(data_objects, "crimes_count")
                    data_desc_x.data = [0, data_desc_x.data[1]]
                    data_desc_y = DataDescription.generate_from_data_objects(data_objects, "district_name")
                    charts[grid_id] = BarChart(
                        data=data_objects,
                        data_keys_for_selection=["district_name"],
                        label=self.__grid_labels[grid_id],
                        bar_width=60,
                        orientation=Orientation.Horizontal,
                        x_axis_data=data_desc_x,
                        x_axis_config=ChartAxisConfiguration(data_steps=5, bottom_offset=0, show_grid_line=GridLines.Markings),
                        y_axis_data=data_desc_y,
                        y_axis_config=ChartAxisConfiguration(show_label=False, bottom_offset=50, top_offset=40),
                        chart_config=ChartConfiguration(padding_left=20 + 10),
                        selection_label_text_config=TextMarkingConfiguration(offset_to_other_element=3)
                    )
                elif grid_id == 38:
                    data_desc_x = DataDescription.generate_from_data_objects(data_objects, "daytime")
                    data_desc_y = DataDescription.generate_from_data_objects(data_objects, "crimes_count")
                    data_desc_y.data = [0, data_desc_y.data[1]]
                    charts[grid_id] = BarChart(
                        data=data_objects,
                        data_keys_for_selection=["daytime"],
                        label=self.__grid_labels[grid_id],
                        x_axis_data=data_desc_x,
                        x_axis_config=ChartAxisConfiguration(show_label=False, bottom_offset=90, top_offset=80),
                        y_axis_data=data_desc_y,
                        y_axis_config=ChartAxisConfiguration(data_steps=5, bottom_offset=0, show_grid_line=GridLines.Markings),
                        chart_config=ChartConfiguration(padding_right=20),
                        selection_label_text_config=TextMarkingConfiguration(offset_to_other_element=3)
                    )
                elif grid_id == 39:
                    data_objects = DataObject.combine_at(data_objects, "crime_type_name")
                    data_desc_x = DataDescription.generate_from_data_objects(data_objects, "daytime")
                    data_desc_y = DataDescription.generate_from_data_objects(data_objects, "crimes_count")
                    charts[grid_id] = LineChart(
                        data=data_objects,
                        data_keys_for_selection=["crime_type_name"],
                        label=self.__grid_labels[grid_id],
                        axis_cross_offset=0,
                        x_axis_data=data_desc_x,
                        x_axis_config=ChartAxisConfiguration(show_label=False, show_grid_line=GridLines.Markings),
                        y_axis_data=data_desc_y,
                        y_axis_config=ChartAxisConfiguration(data_steps=5, show_grid_line=GridLines.Markings),
                        chart_config=ChartConfiguration(padding_right=20),
                        selection_label_text_config=TextMarkingConfiguration(offset_to_other_element=3)
                    )
                elif grid_id == 40:
                    data_objects = DataObject.combine_at(data_objects, "weapon_name")
                    data_desc_x = DataDescription.generate_from_data_objects(data_objects, "district_name")
                    data_desc_y = DataDescription.generate_from_data_objects(data_objects, "crimes_count")
                    charts[grid_id] = LineChart(
                        data=data_objects,
                        data_keys_for_selection=["weapon_name"],
                        label=self.__grid_labels[grid_id],
                        x_axis_data=data_desc_x,
                        x_axis_config=ChartAxisConfiguration(show_label=False, show_grid_line=GridLines.Markings),
                        y_axis_data=data_desc_y,
                        y_axis_config=ChartAxisConfiguration(data_steps=5, show_grid_line=GridLines.Markings),
                        chart_config=ChartConfiguration(padding_right=20),
                        selection_label_text_config=TextMarkingConfiguration(offset_to_other_element=3)
                    )
                elif grid_id == 41:
                    data_objects = DataObject.combine_at(data_objects, "neighborhood_name")
                    data_desc_x = DataDescription.generate_from_data_objects(data_objects, "daytime")
                    data_desc_y = DataDescription.generate_from_data_objects(data_objects, "crimes_count")
                    charts[grid_id] = LineChart(
                        data=data_objects,
                        data_keys_for_selection=["neighborhood_name"],
                        label=self.__grid_labels[grid_id],
                        x_axis_data=data_desc_x,
                        x_axis_config=ChartAxisConfiguration(show_grid_line=GridLines.Markings),
                        y_axis_data=data_desc_y,
                        y_axis_config=ChartAxisConfiguration(data_steps=5, show_grid_line=GridLines.Markings),
                        chart_config=ChartConfiguration(padding_right=60),
                        selection_label_text_config=TextMarkingConfiguration(offset_to_other_element=3)
                    )
                elif grid_id == 42:
                    data_objects = DataObject.combine_at(data_objects, "year")
                    data_desc_x = DataDescription.generate_from_data_objects(data_objects, "datetime")
                    data_desc_y = DataDescription.generate_from_data_objects(data_objects, "crimes_count")
                    charts[grid_id] = LineChart(
                        data=data_objects,
                        data_keys_for_selection=["year"],
                        label=self.__grid_labels[grid_id],
                        x_axis_data=data_desc_x,
                        x_axis_config=ChartAxisConfiguration(data_steps=62),
                        y_axis_data=data_desc_y,
                        y_axis_config=ChartAxisConfiguration(data_steps=3, show_grid_line=GridLines.Markings),
                        chart_config=ChartConfiguration(padding_right=32),
                        selection_label_text_config=TextMarkingConfiguration(offset_to_other_element=3)
                    )
                elif grid_id == 43:
                    data_desc_x = DataDescription.generate_from_data_objects(data_objects, "weekday")
                    data_desc_y = DataDescription.generate_from_data_objects(data_objects, "crime_type_name")
                    charts[grid_id] = ScatterPlot(
                        data=data_objects,
                        data_keys_for_selection=["weekday", "crime_type_name"],
                        label=self.__grid_labels[grid_id],
                        size_key="crimes_count",
                        selection_key="crimes_count",
                        x_axis_data=data_desc_x,
                        x_axis_config=ChartAxisConfiguration(show_label=False),
                        y_axis_data=data_desc_y,
                        y_axis_config=ChartAxisConfiguration(show_label=False, data_direction=DataDirection.Negative),
                        chart_config=ChartConfiguration(padding_left=150, padding_right=35),
                        selection_label_text_config=TextMarkingConfiguration(offset_to_other_element=3)
                    )
                elif 44 <= grid_id <= 48:
                    data_objects = DataObject.combine_at(data_objects, "crime_type_name")
                    data_desc_x = DataDescription.generate_from_data_objects(data_objects, "month")
                    data_desc_y = DataDescription.generate_from_values_and_scheme(data_values.values(), data_schemes.values(), "crimes_count")
                    charts[grid_id] = LineChart(
                        data=data_objects,
                        data_keys_for_selection=["crime_type_name"],
                        label=self.__grid_labels[grid_id],
                        x_axis_data=data_desc_x,
                        x_axis_config=ChartAxisConfiguration(data_steps=12, show_grid_line=GridLines.Markings),
                        y_axis_data=data_desc_y,
                        y_axis_config=ChartAxisConfiguration(data_steps=5, show_grid_line=GridLines.Markings)
                    )
                elif 49 <= grid_id <= 53:
                    data_objects = DataObject.combine_at(data_objects, "district_name")
                    data_desc_x = DataDescription.generate_from_data_objects(data_objects, "month")
                    data_desc_y = DataDescription.generate_from_values_and_scheme(data_values.values(), data_schemes.values(), "crimes_count")
                    charts[grid_id] = LineChart(
                        data=data_objects,
                        data_keys_for_selection=["district_name"],
                        label=self.__grid_labels[grid_id],
                        x_axis_data=data_desc_x,
                        x_axis_config=ChartAxisConfiguration(data_steps=12, show_grid_line=GridLines.Markings),
                        y_axis_data=data_desc_y,
                        y_axis_config=ChartAxisConfiguration(data_steps=5, show_grid_line=GridLines.Markings)
                    )
                elif grid_id == 54:
                    data_desc_x = DataDescription.generate_from_data_objects(data_objects, "premise_name")
                    data_desc_y = DataDescription.generate_from_data_objects(data_objects, "crime_type_name")
                    charts[grid_id] = ScatterPlot(
                        data=data_objects,
                        data_keys_for_selection=["premise_name", "crime_type_name"],
                        label=self.__grid_labels[grid_id],
                        size_key="crimes_count",
                        selection_key="crimes_count",
                        x_axis_data=data_desc_x,
                        x_axis_config=ChartAxisConfiguration(show_label=False, marking_orientation=Orientation.Vertical),
                        y_axis_data=data_desc_y,
                        y_axis_config=ChartAxisConfiguration(show_label=False),
                        chart_config=ChartConfiguration(padding_left=150, padding_right=35, padding_bottom=120)
                    )

        start_time = time.time()
        last_time = start_time

        # Create the map
        map_values = {}
        for query_name in ["map data from neighborhoods", "districts per neighborhood", "crime types per neighborhood", "crime type names", "highest weapon usage per neighborhood"]:
            map_values[query_name], _ = self.__input_data[query_name]

        # Create the data structure for the map points.
        neighborhood_values = {v[0]: {"obj_id": v[0], "lat": v[1] or 0, "lng": v[2] or 0,
                                      "attributes": {"neighborhood_name": v[0], "count": v[3], "districts": [],
                                                     "crime_types": [ctn[0] for ctn in map_values["crime type names"]],
                                                     "crime_types_count": [0] * len(map_values["crime type names"]),
                                                     "highest_crime_type": None,
                                                     "highest_weapon_usage": None
                                                     }
                                      }
                               for v in map_values["map data from neighborhoods"]}
        # Add the districts to the neighborhoods.
        for values in map_values["districts per neighborhood"]:
            if values[1] not in neighborhood_values[values[0]]["attributes"]["districts"]:
                neighborhood_values[values[0]]["attributes"]["districts"].append(values[1])
        # Add the crime types to the neighborhoods.
        for values in map_values["crime types per neighborhood"]:
            index = map_values["crime type names"].index([values[1]])
            neighborhood_values[values[0]]["attributes"]["crime_types_count"][index] = values[2]

            neighborhood_values[values[0]]["attributes"]["highest_crime_type"] = max
        for neighborhood, values in neighborhood_values.iteritems():
            highest = max([(i, v) for i, v in enumerate(values["attributes"]["crime_types_count"])], key=lambda x: x[1])
            values["attributes"]["highest_crime_type"] = values["attributes"]["crime_types"][highest[0]]
        # Add highest weapon to the neighborhoods.
        for values in map_values["highest weapon usage per neighborhood"]:
            if values[0] in neighborhood_values:
                neighborhood_values[values[0]]["attributes"]["highest_weapon_usage"] = values[1]

        image_info = MapImageInfo(
            filename=self.__map_image_info["image"],
            resolution=self.__map_image_info["size"],
            min_geo=GeoCoord(long=self.__map_image_info["left_top"]["lng"], lat=self.__map_image_info["left_top"]["lat"]),
            max_geo=GeoCoord(long=self.__map_image_info["right_bottom"]["lng"], lat=self.__map_image_info["right_bottom"]["lat"])
        )
        map_view = MapVisView(
            data_object_list=neighborhood_values.values(),
            data_keys_for_selection=["neighborhood_name"],
            image_info=image_info,
            label=self.__grid_labels[15],
            chart_config=ChartConfiguration(padding_top=25)
        )
        self.__multi_div_node.add_node_to_grid_element(grid_element_id=15, node=map_view)

        map_view.draw_map()

        now = time.time()
        print "Duration:", now - last_time, "| drawn map"
        last_time = now

        # Draw the charts.
        for grid_element_id, chart in charts.iteritems():
            self.__multi_div_node.add_node_to_grid_element(grid_element_id=grid_element_id, node=chart)
            chart.draw_chart()

            now = time.time()
            print "Duration:", now - last_time, "| drawn chart ", chart.label
            last_time = now

            chart.add_aid_line_controller(aid_line_controller_type=AidLineType.Lasso)

            if grid_element_id == 22:
                continue

            if isinstance(chart, BarChart):
                if chart.orientation is Orientation.Horizontal:
                    aid_line_types = [AidLineType.DepositVertical, AidLineType.AxisDragY]
                else:
                    aid_line_types = [AidLineType.DepositHorizontal, AidLineType.AxisDragX]
            else:
                aid_line_types = [AidLineType.Deposit, AidLineType.AxisDragX, AidLineType.AxisDragY]

            for aid_line_type in aid_line_types:
                chart.add_aid_line_controller(aid_line_controller_type=aid_line_type)
                chart.set_aid_line_controller_attributes(
                    aid_line_controller_type=aid_line_type,
                    intersection_config=IntersectionConfiguration(
                        show_intersections=True,
                        show_label=True,
                        label_content_type='data_object' if grid_element_id in [12, 43, 54] else 'axis'
                    ),
                    show_aid_line_labels=True,
                    use_data_point_snapping=True,
                    labels_only_at_data_points=True if isinstance(chart, LineChart) else False
                )

        self.__divico_control = DivicoControl(multi_view_node=self.__multi_div_node)

        print "The complete creation needed ", time.time() - start_time
