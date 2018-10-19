from data_models.data_enums import DataType


class Attribute(object):
    def __init__(self, data_name, data_type, values):
        """
        :param data_name: The name of this data object.
        :type data_name: str
        :param data_type: The type for this data.
        :type data_type: DataType
        :param values: The data that this object represents.
        :type values: list[object]
        """
        self.__data_name = data_name
        self.__data_type = data_type
        self.__values = values

    def __repr__(self):
        return "A({},{}:{})".format(self.__data_name, self.__data_type, self.__values)

    def __add__(self, other):
        """
        Attributes can only be added if the have the same data_name and data_type.

        :type other: Attribute
        :rtype: Attribute
        """
        if self.__data_name != other.data_name and self.__data_type != other.data_type:
            raise AttributeError("If Attribute's should be added together, they need to have the same name and type.")

        if self.__data_type is DataType.String:
            values = list(self.__values)
            values.extend([v for v in other.values if v not in values])
            values = values
        else:
            values = list(self.__values) + other.values

        return Attribute(
            data_name=self.__data_name,
            data_type=self.__data_type,
            values=values
        )

    @property
    def data_name(self):
        """
        :rtype: str
        """
        return self.__data_name

    @property
    def data_type(self):
        """
        :rtype: DataType
        """
        return self.__data_type

    @property
    def values(self):
        """
        :rtype: list[object]
        """
        return self.__values

    def make_distinct(self):
        """
        Make the values in this attribute distinct.
        """
        values = []
        for value in self.__values:
            if value in values:
                continue
            values.append(value)
        self.__values = values

    def copy(self):
        """
        Copy this attribute.

        :return: The copy.
        :rtype: Attribute
        """
        return Attribute(
            data_name=self.__data_name,
            data_type=self.__data_type,
            values=self.__values[:]
        )
