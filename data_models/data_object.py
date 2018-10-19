import datetime

from libavg.avg import Color

from configs import config_app
from data_models.attribute import Attribute
from data_models.data_enums import *
from data_models.data_enums import DataType
from divico_ctrl.translation import T
from events.event_dispatcher import EventDispatcher
from libavg_charts.utils.default_values import DataDefaults


class DataObject(EventDispatcher):
    _SELECTION_STATE_CHANGED = "selectionStateChanged"
    _POS_CHANGED = "posChanged"
    _SIZE_CHANGED = "sizeChanged"
    _LEVEL_OF_DETAIL_CHANGED = "levelOfDetailChanged"
    _COLOR_CHANGED = "colorChanged"

    def __init__(self, obj_id, attributes, color=DataDefaults.COLOR,
                 pos_x=0, pos_y=0, width=20, height=20, level_of_detail=0):
        """
        :param obj_id: The name of this data object.
        :type obj_id: object
        :param attributes: The list of all different data this object holds.
        :type attributes: list[Attribute]
        :param color: The color for this data object.
        :type color: Color
        """
        EventDispatcher.__init__(self)

        self.__pos_x = pos_x
        self.__pos_y = pos_y
        self.__width = width
        self.__height = height
        self.__level_of_detail = level_of_detail

        self.__value_length = None
        self.__attributes = {}
        self.__obj_id = obj_id
        self.__color = color
        self.__selection_state = DataSelectionState.Nothing

        for attribute in attributes:
            self.__attributes[attribute.data_name] = attribute

    def __repr__(self):
        return "DO {}: {}".format(self.__obj_id, self.__attributes.values())

    @property
    def pos_x(self):
        """
        :rtype: float
        """
        return self.__pos_x

    @pos_x.setter
    def pos_x(self, value):
        """
        :type value: float
        """
        if self.__pos_x == value:
            return
        self.__pos_x = value
        self.dispatch(self._POS_CHANGED, pos_x=value, pos_y=self.__pos_y)

    @property
    def pos_y(self):
        """
        :rtype: float
        """
        return self.__pos_y

    @pos_y.setter
    def pos_y(self, value):
        """
        :type value: float
        """
        if self.__pos_y == value:
            return
        self.__pos_y = value
        self.dispatch(self._POS_CHANGED, pos_x=self.__pos_x, pos_y=value)

    @property
    def width(self):
        """
        :rtype: float
        """
        return self.__width

    @width.setter
    def width(self, value):
        """
        :type value: float
        """
        if self.__width == value:
            return
        self.__width = value
        self.dispatch(self._SIZE_CHANGED, width=value, height=self.__height)

    @property
    def height(self):
        """
        :rtype: float
        """
        return self.__height

    @height.setter
    def height(self, value):
        """
        :type value: float
        """
        if self.__height == value:
            return
        self.__height = value
        self.dispatch(self._SIZE_CHANGED, width=self.__width, height=value)

    @property
    def level_of_detail(self):
        """
        :rtype: int
        """
        return self.__level_of_detail

    @level_of_detail.setter
    def level_of_detail(self, value):
        """
        :type value: int
        """
        if self.__level_of_detail == value:
            return
        self.__level_of_detail = value
        self.dispatch(self._LEVEL_OF_DETAIL_CHANGED, level_of_detail=value)

    @property
    def obj_id(self):
        """
        :rtype: object
        """
        return self.__obj_id

    @obj_id.setter
    def obj_id(self, obj_name):
        """
        :type obj_name: object
        """
        self.__obj_id = obj_name

    @property
    def attributes(self):
        """
        :rtype: dict[str, Attribute]
        """
        return self.__attributes

    @property
    def color(self):
        """
        :rtype: Color
        """
        return self.__color

    @color.setter
    def color(self, color):
        """
        :type color: Color
        """
        self.__color = color
        self.dispatch(self._COLOR_CHANGED, sender=self, new_color=color)

    @property
    def selection_state(self):
        """
        :rtype: DataSelectionState
        """
        return self.__selection_state

    @selection_state.setter
    def selection_state(self, value):
        """
        :type value: DataSelectionState
        """
        if self.__selection_state is value:
            return
        old_state = self.__selection_state
        self.__selection_state = value
        self.dispatch(self._SELECTION_STATE_CHANGED, sender=self, new_state=value, old_state=old_state)

    def set_pos(self, pos_x, pos_y):
        """
        Sets the position of this data object.

        :param pos_x: The x coordinate of the new position.
        :type pos_x: float
        :param pos_y: The y coordinate of the new position.
        :type pos_y: float
        """
        if self.__pos_x == pos_x and self.__pos_y == pos_y:
            return
        self.__pos_x = pos_x
        self.__pos_y = pos_y
        self.dispatch(self._POS_CHANGED, pos_x=pos_x, pos_y=pos_y)

    @staticmethod
    def generate_from_key_and_data(orig_data, obj_name_key=None, search_key_values=None):
        """
        Generates from a data set. Separates the object from the given key.

        :param orig_data: The data to separate. Each dict is a row.
        :type orig_data: list[dict[str, object]]
        :param obj_name_key: The key, that value will be used as the name of the objects. If objects have the same name the will fuse together.
                             If this parameter in None the name will be given through the number of the row the objects was in.
        :type obj_name_key: str
        :param search_key_values: One specific value in the key.
        :type search_key_values: list[object]
        :return: The list of data objects.
        :rtype: list[DataObject]
        """
        search_key_values = search_key_values if search_key_values else []

        separated_data = {}
        data_types = {}
        for i, row in enumerate(orig_data):
            # Ignore all rows that don't got the key or the value.
            if obj_name_key and obj_name_key not in row:
                continue
            # Add the new data object if it's not added yet.
            obj_name = row[obj_name_key] if obj_name_key else i
            # Only add the data objects with a given key value.
            if len(search_key_values) > 0 and obj_name not in search_key_values:
                continue

            if obj_name not in separated_data:
                separated_data[obj_name] = {}
                data_types[obj_name] = {}

            for key, value in row.iteritems():
                # Ignore the key and its value itself.
                if key == obj_name_key:
                    continue
                if key not in data_types[obj_name]:
                    if isinstance(value, int):
                        data_types[obj_name][key] = DataType.Integer
                    elif isinstance(value, float):
                        data_types[obj_name][key] = DataType.Float
                    elif isinstance(value, str):
                        data_types[obj_name][key] = DataType.String
                    elif isinstance(value, datetime.datetime):
                        if "Date" in key or "date" in key:
                            data_types[obj_name][key] = DataType.Date
                        elif "Time" in key or "time" in key:
                            data_types[obj_name][key] = DataType.Time
                # Add the new axis if it's not added yet.
                if key not in separated_data[obj_name]:
                    separated_data[obj_name][key] = []

                separated_data[obj_name][key].append(value)

        data_objects = []
        for obj_name, data_on_axis in separated_data.iteritems():
            attributes = []
            for data_name in data_on_axis.iterkeys():
                attributes.append(Attribute(
                    data_name=data_name,
                    data_type=data_types[obj_name][data_name],
                    values=data_on_axis[data_name]
                ))

            new_data_object = DataObject(
                obj_id=obj_name,
                attributes=attributes
            )
            data_objects.append(new_data_object)

        return data_objects

    @staticmethod
    def generate_from_sql_results(object_values, scheme):
        """
        Converts a query from a sql database to data objects.

        :param object_values: The values for all objects.
        :type object_values: list[list]]
        :param scheme: The scheme that the data is in.
        :type scheme: list[tuple[str, DataType]]
        :return: The converted data values.
        :rtype: list[DataObject]
        """
        data_objects = []
        for obj_id, object in enumerate(object_values):
            attributes = []
            value = None
            for i, value in enumerate(object):
                if value is None:
                    break

                # Convert the values if necessary. unicode to string and string to datetime.
                if scheme[i][1] is DataType.String:
                    value = str(value)
                elif scheme[i][1] is DataType.DateTime:
                    value = datetime.datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
                elif scheme[i][1] is DataType.Date:
                    value = datetime.datetime.strptime(value, "%Y-%m-%d")
                elif scheme[i][1] is DataType.Time:
                    value = datetime.datetime.strptime(value, "%H:%M:%S")
                elif scheme[i][1] is DataType.Weekday:
                    value = T.tl(msg=DataType.int_to_weekday(value), lang=config_app.default_language)
                elif scheme[i][1] is DataType.Month:
                    value = T.tl(msg=DataType.int_to_month(value), lang=config_app.default_language)
                elif scheme[i][1] is DataType.Daytime:
                    value = T.tl(msg=DataType.int_to_daytime(value), lang=config_app.default_language)
                elif scheme[i][1] is DataType.Day:
                    value = datetime.datetime.strptime("{}-1971".format(value if value != "29-02" else "28-02"), "%d-%m-%Y")

                attributes.append(Attribute(
                    data_name=scheme[i][0],
                    data_type=scheme[i][1],
                    values=[value]
                ))
            if value is None:
                continue

            data_objects.append(DataObject(
                obj_id=obj_id,
                attributes=attributes
            ))

        return data_objects

    @staticmethod
    def combine(data_objects_list, attributes_to_ignore=None, obj_ids=None):
        """
        Combines a list of data objects in one.

        :param data_objects_list: The list of data objects to combine. Each list is a own data object.
        :type data_objects_list: list[list[DataObject]]
        :param obj_ids: The ids for the newly created data objects. If empty a counter will determine the obj id.
        :type obj_ids: list[str]
        :param attributes_to_ignore: A list of attribute names that don't need be added to the new object.
        :type attributes_to_ignore: list[str]
        :return: The combined data objects.
        :rtype: list[DataObject]
        """
        attributes_to_ignore = attributes_to_ignore if attributes_to_ignore else []

        new_data_objects = []
        for i, data_object_l in enumerate(data_objects_list):
            attributes = {}
            for data_object in data_object_l:
                for name, attribute in data_object.attributes.iteritems():
                    if name in attributes_to_ignore:
                        continue
                    if name not in attributes:
                        attributes[name] = attribute
                    else:
                        attributes[name] += attribute
            new_data_objects.append(DataObject(
                obj_id=i if not obj_ids else obj_ids[i],
                attributes=attributes.values()
            ))
        return new_data_objects

    @staticmethod
    def combine_at(data_objects, combine_at):
        """
        Combines a list of data objects in one.

        :param data_objects: The list of data objects to combine. Each list is a own data object.
        :type data_objects: list[DataObject]
        :param combine_at: Only combine data objects that have value in this given key is the same. The value will be used
                           as the new obj_id.
        :type combine_at: str
        :return: The combined data objects.
        :rtype: list[DataObject]
        """
        key_list = []
        data_objects_list = []
        for data_object in data_objects:
            # Get the labels for the new data objects.
            key = data_object.attributes[combine_at].values
            if key not in key_list:
                key_list.append(key)
                data_objects_list.append([])
            # Gather all data objects with the same key.
            data_objects_list[key_list.index(key)].append(data_object)

        new_data_objects = []
        for i, data_object_l in enumerate(data_objects_list):
            attributes = {}
            for data_object in data_object_l:
                # Create new attributes or add another attribute to a existing one.
                for name, attribute in data_object.attributes.iteritems():
                    if name not in attributes:
                        attributes[name] = attribute.copy()
                    else:
                        attributes[name] += attribute

            # Make the attribute distinct.
            attributes[combine_at].make_distinct()
            new_data_objects.append(DataObject(
                obj_id=key_list[i][0],
                attributes=attributes.values()
            ))

        return new_data_objects

    def start_listening(self, selection_state_changed=None, pos_changed=None, size_changed=None, level_of_detail_changed=None,
                        color_changed=None):
        """
        Registers a callback to listen to changes or events of this data object. Listeners can register to any number of the
        provided events. For the required structure of the callbacks see below.

        :param selection_state_changed: Called when the data selection state has been changed.
        :type selection_state_changed: function(sender:DataObject, new_state:DataSelectionState, old_state:DataSelectionState.
        :param pos_changed: Called when the position of this data object has changed.
        :type pos_changed: function(sender:DataObject, pos_x:float, pos_y:float)
        :param size_changed: Called when the size of this data object has changed.
        :type size_changed: function(sender:DataObject, width:float, height:float)
        :param level_of_detail_changed: Called when the level of detail of this data object has changed.
        :type level_of_detail_changed: function(sender:DataObject, level_of_detail:int)
        :param color_changed: Called when the color for this data object has changed.
        :type color_changed: function(sender:DataObject, new_color:avg.Color)
        """
        self.bind(self._SELECTION_STATE_CHANGED, selection_state_changed)
        self.bind(self._POS_CHANGED, pos_changed)
        self.bind(self._SIZE_CHANGED, size_changed)
        self.bind(self._LEVEL_OF_DETAIL_CHANGED, level_of_detail_changed)
        self.bind(self._COLOR_CHANGED, color_changed)

    def stop_listening(self, selection_state_changed=None, pos_changed=None, size_changed=None, level_of_detail_changed=None,
                       color_changed=None):
        """
        Stops listening to an event the listener has registered to previously. The provided callback needs to be the
        same that was used to listen to the event in the fist place.

        :param selection_state_changed: Called when the data selection state has been changed.
        :type selection_state_changed: function(sender:DataObject, new_state:DataSelectionState, old_state:DataSelectionState.
        :param pos_changed: Called when the position of this data object has changed.
        :type pos_changed: function(sender:DataObject, pos_x:float, pos_y:float)
        :param size_changed: Called when the size of this data object has changed.
        :type size_changed: function(sender:DataObject, width:float, height:float)
        :param level_of_detail_changed: Called when the level of detail of this data object has changed.
        :type level_of_detail_changed: function(sender:DataObject, level_of_detail:int)
        :param color_changed: Called when the color for this data object has changed.
        :type color_changed: function(sender:DataObject, new_color:avg.Color)
        """
        self.unbind(self._SELECTION_STATE_CHANGED, selection_state_changed)
        self.unbind(self._POS_CHANGED, pos_changed)
        self.unbind(self._SIZE_CHANGED, size_changed)
        self.unbind(self._LEVEL_OF_DETAIL_CHANGED, level_of_detail_changed)
        self.unbind(self._COLOR_CHANGED, color_changed)
