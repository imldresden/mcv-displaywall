import datetime

from configs import config_app
from data_models.attribute import Attribute
from data_models.data_enums import DataType
from data_models.data_object import DataObject
from divico_ctrl.translation import T


class DataDescription(object):
    def __init__(self, data_type, data, key_name, label=None, unit=None):
        """
        :param data_type: The type of the data.
        :type data_type: DataType
        :param data: The list of all possible data. For all besides String its only necessary to place the 
                     first (smallest) and the last (highest) element in the list.
        :type data: list[object]
        :param label: The label this data should be have.
        :type label: str
        :param unit: The unit this data should be have. Will be ignored if the data type is Date, Time or String.
        :type unit: str
        """
        self.__data_type = data_type
        self.__data = data

        if not DataType.is_string(self.__data_type):
            if DataType.is_number(self.__data_type):
                data_range = [float('inf'), float('-inf')]
            else:
                data_range = [datetime.datetime.max, datetime.datetime.min]

            for date in self.__data:
                data_range = [date if date < data_range[0] else data_range[0],
                              date if date > data_range[1] else data_range[1]]
            self.__data = data_range

        self.__key_name = key_name
        self.__label = label
        if label is None:
            self.__label = key_name
        self.__unit = unit if self.__data_type is DataType.Integer or self.__data_type is DataType.Float else None

    def __repr__(self):
        return "DD {}({} {}: {})".format(self.__label, self.__data_type, self.__unit, self.__data)

    @property
    def data_type(self):
        """
        The type of the data.
        
        :rtype: DataType
        """
        return self.__data_type

    @property
    def data(self):
        """
        The list of all possible data. For all besides String its only necessary to place the first (smallest) 
        and the last (highest) element in the list.
        
        :rtype: list[object]
        """
        return self.__data

    @data.setter
    def data(self, value):
        """
        :type value: list[object]
        """
        self.__data = value

    @property
    def key_name(self):
        """
        :rtype: str
        """
        return self.__key_name

    @key_name.setter
    def key_name(self, key_name):
        """
        :type key_name: str
        """
        self.__key_name = key_name

    @property
    def label(self):
        """
        The label this data have.
        
        :rtype: str
        """
        return self.__label

    @label.setter
    def label(self, label):
        """
        :type label: str
        """
        self.__label = label

    @property
    def unit(self):
        """
        The unit this data have. It will be None if the data type is Date, Time or String.
        
        :rtype: str
        """
        return self.__unit

    @unit.setter
    def unit(self, unit):
        self.__unit = unit

    def fit_data_objects_to(self, data_objects, other_attributes=None):
        """
        Changes the attribute that is represented through this description in all the given data objects.
        All objects will have the same number of attributes for this data description.

        :param data_objects: The data objects that should be fitted to this data description.
        :type data_objects: list[DataObject]
        :param other_attributes: All attributes that should get the same order as the attributes represented through this
                                 description. If a value isn't in the attributes a default value will be used.
        :type other_attributes: list[str]
        """
        # TODO: This only works for string descriptions at the moment. It should be extended if wished.

        other_attributes = other_attributes or []

        for data_object in data_objects:
            if self.__key_name not in data_object.attributes:
                continue
            old_main_attribute = data_object.attributes[self.__key_name]
            # Create a new attribute for the new fitting order of the values.
            data_object.attributes[self.__key_name] = Attribute(
                data_name=old_main_attribute.data_name,
                data_type=old_main_attribute.data_type,
                values=self.__data
            )
            # If other attributes should be changed as well.
            for a_key_name in other_attributes:
                if a_key_name not in data_object.attributes:
                    continue
                old_attribute = data_object.attributes[a_key_name]

                values = []
                # Generate the right order of the values.
                for a_value in self.__data:
                    # Generate a default value if no value was found.
                    if a_value not in old_main_attribute.values:
                        values.append(0 if DataType.is_number(old_attribute.data_type) else "")
                    else:
                        values.append(old_attribute.values[old_main_attribute.values.index(a_value)])
                # Create the new attribute.
                data_object.attributes[a_key_name] = Attribute(
                    data_name=old_attribute.data_name,
                    data_type=old_attribute.data_type,
                    values=values
                )

    def fill_data_objects_for(self, data_objects):
        """
        Check the given data objects and add default one if a value of this data description wasn't found.

        :param data_objects: The data objects that should be checked and filled if necessary.
        :type data_objects: list[DataObject]
        """
        other_attributes = []
        if len(data_objects) > 0:
            other_attributes = [(k, a.data_type) for k, a in data_objects[0].attributes.iteritems() if k != self.__key_name]

        for value in self.__data:
            if len([d for d in data_objects if self.__key_name in d.attributes and (d.attributes[self.__key_name].values[0] == value or d.attributes[self.__key_name].values == value)]) != 0:
                continue

            attributes = [Attribute(data_name=self.__key_name, data_type=self.__data_type, values=[value])]
            attributes.extend([Attribute(data_name=k, data_type=dt, values=[0 if DataType.is_number(dt) else ""]) for k, dt in other_attributes])

            data_objects.append(DataObject(
                obj_id=value,
                attributes=attributes
            ))

    @staticmethod
    def generate_from_key_and_data(orig_data, data_separation_key=None, separation_key_values=None):
        """
        Generates from a data set from a given key with a value a number of lists from the data rest.

        :param orig_data: The data to separate. Each dict is a row.
        :type orig_data: list[dict[str, object]]
        :param data_separation_key: The key that will be used to separate the data in different descriptions. If none all rows will be used.
        :type data_separation_key: str
        :param separation_key_values: Specific values in the key. Only create the descriptions for those in this list. Only usable if data_separation_key is given.
        :type separation_key_values: list[object]
        :return: The list of data. The rest from the original data separated by the key.
        :rtype: dict[str, DataDescription]
        """
        separation_key_values = separation_key_values if separation_key_values else []

        separated_data = {}
        data_types = {}
        for row in orig_data:
            # Ignore all rows that don't got the key or the value.
            if data_separation_key and data_separation_key not in row:
                continue
            if data_separation_key and len(separation_key_values) > 0 and row[data_separation_key] not in separation_key_values:
                continue

            for key, value in row.iteritems():
                # Ignore the key and its value itself.
                if key == data_separation_key:
                    continue
                # Generate the data type.
                if key not in data_types:
                    if isinstance(value, int):
                        data_types[key] = DataType.Integer
                    elif isinstance(value, float):
                        data_types[key] = DataType.Float
                    elif isinstance(value, str):
                        data_types[key] = DataType.String
                        # TODO: Add the other data types

                # Save the data in another form.
                if key not in separated_data:
                    separated_data[key] = []
                separated_data[key].append(value)

        data_descriptions = {}
        # Convert the list in data descriptions.
        for key, new_data in separated_data.iteritems():
            data_descriptions[key] = DataDescription(
                data_type=data_types[key],
                data=new_data,
                key_name=key
            )

        return data_descriptions

    @staticmethod
    def generate_from_data_objects(data_objects, description_name):
        """
        Generates a data description from a given data object.

        :param data_objects: The data objects the description should be created from.
        :type data_objects: list[DataObject]
        :param description_name: The name/key for this description that should be created.
        :type description_name: str
        :return: The newly created data description.
        :rtype: DataDescription
        """
        if len(data_objects) == 0:
            return None

        # Only use the labels for the several objects.
        if description_name == "obj_name":
            data = []
            for data_object in data_objects:
                data.append(data_object.obj_id)

            data_description = DataDescription(
                data_type=DataType.String,
                data=data,
                key_name="obj name"
            )
        else:
            # Get the data type for the description.
            if description_name not in data_objects[0].attributes:
                return None
            data_type = data_objects[0].attributes[description_name].data_type

            data = []
            for data_object in data_objects:
                if description_name not in data_object.attributes:
                    continue

                values = data_object.attributes[description_name].values
                if DataType.is_string(data_type):
                    values = filter(lambda v: v not in data, values)
                data.extend(values)

            data_description = DataDescription(
                data_type=data_type,
                data=data if not DataType.is_string(data_type) else list(data),
                key_name=description_name,
                label=DataDescription.get_label_from_description(description_name)
            )

        return data_description

    @staticmethod
    def generate_from_values_and_scheme(values, schemes, description_name, values_to_add=None):
        """
        Generates a data description from values and a scheme from a sql query..

        :param values: All values of an sql query.
        :type values: list[list[list[object]]]
        :param schemes: The scheme for the values of a sql query.
        :type schemes: list[list[tuple[str, DataType]]
        :param description_name: The name/key for this description that should be created.
        :type description_name: str
        :param values_to_add: A list of values that should be added.
        :type values_to_add: list
        :return: The newly created data description.
        :rtype: DataDescription
        """
        values_to_add = values_to_add or []

        data = []
        data_type = None
        for index, scheme in enumerate(schemes):
            if description_name not in [s[0] for s in scheme]:
                return None

            data_index = [i for i in range(len(scheme)) if scheme[i][0] == description_name][0]
            data_type = scheme[data_index][1]
            data.extend([v[data_index] for v in values[index]])

        data.extend(values_to_add)
        data_description = DataDescription(
            data_type=data_type,
            data=list(set(data)) if DataType.is_string(data_type) else data,
            label=DataDescription.get_label_from_description(description_name),
            key_name=description_name
        )

        return data_description

    @staticmethod
    def get_label_from_description(description_name):
        # ToDo due to the overly used '_', we cannot distinguish type from attribute
        # e.g., ('crime_type_name' => a_b + c or a + b_c)
        split_str = description_name.rsplit('_', 1)
        return T.tl(split_str[0] if split_str[0] != "crimes" else "count", lang=config_app.default_language)
