# Installation

1. Download the data set and save the CSV as `BPD_Part_1_Victim_Based_Crime_Data.csv` in the root of this project folder; [https://data.baltimorecity.gov](https://data.baltimorecity.gov/Public-Safety/BPD-Part-1-Victim-Based-Crime-Data/wsfq-mvij)
2. Install the googlemaps python package `pip install googlemaps`


# Tools

* [MySQL Workbench](https://www.mysql.com/de/products/workbench/) for ER database modelling
  * you can then open the file db_modelling.mwb
* [MySQL Workbench ExportSQLite Plugin](https://github.com/tatsushid/mysql-wb-exportsqlite) for exporting the ER database model to SQLite
  * you can then generate the file create-db-schema.sql

# install of module googlemaps on display wall

* 'pip install googlemaps' fails with version conflict, 
    *  update urllib3 and chardet modules: 'pip3 install -U urllib3 chardet' (https://github.com/googlemaps/google-maps-services-python/issues/183), then try again
