import sqlite3

from data_models.data_enums import DataType


class SqlInterface(object):
    def __init__(self, sql_db_path, table_mapper_method, query_file):
        """
        :param sql_db_path: The path to the sql_db_path.
        :type sql_db_path: str
        :param table_mapper_method: The method that maps all the table names of the db to there corresponding PRAGMA queries.
        :type table_mapper_method: function()
        :param query_file: The path to the file with pre written queries to use.
        :type query_file: str
        """
        self.__sql_db_path = sql_db_path
        self.__mapper = table_mapper_method
        self.__connection = sqlite3.connect(self.__sql_db_path)

        # All list have equal length all the time. All for columns.
        self.__c_names, self.__c_types, self.__c_tables, self.__tables_keys = [], [], [], {}
        self.__generate_tables_dict()
        # Load all queries in this object.
        self.__q_names, self.__q_labels, self.__q_strings, self.__q_schemes = [], [], [], []
        self.__read_query_file(query_file=query_file)

    @property
    def query_names(self):
        """
        :rtype: list[str]
        """
        return self.__q_names

    def __generate_tables_dict(self):
        """
        Generates the tables dict of this class. It will save all tables and there corresponding columns with name and types.
        """
        cur = self.__connection.cursor()
        # Get all tables names from the database.
        query = "SELECT name FROM sqlite_master WHERE type='table'"
        cur.execute(query)
        for table_name in cur.fetchall():
            table_name = str(table_name[0])
            query = self.__mapper(table_name)
            # Only allow tables that got a query.
            if not query:
                continue
            self.__tables_keys[table_name] = "{}_id".format(table_name[:-1])
            # Get all columns of the given table.
            cur.execute(query)
            for (cid, name, type, notnull, dft_value, pk) in cur.fetchall():
                self.__c_names.append(str(name))
                if "datetime" in str(name) and "varchar" in str(type).lower():
                    type = "datetime"
                elif "weekday" in str(name) and "integer" == str(type).lower():
                    type = "weekday"
                elif "month" in str(name) and "integer" == str(type).lower():
                    type = "month"
                self.__c_types.append(DataType.string_to_data_type(str(type)))
                self.__c_tables.append(table_name)

    def __read_query_file(self, query_file):
        """
        Reads the given file with the possible queries for this sql_provider interface.

        :param query_file: The path to the query file.
        :type query_file: str
        """
        for i, line in enumerate(open(query_file).readlines()):
            i = i % 5
            # Get the name
            if i == 0:
                line = line.replace('\n', '')
                self.__q_names.append(line)
            # Get the return values for this query.
            elif i == 1:
                line = line.replace('\n', '')
                self.__q_labels.append(line)
            elif i == 2:
                line = line.replace(' ', '').replace('\n', '')
                type_strings = line.split(',')
                scheme = []
                for type_string in type_strings:
                    data_type = None
                    # Check if a data type was given in the query file.
                    try:
                        table, column, data_type = type_string.split('|')
                        data_type = DataType.string_to_data_type(data_type)
                    except ValueError:
                        table, column = type_string.split('|')

                    # If count is the column name save this.
                    if column == "count":
                        scheme.append(("_".join([table, column]), DataType.Integer))
                    else:
                        column_name = column if column != "name" else "_".join([table[:-1], column])
                        data_type = data_type if data_type else self.__c_types[zip(self.__c_tables, self.__c_names).index((table, column))]
                        scheme.append((column_name, data_type))
                self.__q_schemes.append(scheme)
            # The query itself
            elif i == 3:
                self.__q_strings.append(line)
            # No else, so that a line is empty between this and the next query.

    def get_query_results(self, query_name, encoding='utf-8'):
        """
        Generates the result of a pre written query.

        :param query_name: The name of the query that should be used.
        :type query_name: str
        :return: Two lists. The first list are all found objects. Each object is a own list with its attribute values as entries.
                 The second list is the scheme of the data of the objects. It contains a tuple with the name of the attribute and its type.
                 It has the same order as the attributes in the first list of the objects.
        :rtype: tuple[list, list[str, DataType]]
        """
        if query_name not in self.__q_names:
            return [], []

        cur = self.__connection.cursor()
        cur.execute(self.__q_strings[self.__q_names.index(query_name)])

        scheme = self.__q_schemes[self.__q_names.index(query_name)]

        all_values = []
        for v in cur.fetchall():
            values = []
            for i in range(len(scheme)):
                value = v[i]
                if isinstance(value, unicode) and encoding is not None:
                    value = value.encode(encoding)
                values.append(value)
            all_values.append(values)

        return all_values, scheme

    def get_query_label(self, query_name):
        """
        Get the label for the given query.

        :param query_name: The name of the query that should be used.
        :type query_name: str
        :return: The label for the given query.
        :rtype: str
        """
        if query_name not in self.__q_names:
            return ""
        return self.__q_labels[self.__q_names.index(query_name)]
