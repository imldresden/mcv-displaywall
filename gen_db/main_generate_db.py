#!/usr/bin/python

import os
import csv
import re
import time
import math
import datetime
import sqlite3
import googlemaps
import pickle
import shutil
import sys
import getopt
import random
import string

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)
from divico_ctrl.translation import T
from configs.config_app import default_language as LANG

class SimpleType(object):
    DB_TRANSACTION_BATCH_SIZE = 100000

    def __init__(self):
        self.idx_dict = {}
        self.attr_dict = {}

    def exists(self, name):
        return name in self.idx_dict

    def insert(self, name, attr):
        if self.exists(name):
            return self.idx_dict[name]

        index = len(self.idx_dict)
        self.idx_dict[name] = index
        self.attr_dict[name] = attr
        return index

    def save_in_database(self, connection, table_name):
        qry = 'INSERT OR IGNORE INTO {!s} VALUES (?, ?)'.format(
            table_name
        )

        cursor = connection.cursor()
        for name, idx in self.idx_dict.iteritems():
            cursor.execute(qry, [idx, name])
            if idx % SimpleType.DB_TRANSACTION_BATCH_SIZE == 0:
                connection.commit()
        connection.commit()


class CrimeCodes(SimpleType):
    def __init__(self):
        super(CrimeCodes, self).__init__()

    def insert(self, name, desc):
        return super(CrimeCodes, self).insert(
            name=name,
            attr={
                "desc": desc
            }
        )

    def save_in_database(self, connection, table_name):
        qry = 'INSERT OR IGNORE INTO {!s} VALUES (?, ?, ?)'.format(
            table_name
        )

        cursor = connection.cursor()
        for name, idx in self.idx_dict.iteritems():
            desc = self.attr_dict[name]['desc']
            cursor.execute(qry, [idx, name, desc])
            if idx % SimpleType.DB_TRANSACTION_BATCH_SIZE == 0:
                connection.commit()
        connection.commit()


class Weapons(SimpleType):
    def __init__(self):
        super(Weapons, self).__init__()

    def insert(self, name):
        label = T.tl(msg=name, lang=LANG)
        return super(Weapons, self).insert(
            name=name,
            attr={
                'label': label
            }
        )

    def save_in_database(self, connection, table_name):
        qry = 'INSERT OR IGNORE INTO {!s} VALUES (?, ?, ?)'.format(
            table_name
        )

        cursor = connection.cursor()
        for name, idx in self.idx_dict.iteritems():
            label = self.attr_dict[name]['label']
            cursor.execute(qry, [idx, name, label])
            if idx % SimpleType.DB_TRANSACTION_BATCH_SIZE == 0:
                connection.commit()
        connection.commit()


class Premises(SimpleType):
    def __init__(self):
        super(Premises, self).__init__()

    def insert(self, name):
        label = T.tl(msg=name, lang=LANG)
        return super(Premises, self).insert(
            name=name,
            attr={
                'label': label
            }
        )

    def save_in_database(self, connection, table_name):
        qry = 'INSERT OR IGNORE INTO {!s} VALUES (?, ?, ?)'.format(
            table_name
        )

        cursor = connection.cursor()
        for name, idx in self.idx_dict.iteritems():
            label = self.attr_dict[name]['label']
            cursor.execute(qry, [idx, name, label])
            if idx % SimpleType.DB_TRANSACTION_BATCH_SIZE == 0:
                connection.commit()
        connection.commit()


class CrimeTypes(SimpleType):
    def __init__(self):
        super(CrimeTypes, self).__init__()

    def insert(self, name):
        label = T.tl(msg=name, lang=LANG)
        return super(CrimeTypes, self).insert(
            name=name,
            attr={
                'label': label
            }
        )

    def save_in_database(self, connection, table_name):
        qry = 'INSERT OR IGNORE INTO {!s} VALUES (?, ?, ?)'.format(
            table_name
        )

        cursor = connection.cursor()
        for name, idx in self.idx_dict.iteritems():
            label = self.attr_dict[name]['label']
            cursor.execute(qry, [idx, name, label])
            if idx % SimpleType.DB_TRANSACTION_BATCH_SIZE == 0:
                connection.commit()
        connection.commit()


class Districts(SimpleType):
    SHORT_NAMES = {
        'NORTHEASTERN': 'NE',
        'EASTERN': 'E',
        'SOUTHERN': 'S',
        'SOUTHWESTERN': 'SW',
        'SOUTHEASTERN': 'SE',
        'CENTRAL': 'C',
        'NORTHWESTERN': 'NW',
        'WESTERN': 'W',
        'NORTHERN': 'N'
    }

    def __init__(self):
        super(Districts, self).__init__()

    def insert(self, name, lat, lng):
        short_name = Districts.SHORT_NAMES.get(name, None)
        label = T.tl(msg=name, lang=LANG)
        short_label = T.tl(msg=short_name, lang=LANG)
        return super(Districts, self).insert(
            name=name,
            attr={
                'lat': lat,
                'lng': lng,
                'short_name': short_name,
                'label': label,
                'short_label': short_label
            }
        )

    def save_in_database(self, connection, table_name):
        qry = 'INSERT OR IGNORE INTO {!s} VALUES (?, ?, ?, ?, ?, ?, ?)'.format(
            table_name
        )

        cursor = connection.cursor()
        for name, idx in self.idx_dict.iteritems():
            lat = self.attr_dict[name]['lat']
            lng = self.attr_dict[name]['lng']
            short_name = self.attr_dict[name]['short_name']
            label = self.attr_dict[name]['label']
            short_label = self.attr_dict[name]['short_label']
            cursor.execute(
                qry, [idx, name, lat, lng, short_name, label, short_label]
            )
            if idx % SimpleType.DB_TRANSACTION_BATCH_SIZE == 0:
                connection.commit()
        connection.commit()


class Neighbors(SimpleType):
    def __init__(self):
        super(Neighbors, self).__init__()

    def insert(self, name, lat, lng):
        return super(Neighbors, self).insert(
            name=name,
            attr={
                'lat': lat,
                'lng': lng
            }
        )

    def save_in_database(self, connection, table_name):
        qry = 'INSERT OR IGNORE INTO {!s} VALUES (?, ?, ?, ?)'.format(
            table_name
        )

        cursor = connection.cursor()
        for name, idx in self.idx_dict.iteritems():
            lat = self.attr_dict[name]['lat']
            lng = self.attr_dict[name]['lng']
            cursor.execute(qry, [idx, name, lat, lng])
            if idx % SimpleType.DB_TRANSACTION_BATCH_SIZE == 0:
                connection.commit()
        connection.commit()


class Locations(SimpleType):
    def __init__(self):
        super(Locations, self).__init__()
        self.__paras = {}

    def insert(self, address, district, neighbor, street, postal,
               house, lat, lng):
        return super(Locations, self).insert(
            name=address,
            attr={
                'district': district,
                'neighbor': neighbor,
                'street': street,
                'postal': postal,
                'house': house,
                'lat': lat,
                'lng': lng,
                'address': address
            }
        )

    def save_in_database(self, connection, table_name):
        qry = 'INSERT OR IGNORE INTO {!s} ' \
              'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)'.format(
                  table_name
              )

        cursor = connection.cursor()
        for name, idx in self.idx_dict.iteritems():
            district = self.attr_dict[name]['district']
            neighbor = self.attr_dict[name]['neighbor']
            street = self.attr_dict[name]['street']
            postal = self.attr_dict[name]['postal']
            house = self.attr_dict[name]['house']
            lat = self.attr_dict[name]['lat']
            lng = self.attr_dict[name]['lng']
            cursor.execute(qry, [idx, district, neighbor, street, postal, house,
                                 lat, lng, name])
            if idx % SimpleType.DB_TRANSACTION_BATCH_SIZE == 0:
                connection.commit()
        connection.commit()


class Crimes(object):
    def __init__(self):
        self.__data = []

    def insert(
            self, line_in_csv, datetime, inside, location, crime_code,
            crime_type, weapon, premise, incidents, year, month, day, hour,
            minute, seconds, weekday, daytime, week):
        key = len(self.__data)
        self.__data.append({
                'line_in_csv': line_in_csv,
                'datetime': datetime,
                'inside': inside,
                'location': location,
                'crime_code': crime_code,
                'crime_type': crime_type,
                'weapon': weapon,
                'premise': premise,
                'incidents': incidents,
                'year': year,
                'month': month,
                'day': day,
                'hour': hour,
                'minute': minute,
                'seconds': seconds,
                'weekday': weekday,
                'daytime': daytime,
                'week': week
        })
        return key

    def save_in_database(self, connection, table_name):
        qry = 'INSERT OR IGNORE INTO {!s} ' \
              'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ' \
              '?, ?, ?, ?, ?, ?, ?, ?, ?)'.format(
                  table_name
              )

        cursor = connection.cursor()
        for i in range(len(self.__data)):
            cursor.execute(qry, [
                i,
                self.__data[i]['line_in_csv'],
                self.__data[i]['datetime'],
                self.__data[i]['inside'],
                self.__data[i]['location'],
                self.__data[i]['crime_code'],
                self.__data[i]['crime_type'],
                self.__data[i]['weapon'],
                self.__data[i]['premise'],
                self.__data[i]['incidents'],
                self.__data[i]['year'],
                self.__data[i]['month'],
                self.__data[i]['day'],
                self.__data[i]['hour'],
                self.__data[i]['minute'],
                self.__data[i]['seconds'],
                self.__data[i]['weekday'],
                self.__data[i]['daytime'],
                self.__data[i]['week']
            ])
            if i % SimpleType.DB_TRANSACTION_BATCH_SIZE == 0:
                connection.commit()
        connection.commit()


class Geocoder(object):
    def __init__(self, cache_file, api_key):
        self._cache_file = cache_file
        self._api_key = api_key

        self.gmaps = None
        self.responses = None

        try:
            with open(self._cache_file, 'rb') as f:
                self.responses = pickle.load(f)
            print 'Found and loaded existing Google geocode responses!'
        except IOError:
            self.responses = {}
            print 'No existing Google geocode responses found!'

    def __del__(self):
        try:
            with open(self._cache_file, 'wb') as f:
                pickle.dump(self.responses, f, 0)
            print 'Saved google geocode responses locally!'
        except IOError:
            print 'Error: Failed to save google geocode responses locally!'

    def load_google_maps(self):
        if self.gmaps:
            return
        self.gmaps = googlemaps.Client(self._api_key)

    def geocode(self, search_str):
        if search_str in self.responses.keys():
            return self.responses[search_str]
        else:
            print 'Geocode search string = {!s}'.format(search_str)
            self.load_google_maps()
            geocode_result = self.gmaps.geocode(search_str)
            self.responses[search_str] = geocode_result
            return geocode_result


class BaltimoreCrimesLoader(object):
    def __init__(self, source_csv_file, db_filename, db_schema_file,
                 geocoding_cache_file, geocoding_api_key, skip_entries_years):
        self._source_csv_file = source_csv_file
        self._db_filename = db_filename
        self._db_schema_file = db_schema_file
        self._skip_entries_years = []
        for year in skip_entries_years:
            self._skip_entries_years.append(str(year))
        self._googlemaps = Geocoder(
            cache_file=geocoding_cache_file,
            api_key=geocoding_api_key
        )

        self._crime_codes = CrimeCodes()
        self._weapons = Weapons()
        self._premises = Premises()
        self._crime_types = CrimeTypes()
        self._streets = SimpleType()
        self._districts = Districts()
        self._neighbors = Neighbors()
        self._locations = Locations()
        self._crimes = Crimes()

    def _remove_old_database(self):
        try:
            if os.path.isfile(self._db_filename):
                split_filen = os.path.splitext(self._db_filename)
                backup_file = split_filen[0] + '__BAK__' + split_filen[1]
                if os.path.isfile(backup_file):
                    os.remove(backup_file)
                shutil.copy2(self._db_filename, backup_file)
                os.remove(self._db_filename)
                print 'Existing database <{!s}> backuped as <{!s}>!'.format(
                    self._db_filename, backup_file)
        except OSError:
            print 'No existing database <{!s}> found!'.format(self._db_filename)

    def load_data_into_memory(self):
        manual_neighbors = {
            "Locust Point Industrial A": [39.263666, -76.588621],
            "Pimlico Good Neighbors": [39.353143, -76.678128],
            "Curtis Bay Industrial Are": [39.220866, -76.586395],
            "Ellwood Park / Monument": [39.296320, -76.574540],
            "Ellwood Park/Monument": [39.296320, -76.574540],
            "Glenham - Belhar": [39.350204, -76.549603],
            "Glenham-Belhar": [39.350204, -76.549603],
            "Hamilton Hills": [39.350267, -76.550192],
            "Coldstream Homestead Mont": [39.322119, -76.596029],
            "York - Homeland": [39.353128, -76.611055],
            "York-Homeland": [39.353128, -76.611055],
            "Concerned Citizens Of For": [39.323228, -76.683585],
            "Panway / Braddish Avenue": [39.313008, -76.662923],
            "Panway/Braddish Avenue": [39.313008, -76.662923],
            "Blythewood": [39.350726, -76.625777],
            "Lower Herring Run Park": [39.315354, -76.549720],
            "Evesham Park": [39.364919, -76.605988],
            "Carroll - Camden Industri": [39.283686, -76.667409],
            "Carroll-South Hilton": [39.283686, -76.667409],
            "Lower Edmondson Village": [39.296413, -76.680456],
            "Fairfield Area": [39.237704, -76.581329],
            "Coppin Heights / Ash - Co - Eas": [39.307752, -76.657505],
            "Coppin Heights/Ash-Co-Eas": [39.307752, -76.657505],
            "Rosemont Homeowners / Tenan": [39.304480, -76.670238],
            "Rosemont Homeowners/Tenan": [39.304480, -76.670238],
            "Villages Of Homeland": [39.363680, -76.616413],
            "Canton Industrial Area": [39.282195, -76.575505],
            "Wakefield": [39.312590, -76.698092],
            "Towanda - Grantley": [39.330290, -76.662707],
            "Wrenlane": [39.330941, -76.617437],
            "Orangeville Industrial Ar": [39.304863, -76.563546],
            "Middle Branch / Reedbird Pa": [39.251602, -76.618919],
            "Middle Branch/Reedbird Pa": [39.251602, -76.618919],
            "Parkview/Woodbrook": [39.315924, -76.647019]
        }

        manual_premises = {
            "Alley": "ALLEY",
            "APT/CONDO":  "APARTMENTS/CONDOS",
            "AUTO PARTS": "AUTO PARTS WAREHOUSE",
            "BANK/FINAN": "BANK/FINANCIAL",
            "BARBER/BEA": "BARBER/BEAUTY SALON",
            "BUS. PARK":  "BUS PARKING",
            "BUS/RAILRO": "BUS/RAILROAD",
            "CAR  REPAI": "CAR REPAIR SHOP",
            "CAR LOT-NE": "PARKING LOT",
            "CARRY OUT":  "CARRY OUT FOOD",
            "CHAIN FOOD": "CHAIN FOOD STORE",
            "CLOTHING/S": "CLOTHING/SHOP",
            "CONVENIENC": "CONVENIENCE STORE",
            "COURT HOUS": "COURT HOUSE",
            "DOCTORS OF": "DOCTORS OFFICE",
            "GARAGE ON":  "GARAGE",
            "GAS STATIO": "GAS STATION",
            "GROCERY/CO": "GROCERY/CONSUMER MARKET",
            "FAST FOOD":  "FAST FOOD RESTAURANT",
            "HOSP/NURS.": "HOSPITAL",
            "HOTEL/MOTE": "HOTEL/MOTEL",
            "LAUNDRY/CL": "LAUNDRY/CLEANERS",
            "LIQUOR STO": "LIQUOR STORE",
            "MARKET STA": "MARKET STALL",
            "OFFICE BUI": "OFFICE BUILDING",
            "OTHER - IN": "OTHER - INSIDE",
            "OTHER - OU": "OTHER - OUTSIDE",
            "OTHER/RESI": "OTHER - RESIDENCE",
            "PARKING LO": "PARKING LOT",
            "PUBLIC ARE": "PUBLIC AREA",
            "PUBLIC BUI": "PUBLIC BUILDING",
            "RETAIL/SMA": "RETAIL/SMALL BUSINESS",
            "ROW/TOWNHO": "ROW HOME/TOWNHOUSE",
            "SHED/GARAG": "SHED / GARAGE",
            "SHOPPING M": "SHOPPING MALL",
            "SINGLE HOU": "SINGLE HOUSE",
            "VACANT BUI": "VACANT BUILDING",
            "WHOLESALE/": "WHOLESALE",
            "YARD/BUSIN": "YARD/BUSINESS",
            "Dwelling":   "DWELLING",
            "Hospital":   "HOSPITAL",
            "Parking Lo": "PARKING LOT",
            "Public Are": "PUBLIC AREA",
            "Street":     "STREET",
            "Vehicle":    "VEHICLE",
            "PIZZA/OTHE": "PIZZA/OTHER FAST FOOD",
            "TRACTOR TR": "TRACTOR TRAILER",
            "POLICE DEP": "POLICE DEPARTMENT",
            "POOL/BOWLI": "POOL/BOWLING",
            "INNER HARB": "INNER HARBOR",
            "BUS.  STOR": "BUS STORAGE",
            "TAVERN/NIG": "TAVERN/NIGHT CLUB",
            "MINI STORA": "MINI STORAGE",
            "HOUSE UNDE": "HOUSE UNDER CONSTRUCTION",
            "CONSTRUCTI": "CONSTRUCTION SITE"
        }

        line_in_src_csv = 2
        start_time = time.time()
        last_batch_time = start_time
        total_line_count = sum(1 for line in open(self._source_csv_file))

        with open(self._source_csv_file, 'rb') as fin:
            print 'Start loading data into memory ...'
            reader = csv.DictReader(fin)
            for row in reader:
                # print row
                date_str = row['CrimeDate']
                date_parts = re.match(r'([0-9]{2})\/([0-9]{2})\/([0-9]{4})',
                                      date_str)
                day = date_parts.group(2)
                month = date_parts.group(1)
                year = date_parts.group(3)

                time_str = row['CrimeTime']
                time_parts = re.match(r'([0-9]{2}):([0-9]{2}):([0-9]{2})',
                                      time_str)
                hour = time_parts.group(1)
                hour = hour if hour != '24' else '00'
                daytime = int(math.floor(int(hour) / 6))
                minute = time_parts.group(2)
                seconds = time_parts.group(3)
                weekday = datetime.datetime(int(year), int(month),
                                            int(day)).weekday()
                # Necessary to make Monday the first element (the 0)
                weekday = (weekday - 1) % 7
                week = datetime.datetime(int(year), int(month),
                                            int(day)).isocalendar()[1]

                date_time = "{}-{}-{} {}:{}:{}".format(year, month, day,
                                                       hour, minute, seconds)

                lat_lng_str = row['Location 1']
                lat = ''
                lng = ''
                if lat_lng_str:
                    # lat_lng_parts=re.match(r'.([0-9\.]{*}),'
                    #                        r'([0-9\.]*).',
                    #                        lat_lng_str)
                    lat_lng_parts = re.match(r'.([0-9\.\-]*), ([0-9\.\-]*)',
                                             lat_lng_str)
                    lat = lat_lng_parts.group(1)
                    lng = lat_lng_parts.group(2)

                neighbor = row['Neighborhood']
                neighbor_lat = None
                neighbor_lng = None
                if neighbor:
                    geocode_result = self._googlemaps.geocode(
                        str(neighbor) +
                        ' neighborhood, Baltimore, Maryland, USA'
                    )
                    if len(geocode_result) > 0:
                        neighbor_lat =\
                            geocode_result[0]['geometry']['location']['lat']
                        neighbor_lng =\
                            geocode_result[0]['geometry']['location']['lng']
                    elif neighbor in manual_neighbors:
                            neighbor_lat = manual_neighbors[neighbor][0]
                            neighbor_lng = manual_neighbors[neighbor][1]

                inside = row['Inside/Outside']
                total_incidents = row['Total Incidents']

                crime_code = row['CrimeCode']
                crime_code_desc = row['Description']

                post = row['Post']

                district = row['District']
                district_lat = None
                district_lng = None
                if district:
                    geocode_result = self._googlemaps.geocode(
                        str(district) +
                        ' district, Baltimore, Maryland, USA'
                    )
                    if len(geocode_result) > 0:
                        district_lat = \
                            geocode_result[0]['geometry']['location']['lat']
                        district_lng = \
                            geocode_result[0]['geometry']['location']['lng']

                weapon = row['Weapon']
                weapon = weapon if weapon != "" else "UNKNOWN"

                premise = row['Premise']
                premise = premise if premise != "" else "UNKNOWN"
                if premise in manual_premises:
                    premise = manual_premises[premise]

                street_long = row['Location']
                house_number = ''
                street_name = ''
                if street_long:
                    street_parts = re.match(r'([0-9]*) ?([a-zA-Z0-9\-\&\+ ]+)',
                                            street_long)
                    house_number = street_parts.group(1)
                    street_name = street_parts.group(2)

                # continue if the year is 2017
                if str(year) in self._skip_entries_years:
                    continue

                # save all the values for the sql queries
                neighbor_key = ''
                if neighbor:
                    neighbor_key = self._neighbors.insert(
                        name=neighbor,
                        lat=neighbor_lat,
                        lng=neighbor_lng
                    )

                crime_code_key = ''
                if crime_code:
                    crime_code_key = self._crime_codes.insert(
                        name=crime_code,
                        desc=crime_code_desc
                    )

                crime_type_key = ''
                if crime_code_desc:
                    crime_type_key = self._crime_types.insert(
                        name=crime_code_desc
                    )

                district_key = ''
                if district:
                    district_key = self._districts.insert(
                        name=district,
                        lat=district_lat,
                        lng=district_lng
                    )

                weapon_key = ''
                if weapon:
                    weapon_key = self._weapons.insert(name=weapon)

                premise_key = ''
                if premise:
                    premise_key = self._premises.insert(name=premise)

                street_key = ''
                if street_name:
                    street_key = self._streets.insert(name=street_name, attr={})

                location_key = self._locations.insert(
                    address=street_long,
                    district=district_key,
                    neighbor=neighbor_key,
                    street=street_key,
                    postal=post,
                    house=house_number,
                    lat=lat,
                    lng=lng
                )

                crime_key = self._crimes.insert(
                    line_in_csv=line_in_src_csv,
                    datetime=date_time,
                    inside=inside,
                    location=location_key,
                    crime_code=crime_code_key,
                    crime_type=crime_type_key,
                    weapon=weapon_key,
                    premise=premise_key,
                    incidents=total_incidents,
                    year=year,
                    month=month,
                    day=day,
                    hour=hour,
                    minute=minute,
                    seconds=seconds,
                    weekday=weekday,
                    daytime=daytime,
                    week=week
                )
                line_in_src_csv += 1

                if line_in_src_csv % 25000 == 0:
                    mid_time = time.time()
                    elapsed = mid_time - start_time
                    elapsed_minutes = elapsed / 60
                    est_factor = total_line_count / float(line_in_src_csv)
                    est_duration = est_factor * elapsed
                    est_duration_minutes = est_duration / 60
                    delta = mid_time - last_batch_time
                    delta_minutes = delta / 60
                    perc = 100 * line_in_src_csv / total_line_count
                    msg = "\tParsed line {} ({:.2f}%, "\
                          "time elapsed {:.2f} minutes, " \
                          "delta time {:.2f} minutes, " \
                          "estimated duration {:.2f} minutes)"
                    print msg.format(line_in_src_csv, perc, elapsed_minutes,
                                     delta_minutes, est_duration_minutes)
                    last_batch_time = mid_time

            print 'Data loading complete!'

    def _create_database_schema(self, connection):
        print "Start creating database schema ..."

        query = open(self._db_schema_file, 'r').read()
        query = query.replace('balitmore_crime_db.sdb', self._db_filename)
        cursor = connection.cursor()
        # cursor.execute('PRAGMA journal_mode=MEMORY;')
        # cursor.execute('PRAGMA synchronous=OFF;')
        # cursor.execute('PRAGMA temp_store=MEMORY;')
        cursor.execute('PRAGMA encoding="UTF-8";')
        cursor.executescript(query)
        connection.commit()
        cursor.close()

        print "Database schema created!"

    def save_data_in_database(self):
        self._remove_old_database()

        connection = sqlite3.connect(self._db_filename)
        connection.text_factory = str
        print "Created and opened database successfully"

        self._create_database_schema(connection=connection)

        start_time = time.time()
        current_time = start_time
        last_batch_time = current_time
        print "Start saving data in the database ..."

        self._streets.save_in_database(connection=connection,
                                       table_name='streets')
        current_time = time.time()
        print "\tSaved streets ({:.2f}s) ...".format(
            current_time - last_batch_time
        )
        last_batch_time = current_time

        self._districts.save_in_database(connection=connection,
                                         table_name='districts')
        current_time = time.time()
        print "\tSaved districts ({:.2f}s) ...".format(
            current_time - last_batch_time
        )
        last_batch_time = current_time

        self._neighbors.save_in_database(connection=connection,
                                         table_name='neighborhoods')
        current_time = time.time()
        print "\tSaved neighborhoods ({:.2f}s) ...".format(
            current_time - last_batch_time
        )
        last_batch_time = current_time

        self._crime_codes.save_in_database(connection=connection,
                                           table_name='crime_codes')
        current_time = time.time()
        print "\tSaved crime codes ({:.2f}s) ...".format(
            time.time() - last_batch_time
        )
        last_batch_time = current_time

        self._weapons.save_in_database(connection=connection,
                                       table_name='weapons')
        current_time = time.time()
        print "\tSaved weapons ({:.2f}s) ...".format(
            current_time - last_batch_time
        )
        last_batch_time = current_time

        self._premises.save_in_database(connection=connection,
                                        table_name='premises')
        current_time = time.time()
        print "\tSaved premises ...".format(
            current_time - last_batch_time
        )
        last_batch_time = current_time

        self._crime_types.save_in_database(connection=connection,
                                           table_name='crime_types')
        current_time = time.time()
        print "\tSaved crime types ({:.2f}s) ...".format(
            time.time() - last_batch_time
        )
        last_batch_time = current_time

        self._locations.save_in_database(connection=connection,
                                         table_name='locations')
        current_time = time.time()
        print "\tSaved locations ({:.2f}s) ...".format(
            current_time - last_batch_time
        )
        last_batch_time = current_time

        self._crimes.save_in_database(connection=connection,
                                      table_name='crimes')
        current_time = time.time()
        print "\tSaved crimes ({:.2f}s) ...".format(
            current_time - last_batch_time
        )

        current_time = time.time()
        print "Finished saving all data in the database! "\
              "(duration {:.2f}s)".format(current_time - start_time)


class FakeDataGenerator(object):
    LIST_OF_DISTRICTS = ['NORTHEASTERN', 'EASTERN', 'SOUTHEASTERN',
                        'NORTHWESTERN', 'NORTHERN', 'SOUTHWESTERN',
                        'WESTERN', 'SOUTHERN', 'CENTRAL']

    LIST_OF_NEIGHBORS = [
        "Darley Park",
        "CARE",
        "Canton",
        "Central Park Heights",
        "Kenilworth Park",
        "Irvington",
        "Woodbourne Heights",
        "Charles Village",
        "Belair - Edison",
        "Patterson Park Neighborho",
        "Central Forest Park",
        "Penn North",
        "Cherry Hill",
        "Harlem Park",
        "West Forest Park",
        "Bridgeview / Greenlawn",
        "Bayview",
        "Curtis Bay",
        "Better Waverly",
        "Hollins Market",
        "Pulaski Industrial Area",
        "Uplands",
        "Concerned Citizens Of For",
        "Middle East",
        "Millhill",
        "Washington Village / Pigtow",
        "Waverly",
        "Rosemont",
        "Inner Harbor",
        "Westport",
        "Rognel Heights",
        "Edgewood",
        "West Arlington",
        "Downtown",
        "Saint Josephs",
        "Carrollton Ridge",
        "Ellwood Park / Monument",
        "Cedmont",
        "Charles North",
        "Northwest Community Actio",
        "Baltimore Highlands",
        "Washington Hill",
        "Reisterstown Station",
        "Old Goucher",
        "Highlandtown",
        "McElderry Park",
        "Brooklyn",
        "Parkview / Woodbrook",
        "Forest Park",
        "Park Circle",
        "Frankford",
        "Oliver",
        "Dunbar - Broadway",
        "Woodmere",
        "Mount Vernon",
        "Seton Business Park",
        "Pimlico Good Neighbors",
        "Rosemont Homeowners / Tenan",
        "Dolfield",
        "Broening Manor",
        "Greenspring",
        "Mosher",
        "New Southwest / Mount Clare",
        "Oldtown",
        "Madison Park",
        "Mount Winans",
        "Glen Oaks",
        "Lucille Park",
        "Boyd - Booth",
        "Graceland Park",
        "Mid - Town Belvedere",
        "Tremont",
        "Winchester",
        "Broadway East",
        "North Harford Road",
        "Jonestown",
        "Ramblewood",
        "South Baltimore",
        "Downtown West",
        "Seton Hill",
        "Berea",
        "Waltherson",
        "Kresson",
        "Liberty Square",
        "Panway / Braddish Avenue",
        "Mondawmin",
        "Idlewood",
        "Shipley Hill",
        "New Northwood",
        "Lakeland",
        "Reservoir Hill",
        "Coppin Heights / Ash - Co - Eas",
        "Cedonia",
        "Hillen",
        "Oaklee",
        "Union Square",
        "Medford",
        "East Baltimore Midway",
        "Oakenshawe",
        "Greenmount West",
        "Morrell Park",
        "Penrose / Fayette Street Ou",
        "York - Homeland",
        "Midtown - Edmondson",
        "Upton",
        "Sandtown - Winchester",
        "Franklintown",
        "Gay Street",
        "Howard Park",
        "Glenham - Belhar",
        "Wakefield",
        "University Of Maryland",
        "Pen Lucy",
        "Carroll - Camden Industri",
        "Hanlon - Longwood",
        "Easterwood",
        "Westgate",
        "Woodbourne - McCabe",
        "Beechfield",
        "Barclay",
        "East Arlington",
        "Federal Hill",
        "Poppleton",
        "Biddle Street",
        "Cylburn",
        "Roland Park",
        "Ednor Gardens - Lakeside",
        "Armistead Gardens",
        "Kernewood",
        "Fallstaff",
        "Heritage Crossing",
        "Towanda - Grantley",
        "Keswick",
        "Loch Raven",
        "Madison - Eastend",
        "Walbrook",
        "Arlington",
        "Mount Washington",
        "Greektown",
        "Harwood",
        "Cross Keys",
        "Overlea",
        "Edmondson Village",
        "Fairmont",
        "Cheswolde",
        "Rosebank",
        "Wyman Park",
        "Garwyn Oaks",
        "Hamilton Hills",
        "Ashburton",
        "Johnston Square",
        "Franklin Square",
        "West Hills",
        "Otterbein",
        "Coldstream Homestead Mont",
        "Orchard Ridge",
        "Canton Industrial Area",
        "Arcadia",
        "Fells Point",
        "Druid Heights",
        "Glen",
        "Homeland",
        "Bolton Hill",
        "Mount Holly",
        "Hampden",
        "Remington",
        "Four By Four",
        "Penn - Fallsway",
        "Violetville",
        "Milton - Montford",
        "Woodberry",
        "Carroll Park",
        "Guilford",
        "Grove Park",
        "Ridgely's Delight",
        "South Clifton Park",
        "Little Italy",
        "Upper Fells Point",
        "Callaway - Garrison",
        "Dorchester",
        "Villages Of Homeland",
        "Coldspring",
        "Lauraville",
        "Beverly Hills",
        "Cross Country",
        "Original Northwood",
        "Riverside",
        "Butcher's Hill",
        "Hunting Ridge",
        "Evergreen Lawn",
        "Barre Circle",
        "Windsor Hills",
        "Chinquapin Park",
        "Orangeville Industrial Ar",
        "Carroll - South Hilton",
        "Orangeville",
        "Franklintown Road",
        "Dickeyville",
        "Abell",
        "Clifton Park",
        "Burleith - Leighton",
        "Lake Walker",
        "Saint Agnes",
        "Allendale",
        "Patterson Place",
        "Saint Paul",
        "Rosemont East",
        "Medfield",
        "Winston - Govans",
        "Cedarcroft",
        "Wilhelm Park",
        "Mid - Govans",
        "Wilson Park",
        "Pleasant View Gardens",
        "Perkins Homes",
        "Lower Herring Run Park",
        "Ten Hills",
        "Wrenlane",
        "Parkside",
        "North Roland Park / Poplar",
        "Purnell",
        "Radnor - Winston",
        "Saint Helena",
        "Brewers Hill",
        "Yale Heights",
        "Belvedere",
        "Sharp - Leadenhall",
        "Westfield",
        "Locust Point Industrial A",
        "Moravia - Walther",
        "Morgan State University",
        "Hoes Heights",
        "Fairfield Area",
        "Eastwood",
        "Middle Branch / Reedbird Pa",
        "Mayfield",
        "Gwynns Falls",
        "Stonewood - Pentwood - Winsto",
        "Perring Loch",
        "Levindale",
        "Lower Edmondson Village",
        "Hopkins Bayview",
        "Parklane",
        "Loyola / Notre Dame",
        "Gwynns Falls / Leakin Park",
        "Jones Falls Area",
        "Locust Point",
        "Langston Hughes",
        "Johns Hopkins Homewood",
        "Montebello",
        "O'Donnell Heights",
        "Stadium Area",
        "Greenmount Cemetery",
        "Forest Park Golf Course",
        "Druid Hill Park",
        "Sabina - Mattfeldt",
        "Wyndhurst",
        "Tuscany - Canterbury",
        "Cameron Village",
        "Bellona - Gittings",
        "Hawkins Point",
        "Patterson Park",
        "Evergreen",
        "Evesham Park",
        "Richnor Springs",
        "Lake Evesham",
        "Spring Garden Industrial",
        "Holabird Industrial Park",
        "Herring Run Park",
        "The Orchards",
        "Belair - Parkside",
        "Curtis Bay Industrial Are",
        "Blythewood",
        "Port Covington",
        "Morgan Park",
        "Taylor Heights",
        "Mt Pleasant Park",
        "Dundalk Marine Terminal"
    ]

    LIST_OF_PREMISES = [
        "STREET",
        "RELIGIOUS",
        "UNKNOWN",
        "RESTAURANT",
        "OTHER / RESI",
        "PARKING LO",
        "ROW / TOWNHO",
        "ALLEY",
        "OTHER - IN",
        "GARAGE ON",
        "GROCERY / CO",
        "OTHER - OU",
        "Parking Lo",
        "APT / CONDO",
        "VACANT BUI",
        "DRUG STORE",
        "FAST FOOD",
        "RETAIL / SMA",
        "RECREATION",
        "CLOTHING / S",
        "GAS STATIO",
        "Street",
        "CONVENIENC",
        "SINGLE HOU",
        "HOTEL / MOTE",
        "HOSP / NURS.",
        "BAR",
        "BARBER / BEA",
        "YARD",
        "BANK / FINAN",
        "LIQUOR STO",
        "PARK",
        "HOUSE UNDE",
        "SPECIALTY",
        "POLICE DEP",
        "SHED / GARAG",
        "DRIVEWAY",
        "SCHOOL",
        "Dwelling",
        "CARRY OUT",
        "LIBRARY",
        "DOCTORS OF",
        "FINANCE / LO",
        "DEPARTMENT",
        "OFFICE BUI",
        "CAB",
        "APARTMENT",
        "CONSTRUCTI",
        "MARKET STA",
        "PORCH / DECK",
        "BUS / AUTO",
        "AUTO PARTS",
        "CAR LOT - NE",
        "CAR  REPAI",
        "ATM MACHIN",
        "BOAT YARD",
        "Public Are",
        "BUS.STOR",
        "SHOPPING M",
        "MINI STORA",
        "Hospital",
        "Vacant Dwe",
        "COURT HOUS",
        "STADIUM",
        "RACE TRACK",
        "LAUNDRY / CL",
        "YARD / BUSIN",
        "PUBLIC BUI",
        "THEATRE",
        "INNER HARB",
        "NIGHT DEPO",
        "SUBWAY",
        "TAVERN / NIG",
        "WAREHOUSE",
        "Common Bus",
        "JEWELRY ST",
        "APT.LOCKE",
        "CLUB HOUSE",
        "HARDWARE / B",
        "Alley",
        "BOAT / SHIP",
        "BUS / RAILRO",
        "PLAYGROUND",
        "CONVENTION",
        "STRUCTURE -",
        "SALESMAN / C",
        "PUBLIC HOU",
        "BLDG UNDER",
        "RENTAL / VID",
        "TRACTOR TR",
        "FIRE DEPAR",
        "LIGHT RAIL",
        "VACANT LOT",
        "CHAIN FOOD",
        "SCHOOL PLA",
        "BUS.PARK",
        "CEMETERY",
        "PAWN SHOP",
        "PIZZA / OTHE",
        "MAILBOX - ST",
        "Public Hou",
        "POOL / BOWLI",
        "Church",
        "BAKERY",
        "RAILROAD C",
        "ARENA",
        "Garage",
        "BRIDGE - PIE",
        "WHOLESALE /",
        "Public Sch",
        "PHOTO STUD",
        "UTILITIES -",
        "MTA LOT",
        "PENITENTIA",
        "MOBILE HOM",
        "SKYWALK",
        "TRUCKING &",
        "Private Sc",
        "BOX CARS / C"
    ]

    LIST_OF_WEAPONS = [
        'FIREARM',
        'FIREARM',
        'FIREARM',
        'OTHER',
        'UNKNOWN',
        'HANDS',
        'HANDS',
        'KNIFE',
        'KNIFE',
        'KNIFE',
        'KNIFE'
    ]

    LIST_OF_CRIME_CODES = {
        '3AF': 'ROBBERY - STREET',
        '4C': 'AGG. ASSAULT',
        '6G': 'LARCENY',
        '6D': 'LARCENY FROM AUTO',
        '4E': 'COMMON ASSAULT',
        '5A': 'BURGLARY',
        '6E': 'LARCENY',
        '4F': 'ASSAULT BY THREAT',
        '3AJF': 'ROBBERY - CARJACKING',
        '7A': 'AUTO THEFT',
        '4B': 'AGG. ASSAULT',
        '3B': 'ROBBERY - STREET',
        '4A': 'AGG. ASSAULT',
        '3CF': 'ROBBERY - COMMERCIAL',
        '5B': 'BURGLARY',
        '9S': 'SHOOTING',
        '3JK': 'ROBBERY - RESIDENCE',
        '6C': 'LARCENY',
        '3AK': 'ROBBERY - STREET',
        '6J': 'LARCENY',
        '3CO': 'ROBBERY - COMMERCIAL',
        '5D': 'BURGLARY',
        '4D': 'AGG. ASSAULT',
        '3D': 'ROBBERY - COMMERCIAL',
        '1F': 'HOMICIDE',
        '3AO': 'ROBBERY - STREET',
        '5C': 'BURGLARY',
        '3K': 'ROBBERY - RESIDENCE',
        '8H': 'ARSON',
        '5E': 'BURGLARY',
        '3GF': 'ROBBERY - COMMERCIAL',
        '8BO': 'ARSON',
        '6F': 'LARCENY',
        '3H': 'ROBBERY - COMMERCIAL',
        '2A': 'RAPE',
        '6A': 'LARCENY',
        '3LF': 'ROBBERY - COMMERCIAL',
        '2B': 'RAPE',
        '3JF': 'ROBBERY - RESIDENCE',
        '8J': 'ARSON',
        '3CK': 'ROBBERY - COMMERCIAL',
        '3BJ': 'ROBBERY - CARJACKING',
        '1K': 'HOMICIDE',
        '5F': 'BURGLARY',
        '7C': 'AUTO THEFT',
        '6B': 'LARCENY',
        '3NF': 'ROBBERY - STREET',
        '8AO': 'ARSON',
        '3P': 'ROBBERY - STREET',
        '6L': 'LARCENY',
        '3NO': 'ROBBERY - STREET',
        '1O': 'HOMICIDE',
        '3JO': 'ROBBERY - RESIDENCE',
        '8BV': 'ARSON',
        '8AV': 'ARSON',
        '3NK': 'ROBBERY - STREET',
        '3M': 'ROBBERY - COMMERCIAL',
        '3F': 'ROBBERY - COMMERCIAL',
        '3AJO': 'ROBBERY - CARJACKING',
        '3AJK': 'ROBBERY - CARJACKING',
        '8FO': 'ARSON',
        '3GO': 'ROBBERY - COMMERCIAL',
        '3EF': 'ROBBERY - COMMERCIAL',
        '3EO': 'ROBBERY - COMMERCIAL',
        '8EO': 'ARSON',
        '3LO': 'ROBBERY - COMMERCIAL',
        '8GV': 'ARSON',
        '8CO': 'ARSON',
        '6H': 'LARCENY',
        '8I': 'ARSON',
        '3EK': 'ROBBERY - COMMERCIAL',
        '3GK': 'ROBBERY - COMMERCIAL',
        '7B': 'AUTO THEFT',
        '8CV': 'ARSON',
        '8EV': 'ARSON',
        '8GO': 'ARSON',
        '3LK': 'ROBBERY - COMMERCIAL',
        '6K': 'LARCENY',
        '8FV': 'ARSON',
        '3N': 'ROBBERY - STREET',
        '8DO': 'ARSON'
    }

    def __init__(self, csv_file_name, number_of_entries, list_of_years):
        self._data = []
        self._number_of_entries = number_of_entries
        self._list_of_years = list_of_years
        self._csv_file_name = csv_file_name

    def _randomword(self, length):
        return ''.join(random.choice(string.lowercase) for i in range(length))

    def load_data_into_memory(self):
        for i in range(int(self._number_of_entries)):
            row = []

            # CrimeDate
            year = random.choice(self._list_of_years)
            month = random.randint(1, 12)
            day = random.randint(1, 28)
            row.append('{0:02d}/{1:02d}/{2:02d}'.format(month, day, year))

            # CrimeTime
            hour = random.randint(1, 23)
            minute = random.randint(1, 59)
            seconds = random.randint(1, 59)
            row.append('{:02d}:{:02d}:{:02d}'.format(hour, minute, seconds))

            # CrimeCode
            crime_code = random.choice(
                FakeDataGenerator.LIST_OF_CRIME_CODES.keys())
            row.append('{!s}'.format(crime_code))

            # Location
            house_number = random.randint(1, 3000)
            # street = self._randomword(12)
            street = 'street'
            row.append('{!s} {!s}'.format(house_number, street))

            # Description
            crime_desc = FakeDataGenerator.LIST_OF_CRIME_CODES[crime_code]
            row.append('{!s}'.format(crime_desc))

            # Inside/Outside
            inside = random.choice(['I', 'O'])
            row.append('{!s}'.format(inside))

            # Weapon
            weapon = random.choice(FakeDataGenerator.LIST_OF_WEAPONS)
            row.append('{!s}'.format(weapon))

            # Post
            post = 0
            row.append('{!s}'.format(post))

            # District
            district = random.choice(FakeDataGenerator.LIST_OF_DISTRICTS)
            row.append('{!s}'.format(district))

            # Neighborhood
            neighbor = random.choice(FakeDataGenerator.LIST_OF_NEIGHBORS)
            row.append('{!s}'.format(neighbor))

            # Longitude
            lng = 0
            row.append('{!s}'.format(lng))

            # Latitude
            lat = 0
            row.append('{!s}'.format(lat))

            # Location 1
            location_1 = '(0, 0)'
            row.append('{!s}'.format(location_1))

            # Premise
            premise = random.choice(FakeDataGenerator.LIST_OF_PREMISES)
            row.append('{!s}'.format(premise))

            # Total Incidents
            total_incidents = 1
            row.append('{!s}'.format(total_incidents))

            # save the data
            self._data.append(row)

            if i > 0 and i % 25000 == 0:
                print 'Generated {!s} random rows ...'.format(i)

    def save_data_to_csv(self):
        with open(self._csv_file_name, 'wb') as f:
            print 'Start writing csv file ...'
            wr = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
            wr.writerow(['CrimeDate', 'CrimeTime', 'CrimeCode', 'Location',
                         'Description', 'Inside/Outside', 'Weapon', 'Post',
                         'District', 'Neighborhood', 'Longitude', 'Latitude',
                         'Location 1', 'Premise', 'Total Incidents'])
            for row in self._data:
                wr.writerow(row)
            print 'Finished writing csv file!'


def generate_fake_db(csv_filename,
                     number_of_entries,
                     list_of_years,
                     db_filename,
                     db_schema_file,
                     geocoding_cache_file,
                     geocoding_api_key,
                     skip_entries_years
                     ):
    gen = FakeDataGenerator(
        csv_file_name=csv_filename,
        number_of_entries=number_of_entries,
        list_of_years=list_of_years
    )
    gen.load_data_into_memory()
    gen.save_data_to_csv()

    db_filename = db_filename.replace('.', '_fake.')
    db_loader = BaltimoreCrimesLoader(
        csv_filename, db_filename, db_schema_file, geocoding_cache_file,
        geocoding_api_key, skip_entries_years
    )
    db_loader.load_data_into_memory()
    db_loader.save_data_in_database()


def generate_real_db(source_csv_file,
                     db_filename,
                     db_schema_file,
                     geocoding_cache_file,
                     geocoding_api_key,
                     skip_entries_years):
    db_loader = BaltimoreCrimesLoader(
        source_csv_file, db_filename, db_schema_file, geocoding_cache_file,
        geocoding_api_key, skip_entries_years
    )
    db_loader.load_data_into_memory()
    db_loader.save_data_in_database()


def usage():
    spaces = '                                  '
    msg = '\nusage: '
    msg += 'python main_generate_db.py '
    msg += '[-h] [--help] '
    msg += '[-r] [--real] '
    msg += '[-f] [--fake]\n'
    msg += spaces + '[--csv=<path>] '
    msg += '[-api_key=<key>]\n'
    msg += spaces + '[-schema=<path>] '
    msg += '[-output=<path>]'
    print msg

    print '\nAVAILABLE OPTIONS:'

    spaces = '     '

    msg = '  -h, --help\n'
    msg += spaces + 'Print this information :)'
    print msg + '\n'

    msg = '  -r, --real\n'
    msg += spaces + 'Generate database by using the real data (see the\n'
    msg += spaces + 'option csv).'
    print msg + '\n'

    msg = '  --output\n'
    msg += spaces + 'Option to set the path the resulting database file.\n'
    msg += spaces + '(default = balitmore_crime_db.sdb)'
    print msg + '\n'

    msg = '  --skip_years\n'
    msg += spaces + 'Option to skip certain years during the database '
    msg += 'generation.\n'
    msg += spaces + 'Note: Use string with comma separated values, for '
    msg += 'example:\n\t--skip_years="2015, 2020, 1998"\n'
    msg += spaces + '(default = "2017")'
    print msg + '\n'

    msg = '  --csv\n'
    msg += spaces + 'Option to set the path and name for the source csv file.\n'
    msg += spaces + '(default = BPD_Part_1_Victim_Based_Crime_Data.csv)'
    print msg + '\n'

    msg = '  --api_key\n'
    msg += spaces + 'Option to set API key, which is used to retrieve the.\n'
    msg += spaces + 'coordinates (lat and lng) for locations, such as\n'
    msg += spaces + 'districts or neighborhoods.\n'
    print msg + '\n'

    msg = '  --schema\n'
    msg += spaces + 'Option to set the SQL schema file, which is used to\n'
    msg += spaces + 'initialize the SQLite database.\n'
    msg += spaces + '(default = create-db-schema.sql)'
    print msg + '\n'

    msg = '  -f, --fake\n'
    msg += spaces + 'Generate database by using random fake data.\n'
    msg += spaces + 'This creates a fake csv file first and then generates\n'
    msg += spaces + 'the database.'
    print msg + '\n'

    msg = '  --fake_entries\n'
    msg += spaces + 'Option to set the number of entires for the '
    msg += 'fake dataset.\n'
    msg += spaces + '(default = 270000)'
    print msg + '\n'

    msg = '  --fake_years\n'
    msg += spaces + 'Option to set possible years for the generation of '
    msg += 'the fake data.\n'
    msg += spaces + 'Note: Use string with comma separated values, for '
    msg += 'example:\n\t--fake_years="2015, 2020, 1998"\n'
    msg += spaces + '(default = "2012, 2013, 2014, 2015, 2016")'
    print msg + '\n'


def main():
    if len(sys.argv) <= 1:
        print "missing arguments/options"
        usage()
    try:
        opts, args = getopt.getopt(
            sys.argv[1:],
            "rfh",
            [
                "help", "real", "fake", "csv=", "api_key=",
                "schema=", "output=", "fake_entries=", "fake_years=",
                "skip_years="
            ]
        )
    except getopt.GetoptError as err:
        print str(err)
        usage()
        sys.exit(2)

    do_real_db = False
    do_fake_db = False
    path_this = os.path.dirname(os.path.abspath(__file__))
    csv = path_this + '/../assets/data/BPD_Part_1_Victim_Based_Crime_Data.csv'
    api_key = ''
    schema = path_this + '/create-db-schema.sql'
    db = path_this + '/balitmore_crime_db.sdb'
    skip_years = [2017]
    fake_num_entries = 270000
    fake_years = [2012, 2013, 2014, 2015, 2016]
    for option, arg in opts:
        if option in ("-h", "--help"):
            usage()
            sys.exit()
        elif option in ("-r", "--real"):
            do_real_db = True
        elif option in ("-f", "--fake"):
            do_fake_db = True
        elif option == "--csv":
            csv = arg
        elif option == "--api_key":
            api_key = arg
        elif option == "--schema":
            schema = arg
        elif option == "--output":
            db = arg
        elif option == "--fake_entries":
            fake_num_entries = arg
        elif option == "--fake_years":
            years = arg.replace(old=' ', new='')
            fake_years = years.split(str=',')
        elif option == "--skip_years":
            years = arg.replace(old=' ', new='')
            skip_years = years.split(str=',')
        else:
            assert False, "unhandled option"
            usage()

    geocoding_cache_file = path_this + '/google_geocode_responses.pkl'

    if do_real_db:
        generate_real_db(source_csv_file=csv,
                         db_filename=db,
                         db_schema_file=schema,
                         geocoding_cache_file=geocoding_cache_file,
                         geocoding_api_key=api_key,
                         skip_entries_years=skip_years)

    if do_fake_db:
        generate_fake_db(csv_filename=csv.replace('.csv', '_fake.csv'),
                         number_of_entries=fake_num_entries,
                         list_of_years=fake_years,
                         db_filename=db,
                         db_schema_file=schema,
                         geocoding_cache_file=geocoding_cache_file,
                         geocoding_api_key=api_key,
                         skip_entries_years=skip_years)


if __name__ == "__main__":
    # print 'Number of arguments:', len(sys.argv), 'arguments.'
    # print 'Argument List:', str(sys.argv)
    main()
