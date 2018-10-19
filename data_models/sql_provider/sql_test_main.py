from data_models.data_object import DataObject
from data_models.sql_provider.sql_interface import SqlInterface
from data_models.sql_provider.sql_interface_generic import SqlInterfaceGeneric, WhereClauseTypes
from examples.data.sql_crime_data import table_name_to_query


def sql_generic_test():
    sql = SqlInterfaceGeneric(
            sql_db_path="../../../crime-data-sqlite/balitmore_crime_db.sdb",
            table_mapper_method=table_name_to_query
        )
    print sql.get_number_of_objects_from(
        table_name="crimes",
        column_names=["day", "month"],
        where_clause_types=[WhereClauseTypes.Is, WhereClauseTypes.Is],
        compare_values=[[15], [7]]
    )
    print sql.get_object_ids_from(
        table_name="crimes",
        column_names=["day", "month"],
        where_clause_types=[WhereClauseTypes.Is, WhereClauseTypes.Is],
        compare_values=[[15], [7]]
    )[:40]
    test = sql.get_objects_with_id_from_table(
        table_name="crimes",
        ids=range(20),
        column_names=["weapon_id", "premise_id"]
    )
    print test
    print sql.get_objects_with_id_from_table(
        table_name="weapons",
        ids=[o[0] for o in filter(lambda ob: ob[0], test[0])],
        column_names=["name"]
    )
    print sql.get_objects_with_id_from_tables(
        table_names=["crimes", "weapons"],
        ids=range(20),
        column_names=["day", "month", "weapon_id", "weapons.name"]
    )


def sql_test():
    sql = SqlInterface(
        sql_db_path="../../../crime-data-sqlite/balitmore_crime_db.sdb",
        table_mapper_method=table_name_to_query,
        query_file="../../examples/e_data/crime_data.queries"
    )

    for query_name in sql.query_names:
        values, scheme = sql.get_query_results(query_name)
        data_objects = DataObject.generate_from_sql_results(values, scheme)
        print len(data_objects), data_objects


if __name__ == '__main__':
    # sql_generic_test()
    sql_test()
