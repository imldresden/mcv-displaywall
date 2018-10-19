def table_name_to_query(table_name):
    """
    Maps the given table to a complete query to get all the columns in this table. (PRAGMA)

    :param table_name:
    :type table_name: str
    :return: The query for the PRAGMA for the given table.
    :rtype: str
    """
    if table_name == "crime_codes":
        return "PRAGMA table_info(crime_codes)"
    elif table_name == "crime_types":
        return "PRAGMA table_info(crime_types)"
    elif table_name == "crimes":
        return "PRAGMA table_info(crimes)"
    elif table_name == "districts":
        return "PRAGMA table_info(districts)"
    elif table_name == "locations":
        return "PRAGMA table_info(locations)"
    elif table_name == "neighborhoods":
        return "PRAGMA table_info(neighborhoods)"
    elif table_name == "premises":
        return "PRAGMA table_info(premises)"
    elif table_name == "streets":
        return "PRAGMA table_info(streets)"
    elif table_name == "weapons":
        return "PRAGMA table_info(weapons)"
    else:
        return None
