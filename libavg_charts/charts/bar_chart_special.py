from data_models.data_desciption import DataDescription
from data_models.data_enums import DataType
from data_models.data_object import DataObject
from libavg_charts.charts.chart_basis.bar_chart_base import BarChartBase


class BarChartOneObject(BarChartBase):
    """
    Bar chart for one object.
    It's not possible to use a sum for the y axis.
    """
    def __init__(self, data_object, **kwargs):
        """          
        The parameter 'data' will not be used with this class.
              
        :type data_object: MultivariateDataObject
        :param kwargs: All other parameter for the div node and the two axis chart.
        """
        if 'data' in kwargs:
            kwargs.pop('data')

        super(BarChartOneObject, self).__init__(data=[data_object], **kwargs)

    def _create_data_objects(self, x_axis_data, y_axis_data):
        """
        Creates all bars for all data objects in this chart.
        
        :type x_axis_data: DataDescription
        :type y_axis_data: DataDescription
        """
        bar_width = self._calc_bar_width(x_key_name=x_axis_data.label, y_key_name=y_axis_data.label)

        for data_object in self._data_objects.itervalues():
            # Get all the values.
            x_values = data_object.attributes[x_axis_data.label].values
            y_values = data_object.attributes[y_axis_data.label].values
            for i in range(len(x_values)):
                self._data_object_nodes[x_values[i]] = self._create_new_bar(
                    x_key_name=x_axis_data.label,  y_key_name=y_axis_data.label,
                    x_value=x_values[i], y_value=y_values[i],
                    bar_width=bar_width, color=data_object.color
                )

        super(BarChartOneObject, self)._create_data_objects_for_base()


class BarChartManyObjects(BarChartBase):
    """
    Bar chart for a data set with many data objects. The x axis will be automatically the obj names from the objects.
    It's possible to use a sum for the y axis.
    """
    def __init__(self, data, y_axis_data=None, x_axis_key="obj_name", **kwargs):
        """          
        The parameter 'x_axis_data' will not be used with this class.
        The axis configuration can be customized as wished. But the marking side, orientation, top offset, tick side, bottom offset of x and
        the marking steps of the x axis will be set through this class.

        :type data: list[DataObject]
        :param y_axis_data: The data object for the y axis. Can be 'None' if another 'x_axis_key' than the default is given.
        :type y_axis_data: DataDescription
        :param x_axis_key: The key that will be used on the x axis. If it's not the default value ('obj_name') than the y axis will be changed
                           to the data type 'Count'.
        :type x_axis_key: str
        :param kwargs: All other parameter for the div node and the two axis chart.
        """
        if 'x_axis_data' in kwargs:
            kwargs.pop('x_axis_data')

        # Check if a y_axis_data object is needed.
        if x_axis_key == "obj_name" and not y_axis_data:
            raise AttributeError("The y_axis_data isn't allowed to be 'None' if the x_axis_key is the default value!")
        elif x_axis_key != "obj_name":
            # Count all appearances of the values of a key.
            self._count = {}
            for data_object in data:
                key = data_object.attributes[x_axis_key].values[0]
                if key not in self._count:
                    self._count[key] = 0
                self._count[key] += 1
            y_axis_data = DataDescription(
                data_type=DataType.Count, data=[c for c in self._count.itervalues()], key_name="Count", unit="")

        x_axis_data = DataDescription.generate_from_data_objects(data_objects=data, description_name=x_axis_key)
        super(BarChartManyObjects, self).__init__(y_axis_data=y_axis_data, x_axis_data=x_axis_data, data=data, **kwargs)

    def _create_data_objects(self, x_axis_data, y_axis_data):
        """
        Creates all bars for all data objects in this chart.
        
        :type x_axis_data: DataDescription
        :type y_axis_data: DataDescription
        """
        bar_width = self._calc_bar_width(x_key_name=x_axis_data.label, y_key_name=y_axis_data.label)

        for data_object in self._data_objects.itervalues():
            # Get all the values.
            if x_axis_data.label == "obj_name":
                x_value = data_object.obj_id
            else:
                x_value = data_object.attributes[x_axis_data.label].values[0]

            # Decide which data is used:
            if DataType.is_sum(self.vertical_axis_views[y_axis_data.label].data_desc.data_type):
                y_value = sum(data_object.attributes[y_axis_data.label].values)
            # If its a count use the pre calculated values.
            elif self.vertical_axis_views[y_axis_data.label].data_desc.data_type == DataType.Count:
                y_value = self._count[data_object.attributes[x_axis_data.label].values[0]]
            # If its not the sum, use the first value in the list.
            else:
                y_value = data_object.attributes[y_axis_data.label].values[0]

            self._data_object_nodes[data_object.obj_id] = self._create_new_bar(
                x_key_name=x_axis_data.label,  y_key_name=y_axis_data.label,
                x_value=x_value, y_value=y_value,
                bar_width=bar_width, color=data_object.color
            )

        super(BarChartManyObjects, self)._create_data_objects_for_base()

    def _generate_axis_configurations(self, x_axis_config, y_axis_config):
        """
        Sets the axis configuration for this chart.
        It should be overwritten but also be used from the children classes if necessary.

        :param x_axis_config: The input configuration for the x axis of this chart.
        :type x_axis_config: ChartAxisConfiguration
        :param y_axis_config: The input configuration for the y axis of this chart.
        :type y_axis_config: ChartAxisConfiguration
        :return: The created or changed configurations for the axis. First is the x axis, second the y axis.
        :rtype: tuple[ChartAxisConfiguration, ChartAxisConfiguration]
        """
        x_axis_config, y_axis_config = super(BarChartManyObjects, self)._generate_axis_configurations(x_axis_config=x_axis_config, y_axis_config=y_axis_config)

        x_axis_config.marking_steps = 1
        x_axis_config.top_offset = x_axis_config.bottom_offset / 2 + self._bar_spacing / 2 + self._bar_line_width
        y_axis_config.top_offset = y_axis_config.bottom_offset / 2 + self._bar_spacing / 2 + self._bar_line_width
        return x_axis_config, y_axis_config