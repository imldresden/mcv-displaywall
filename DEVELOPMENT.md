# Development Guide

**Important**: Parts of this development guide are out-of-date.

## External Tracking System for Device Localization

During the development of this prototype we used the OptiTrack tracking system
by NaturalPoint to capture device locations. The server listens
(see [oscReceiver](server/utility/oscReceiver.ts)) on [OSC](http://opensoundcontrol.org/) network
messages containing the corresponding device locations.

As describe in the [README](README.md), the app can also be used without such a tracking
system.

## Setup and Run Project Within PyCharm

1. Load the root folder in PyCharm and open the **Project** tab.
2. Get a key for the [Google Geocoding API](https://developers.google.com/maps/documentation/geocoding/start). This key
is necessary to get the coordination of the neighborhoods in Baltimore.
2. Right-click on `gen_db\main_generate_db.py` and choose **Run 'main_generate_db'**.
3. Left click on the `main_generate_db` on the top right, right next to the start button, and than choose **Edit 
configurations ..**. There you need to add **-r** in the `Parameters` field. You should also add the parameter 
**--api-key=** for the API key from google. 
4. Start the `main_generate_db` again. This will create the database for the application.
5. Change values in the `config/config_app.py` file.
6.  Right-click on `main.py` and choose **Run 'main'**.

## Parameters in `config_app.py`

There are several settings to be found in the `configs/config_app.py` to find. Some of them will be descript here:
+ __SETTING__: The environment the application is started on. The following lines containes different values specifig for each technical setting this application can run on.
+ __show_test_touch_view__: Should an extra view be shown before the main app created? This only occurres if the study_mode is true. To leave the test touch view its necessary to touch each of the 12 rectangles shown. This allows us to test if each of the single displays recognizes the touches.
+ __study_mode__: Should the application be started in study mode? In study mode the application logs all movement and interactions of users and devices in front of the wall. Also all touch events are logged too. It will also show an extra study mode task text view.
+ __optitrack_ip__: The ip of the optitrack server the application should receive the data from.
+ __optitrack_port__: The port of the optitrack server.
+ __kinect_data_ip__: The ip of the kinect that sends data to the application. This is only necessary if the application should work in study mode.
+ __pixel_per_cm__: The pixel per cm of the display that is used. This is necessary to map the pointer of a deivce correctly on the display wall.
+ __display_height_cm__: The height of the display that is used. This is only necessary in combination with the use of a device as a cursor.
+ __force_sql_reload__: If this is true the sql results will be calculated again at the next start up of the application. This is necessary if the sqlite database was newly generated or if the sql queries were changed.
+ __fake_data_mode__: If this is true the application will not use the real data set but rather the fake one. The fake one needs to be created with the flag `-f` at the `gen_db/main_generate_db.py`. Here its only necessary to set this setting to True.
+ __default_language__: Its possible to translate all shown text of this application from english in different languages. If a new language besides english and german should be used, a file in `assets/translations` needs to be added. Further is it necessary to add this file in the 
`divico_ctrl/translation.py` file. Also is it necessary to repeat all steps at the first start if the application was run before.