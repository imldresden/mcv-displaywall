-- Creator:       MySQL Workbench 6.3.9/ExportSQLite Plugin 0.1.0
-- Author:        Ricardo Langner
-- Caption:       New Model
-- Project:       Name of the project
-- Changed:       2017-09-13 17:11
-- Created:       2017-07-26 21:33
PRAGMA foreign_keys = OFF;

-- Schema: balitmore_crime_db
ATTACH "balitmore_crime_db.sdb" AS "balitmore_crime_db";
BEGIN;
CREATE TABLE "balitmore_crime_db"."districts"(
  "district_id" INTEGER PRIMARY KEY NOT NULL,
  "name" VARCHAR(45) NOT NULL,
  "lat" FLOAT,
  "lng" FLOAT,
  "short_name" VARCHAR(2),
  "label" VARCHAR(45),
  "short_label" VARCHAR(45),
  CONSTRAINT "name_UNIQUE"
    UNIQUE("name")
);
CREATE TABLE "balitmore_crime_db"."crime_codes"(
  "crime_code_id" INTEGER PRIMARY KEY NOT NULL,
  "crime_code" VARCHAR(3) NOT NULL,
  "description" VARCHAR(45),
  CONSTRAINT "crime_code_UNIQUE"
    UNIQUE("crime_code")
);
CREATE TABLE "balitmore_crime_db"."streets"(
  "street_id" INTEGER PRIMARY KEY NOT NULL,
  "name" VARCHAR(45) NOT NULL,
  CONSTRAINT "name_UNIQUE"
    UNIQUE("name")
);
CREATE TABLE "balitmore_crime_db"."neighborhoods"(
  "neighbor_id" INTEGER PRIMARY KEY NOT NULL,
  "name" VARCHAR(45) NOT NULL,
  "lat" FLOAT,
  "lng" FLOAT,
  CONSTRAINT "name_UNIQUE"
    UNIQUE("name")
);
CREATE TABLE "balitmore_crime_db"."premises"(
  "premise_id" INTEGER PRIMARY KEY NOT NULL,
  "name" VARCHAR(45) NOT NULL,
  "label" VARCHAR(45),
  CONSTRAINT "name_UNIQUE"
    UNIQUE("name")
);
CREATE TABLE "balitmore_crime_db"."locations"(
  "location_id" INTEGER PRIMARY KEY NOT NULL,
  "district_id" INTEGER,
  "neighbor_id" INTEGER,
  "street_id" INTEGER,
  "postal_code" INTEGER,
  "house_number" VARCHAR(45),
  "lat" FLOAT,
  "lng" FLOAT,
  "orig_address" VARCHAR(45),
  CONSTRAINT "street_id"
    FOREIGN KEY("street_id")
    REFERENCES "streets"("street_id")
    ON DELETE RESTRICT
    ON UPDATE RESTRICT,
  CONSTRAINT "district_id"
    FOREIGN KEY("district_id")
    REFERENCES "districts"("district_id")
    ON DELETE RESTRICT
    ON UPDATE RESTRICT,
  CONSTRAINT "neighbor_id"
    FOREIGN KEY("neighbor_id")
    REFERENCES "neighborhoods"("neighbor_id")
    ON DELETE RESTRICT
    ON UPDATE RESTRICT
);
CREATE INDEX "balitmore_crime_db"."locations.street_id_idx" ON "locations" ("street_id");
CREATE INDEX "balitmore_crime_db"."locations.postal_code_idx" ON "locations" ("district_id");
CREATE INDEX "balitmore_crime_db"."locations.neighbor_id_idx" ON "locations" ("neighbor_id");
CREATE TABLE "balitmore_crime_db"."weapons"(
  "weapon_id" INTEGER PRIMARY KEY NOT NULL,
  "name" VARCHAR(45) NOT NULL,
  "label" VARCHAR(45),
  CONSTRAINT "name_UNIQUE"
    UNIQUE("name")
);
CREATE TABLE "balitmore_crime_db"."crime_types"(
  "crime_type_id" INTEGER PRIMARY KEY NOT NULL,
  "name" VARCHAR(45) NOT NULL,
  "label" VARCHAR(45),
  CONSTRAINT "name_UNIQUE"
    UNIQUE("name")
);
CREATE TABLE "balitmore_crime_db"."crimes"(
  "crime_id" INTEGER PRIMARY KEY NOT NULL,
  "line_in_src_csv" INTEGER NOT NULL,
  "datetime" VARCHAR(19) NOT NULL,
  "inside" INTEGER,
  "location_id" INTEGER,
  "crime_code" VARCHAR(3),
  "crime_type_id" INTEGER,
  "weapon_id" INTEGER,
  "premise_id" INTEGER,
  "total_incidents" INTEGER,
  "year" INTEGER NOT NULL,
  "month" INTEGER NOT NULL,
  "day" INTEGER NOT NULL,
  "hour" INTEGER NOT NULL,
  "minute" INTEGER NOT NULL,
  "seconds" INTEGER NOT NULL,
  "weekday" INTEGER NOT NULL,
  "daytime" INTEGER NOT NULL,
  "week" INTEGER NOT NULL,
  CONSTRAINT "line_in_src_csv_UNIQUE"
    UNIQUE("line_in_src_csv"),
  CONSTRAINT "location_id"
    FOREIGN KEY("location_id")
    REFERENCES "locations"("location_id")
    ON DELETE RESTRICT
    ON UPDATE RESTRICT,
  CONSTRAINT "crime_code"
    FOREIGN KEY("crime_code")
    REFERENCES "crime_codes"("crime_code")
    ON DELETE RESTRICT
    ON UPDATE RESTRICT,
  CONSTRAINT "weapon_id"
    FOREIGN KEY("weapon_id")
    REFERENCES "weapons"("weapon_id")
    ON DELETE RESTRICT
    ON UPDATE RESTRICT,
  CONSTRAINT "premise_id"
    FOREIGN KEY("premise_id")
    REFERENCES "premises"("premise_id")
    ON DELETE RESTRICT
    ON UPDATE RESTRICT,
  CONSTRAINT "crime_type_id"
    FOREIGN KEY("crime_type_id")
    REFERENCES "crime_types"("crime_type_id")
    ON DELETE RESTRICT
    ON UPDATE RESTRICT
);
CREATE INDEX "balitmore_crime_db"."crimes.location_id_idx" ON "crimes" ("location_id");
CREATE INDEX "balitmore_crime_db"."crimes.crime_code_idx" ON "crimes" ("crime_code");
CREATE INDEX "balitmore_crime_db"."crimes.weapon_id_idx" ON "crimes" ("weapon_id");
CREATE INDEX "balitmore_crime_db"."crimes.premise_id_idx" ON "crimes" ("premise_id");
CREATE INDEX "balitmore_crime_db"."crimes.crime_type_id_idx" ON "crimes" ("crime_type_id");
COMMIT;
