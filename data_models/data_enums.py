from enum import Enum


class DataType(Enum):
    """
    All variants of possible data types in a chart.
    """
    Integer = 0
    IntegerSum = 1
    Float = 2
    FloatSum = 3
    String = 4
    DateTime = 5
    Date = 6
    Time = 7
    Daytime = 8
    Count = 9
    Weekday = 10
    Day = 11
    Month = 12

    @staticmethod
    def is_number(data_type):
        return data_type in [DataType.Integer, DataType.Float, DataType.IntegerSum, DataType.FloatSum, DataType.Count]

    @staticmethod
    def is_sum(data_type):
        return data_type in [DataType.IntegerSum, DataType.FloatSum]

    @staticmethod
    def is_datetime(data_type):
        return data_type in [DataType.DateTime, DataType.Date, DataType.Time, DataType.Day]

    @staticmethod
    def is_string(data_type):
        return data_type in [DataType.String, DataType.Weekday, DataType.Daytime, DataType.Month]

    @staticmethod
    def string_to_data_type(data_type_string):
        """
        Converts a given string in a object of this enum.

        :param data_type_string: The string that represents an enum value.
        :type data_type_string: str
        :return: The data type corresponding to the string.
        :rtype: DataType
        """
        data_type_string = data_type_string.lower()
        if "integer" == data_type_string:
            return DataType.Integer
        elif "float" == data_type_string:
            return DataType.Float
        elif "varchar" in data_type_string:
            return DataType.String
        elif "datetime" == data_type_string:
            return DataType.DateTime
        elif "time" == data_type_string:
            return DataType.Time
        elif "date" == data_type_string:
            return DataType.Date
        elif "weekday" == data_type_string:
            return DataType.Weekday
        elif "month" == data_type_string:
            return DataType.Month
        elif "daytime" == data_type_string:
            return DataType.Daytime
        elif "string" == data_type_string:
            return DataType.String
        elif "day" == data_type_string:
            return DataType.Day

    @staticmethod
    def int_to_weekday(weekday):
        """
        Converts a given int to a weekday.

        :param weekday: The int of the weekday. 0 is Monday.
        :type weekday: int
        :return: The string for the weekday.
        :rtype: str
        """
        if not 0 <= weekday <= 6:
            return ""
        return ["Mon.", "Tue.", "Wed.", "Thu.", "Fri.", "Sat.", "Sun."][weekday]

    @staticmethod
    def int_to_month(month):
        """
        Converts a given int to a month.

        :param month: The int of the weekday. 1 is January.
        :type month: int
        :return: The string for the month.
        :rtype: str
        """
        if not 1 <= month <= 12:
            return ""
        return ["Jan.", "Feb.", "Mar.", "Apr.", "May", "Jun.", "Jul.", "Aug.", "Sept.", "Oct.", "Nov.", "Dec."][month - 1]

    @staticmethod
    def int_to_daytime(daytime):
        """
        Converts a given int to a daytime.

        :param daytime: The int of the weekday. 0 is Morning.
        :type daytime: int
        :return: The string for the daytime.
        :rtype: str
        """
        if not 0 <= daytime <= 3:
            return ""
        return ["Night", "Morning", "Afternoon", "Evening"][daytime]


class DataSelectionState(Enum):
    """
    Which state has a data object.
    """
    Nothing = 0,
    Selected = 1,
    Highlighted = 2


class ListAction(Enum):
    removed = 0,
    added = 1,
    moved = 2,
