import os.path
import string
import csv
import datetime


def get_data_from_csv_file(filename, with_settings=False):
    """
    Creates a new dict from the given files.

    :param filename: The file for the data. It should be a .csv file.
    :type filename: str
    :param with_settings: Is there a *.setting file in the same folder to use it for the data?
    :type with_settings: bool
    :return: Returns two elements. First is the list of all keys with there data range, the second is the list of all data with there corresponding keys.
    :rtype: tuple[dict[string, list[object]], list[dict[string, object]]]
    """
    if not os.path.isfile(filename + '.csv'):
        raise Exception("There is no " + filename + ".csv to be create the data from.")
    if with_settings:
        if not os.path.isfile(filename + ".setting"):
            raise Exception("There is no " + filename + ".setting file to use.")

    # Read the settings if a file is given.
    settings = {}
    if with_settings:
        pre_settings = __get_settings(file_name=filename + '.setting')
        for index, values in pre_settings.iteritems():
            for value in values:
                settings[value] = index

    data = []
    keys = {}
    # Fill the map with the data from the file.
    with open(filename + '.csv', 'rb') as file_csv:
        csv_reader = csv.reader(file_csv, delimiter=",")

        # Get the first row with all names for the columns
        header = csv_reader.next()
        for prop in header:
            if prop in settings:
                if settings[prop] == 'float' or settings[prop] == 'int':
                    keys[prop] = [float('inf'), float('-inf')]
                elif settings[prop] == 'date' or settings[prop] == 'time':
                    keys[prop] = [datetime.datetime.max, datetime.datetime.min]
                else:  # settings[prop] == 'string':
                    keys[prop] = set()
            else:
                keys[prop] = set()

        # Generate new points and fill them
        for row in csv_reader:
            row_data = {}
            for index, value in enumerate(row):
                prop = header[index]
                # Go through all settings and convert the values according to there type
                if prop in settings:
                    if settings[prop] == 'float':
                        # If the value is empty use a placeholder
                        converted_value = float(value) if value != "" else float("-inf")
                    elif settings[prop] == 'int':
                        # If the value is empty use a placeholder
                        converted_value = int(value) if value != "" else float("-inf")
                    elif settings[prop] == 'date':
                        # Based on this format: MM/DD/YY
                        value_split = value.split('/')
                        converted_value = datetime.datetime(int(value_split[2]), int(value_split[0]), int(value_split[1]))
                    elif settings[prop] == 'time':
                        # Based on this format: HH:MM:SS
                        value_split = value.split(':')
                        converted_value = datetime.datetime(2017, 07, 27, int(value_split[0]), int(value_split[1]), int(value_split[2]))
                    else:  # settings[prop] == 'string':
                        converted_value = str(value)
                # If there were no settings for the property leave it as it is
                else:
                    converted_value = value

                # Get the data range from the data
                if prop in settings:
                    if settings[prop] != 'string':
                        keys[prop] = [converted_value if converted_value < keys[prop][0] else keys[prop][0],
                                      converted_value if converted_value > keys[prop][1] else keys[prop][1]]
                    else:  # settings[prop] == 'string':
                        keys[prop].add(converted_value)
                else:
                    keys[prop].add(converted_value)

                row_data[prop] = converted_value
            data.append(row_data)

        # Change the type from set to list
        for prop in keys.iterkeys():
            if isinstance(keys[prop], set):
                keys[prop] = list(keys[prop])

    return keys, data


def __get_settings(file_name):
    """
    Opens the settings file associated to a csv file and returns it.

    :param file_name: The path to settings file.
    :type file_name: str
    :return: The settings.
    :rtype: dict[str, str]
    """
    settings = {}
    if not file_name.endswith('.setting'):
        file_name += '.setting'

    for line in open(name=file_name).readlines():
        # Split line by the setting name
        split = string.split(line, sep=': ')
        if not split[0] or split[0] == '\n':
            continue
        # Split the setting values by the commas and delete the new line und the spaces
        settings[split[0]] = string.split(
            string.replace(s=string.replace(s=split[1], old='\n', new=''), old=' ', new=''), ',')

    return settings
