import sqlite3

from enum import Enum

from data_models.data_enums import DataType


class WhereClauseTypes(Enum):
    Is = 0
    In = 1
    Between = 2
    Less = 3
    LessEqual = 4
    Greater = 5
    GreaterEqual = 6
    Like = 7

    @staticmethod
    def get_string_for_single_clause(column_name, where_clause_type, values, table_name=None, negation=False):
        """
        Converts a given type and values to a where clause string that can be used in sql_provider queries.

        :param column_name: The column name that should be checked with the values.
        :type column_name: str
        :param where_clause_type: The type of the where clause.
        :type where_clause_type: WhereClauseTypes
        :param values: The list of values that should be used. The values needs to fit for the corresponding where clause.
        :type values: list[]
        :param table_name: The name of the table that is used for the column names.
        :type table_name: str
        :param negation: Should the clause be negated?
        :type negation: bool
        :return: The complete where clause part for this column and its values.
        :rtype: str
        """
        if where_clause_type is WhereClauseTypes.Is:
            return "{}{}{} IS {}".format("NOT " if negation else "", (table_name + ".") if table_name else "", column_name, values[0])
        elif where_clause_type is WhereClauseTypes.In:
            return "{}{}{} IN ({})".format("NOT " if negation else "", (table_name + ".") if table_name else "", column_name, str(values)[1:][:-1])
        elif where_clause_type is WhereClauseTypes.Between:
            return "{}{}{} BETWEEN {} AND {}".format("NOT " if negation else "", (table_name + ".") if table_name else "", column_name, values[0], values[1])
        elif where_clause_type is WhereClauseTypes.Less:
            return "{}{}{} < {}".format("NOT " if negation else "", (table_name + ".") if table_name else "", column_name, values[0])
        elif where_clause_type is WhereClauseTypes.LessEqual:
            return "{}{}{} <= {}".format("NOT " if negation else "", (table_name + ".") if table_name else "", column_name, values[0])
        elif where_clause_type is WhereClauseTypes.Greater:
            return "{}{}{} > {}".format("NOT " if negation else "", (table_name + ".") if table_name else "", column_name, values[0])
        elif where_clause_type is WhereClauseTypes.GreaterEqual:
            return "{}{}{} >= {}".format("NOT " if negation else "", (table_name + ".") if table_name else "", column_name, values[0])
        elif where_clause_type is WhereClauseTypes.Like:
            return "{}{}{} LIKE {}".format("NOT " if negation else "", (table_name + ".") if table_name else "", column_name, values[0])
        else:
            return ""

    @staticmethod
    def get_string_for_multiple_clauses(column_names, where_clause_types, values, table_name=None, negations=None):
        """
        Converts a given types and values to different where clause strings that can be used in sql_provider queries.
        All four lists need to be the same length.

        :param column_names: The column names that should be checked with the values.
        :type column_names: list[str]
        :param where_clause_types: The types of the where clause.
        :type where_clause_types: list[WhereClauseTypes]
        :param values: The list of values that should be used. The values needs to fit for the corresponding where clause.
        :type values: list
        :param table_name: The name of the table that is used for the column names.
        :type table_name: str
        :param negations: Should the clause be negated?
        :type negations: list[bool]
        :return: The complete where clause part for this column and its values.
        :rtype: str
        """
        if not negations:
            negations = [False] * len(column_names)
        pairs = [WhereClauseTypes.get_string_for_single_clause(cn, wct, v, table_name, n) for cn, wct, v, n in zip(column_names, where_clause_types, values, negations)]
        return " AND ".join(pairs)


class SqlInterfaceGeneric(object):
    def __init__(self, sql_db_path, table_mapper_method):
        """
        :param sql_db_path: The path to the sql_db_path.
        :type sql_db_path: str
        :param table_mapper_method: The method that maps all the table names of the db to there corresponding PRAGMA queries.
        :type table_mapper_method: function()
        """
        self.__sql_db_path = sql_db_path
        self.__mapper = table_mapper_method
        self.__connection = sqlite3.connect(self.__sql_db_path)

        # All list have equal length all the time. All for columns.
        self.__c_names, self.__c_types, self.__c_tables, self.__tables_keys = [], [], [], {}
        self.__generate_tables_dict()

    def __generate_tables_dict(self):
        """
        Generates the tables dict of this class. It will save all tables and there corresponding columns with name and types.
        """
        cur = self.__connection.cursor()
        # Get all tables names from the database.
        query = "SELECT name FROM sqlite_master WHERE type='table'"
        cur.execute(query)
        for table_name in list(cur.fetchall()):
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
                self.__c_types.append(DataType.string_to_data_type(str(type)))
                self.__c_tables.append(table_name)

    def get_number_of_objects_from(self, table_name, column_names=None, where_clause_types=None, compare_values=None):
        """
        Get the number of all elements in the given table. All three lists need to be the same length.

        :param table_name: The name of the table to search in.
        :type table_name: str
        :param column_names: The name of the columns to compare with in the table.
        :type column_names: list[str]
        :param where_clause_types: The where clauses types used to compare the column with the values.
        :type where_clause_types: list[WhereClauseTypes]
        :param compare_values: The values to compare the columns against.
        :type compare_values: list
        :return: The number of elements in the table.
        :rtype: int
        """
        if table_name not in self.__c_tables:
            return -1

        cur = self.__connection.cursor()
        w_clause = "" if not column_names else "WHERE " + WhereClauseTypes.get_string_for_multiple_clauses(column_names, where_clause_types, compare_values)
        query = "SELECT COUNT(t.{id}) FROM {table_name} t {w_clause}".format(
            id="{}_id".format(table_name[:-1]),
            table_name=table_name,
            w_clause=w_clause
        )
        cur.execute(query)
        return cur.fetchone()[0]

    def get_object_ids_from(self, table_name, column_names=None, where_clause_types=None, compare_values=None):
        """
        Get the all elements in the given table.

        :param table_name: The name of the table to search in.
        :type table_name: str
        :param column_names: The name of the columns to compare with in the table.
        :type column_names: list[str]
        :param where_clause_types: The where clauses types used to compare the column with the values.
        :type where_clause_types: list[WhereClauseTypes]
        :param compare_values: The values to compare the columns against.
        :type compare_values: list
        :return: Two lists. The first list are all found objects. Each object is a own list with its attribute values as entries.
                 The second list is the scheme of the data of the objects. It contains a tuple with the name of the attribute and its type.
                 It has the same order as the attributes in the first list of the objects.
        :rtype: tuple[list, list[str, DataType]]
        """
        if table_name not in self.__c_tables:
            return [], []

        cur = self.__connection.cursor()
        table_id = "{}_id".format(table_name[:-1])
        w_clause = "" if not column_names else "WHERE " + WhereClauseTypes.get_string_for_multiple_clauses(column_names, where_clause_types, compare_values, "t")
        query = "SELECT t.{id} FROM {table_name} t {w_clause}".format(
            id=table_id,
            table_name=table_name,
            w_clause=w_clause
        )
        cur.execute(query)

        # TODO: Its possible that its necessary to convert all unicodes to string for future use.
        values, scheme = [[v[0]] for v in cur.fetchall()], [(table_id, self.__c_types[self.__c_names.index(table_id)])]
        return values, scheme

    def get_objects_with_id_from_table(self, table_name, ids, column_names=None):
        """
        Search for given ids all elements in the given table.

        :param table_name: The name of the table to search in.
        :type table_name: str
        :param ids: The list of all ids to search for.
        :type ids: list[int]
        :param column_names: All columns that the output should have.
        :type column_names: list[str]
        :return: Two lists. The first list are all found objects. Each object is a own list with its attribute values as entries.
                 The second list is the scheme of the data of the objects. It contains a tuple with the name of the attribute and its type.
                 It has the same order as the attributes in the first list of the objects.
        :rtype: tuple[list, list[str, DataType]]
        """
        if table_name not in self.__c_tables:
            return [], []

        cur = self.__connection.cursor()
        query = "SELECT {s_clause} FROM {table_name} WHERE {w_clause}".format(
            s_clause="*" if not column_names else ", ".join(column_names),
            table_name=table_name,
            w_clause=WhereClauseTypes.get_string_for_single_clause(
                column_name="{}_id".format(table_name[:-1]),
                where_clause_type=WhereClauseTypes.In,
                values=ids
            )
        )
        cur.execute(query)

        values, scheme = [list(v)[:(len(column_names))] for v in cur.fetchall()], [(cn, self.__c_types[self.__c_names.index(cn)]) for cn in column_names]
        return values, scheme
