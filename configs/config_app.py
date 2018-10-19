from libavg import avg

SETTING = "Desktop"  # Wall, Proj, Desktop, SurfaceHub
IP_SETTINGS = "MarcLaptop"  # PhilippDesktop, MarcLaptop, LaborDesktop, Wall, SurfaceHub

LONG_RECOGNIZER_MODE = False
SESSION = 1

# Values for the optitrack system.
optitrack_ip = "127.0.0.1"
optitrack_port = "5103"
optitrack_osc_format = ["id", "x", "y", "z", "roll", "pitch", "yaw", "quat_2", "quat_3", "quat_4", "quat_1", "name"]

# Mobile device mapping: Ip of the device that has opened the website for the mobile view and the name for the
# optitrack system.
mobile_devices = {"141.76.67.241": "Healthy", "141.76.67.232": "Bumpy"}

# Other values and study parameters.
kinect_data_ip = "127.0.0.1"
show_test_touch_view = False
study_mode = False

server_port = "8080"  # TODO: Decide which server to use.
if IP_SETTINGS == "MarcLaptop":
    server_ip = "141.76.67.175"
elif IP_SETTINGS == "PhilippDesktop":
    server_ip = "192.168.178.192"
elif IP_SETTINGS == "LaborDesktop":
    server_ip = "141.76.67.209"
elif IP_SETTINGS == "Wall":
    server_ip = "141.76.67.198"
    optitrack_ip = "141.76.67.198"
    kinect_data_ip = "141.76.67.198"
elif IP_SETTINGS == "SurfaceHub":
    optitrack_ip = "141.76.67.202"
    server_ip = "141.76.67.202"

if SETTING == "Wall":
    app_resolution = 7680, 3240
    app_full_screen = True
    pixel_per_cm = 15.802469
    # Values for the optitrack system.
    display_height_cm = 206
    pitch_min_max = [1.09, -1.15, -app_resolution[0] / 2, app_resolution[0] / 2]
    roll_min_max = [0.618, -0.694, -app_resolution[1] / 2, app_resolution[1] / 2]
    # Values for the user study.
    show_test_touch_view = True
    study_mode = False
    # Values for the map.
    min_map_scale_factor = 0.282029497494
    max_map_scale_factor = 2.057954395234
elif SETTING == "Desktop":
    app_resolution = avg.Point2D(1920, 1080)
    pixel_per_cm = 15.87
    app_full_screen = True
    # Values for the optitrack system.
    display_height_cm = 50
    # Values for the user study.
    show_test_touch_view = False
    study_mode = False
    # Values for the map.
    min_map_scale_factor = 0.0767852680667
    max_map_scale_factor = 1.38833813268
elif SETTING == "SurfaceHub":
    app_resolution = avg.Point2D(3840, 2160)
    pixel_per_cm = 15.87
    # Values for the optitrack system.
    display_height_cm = 95
    # Values for the user study.
    show_test_touch_view = False
    study_mode = False
    # Values for the map.
    min_map_scale_factor = 0.0767852680667
    max_map_scale_factor = 1.38833813268

pointing_mode = 2  # For Perspectiv ... look at device.py -> PointingMapping
zoom_enabled = False if study_mode else True
pan_enabled = False if study_mode else True
pan_frequency_factor = 3
min_pan_movement = 25

force_sql_reload = False
fake_data_mode = False
data_mode_string = "fake" if fake_data_mode else "real"

default_language = "de"

sql_result_dump_filename = {
    "real": 'tmp/sql_result_dump.pkl',
    "fake": 'tmp/fake_sql_result_dump.pkl'
}
db_filename = {
    "real": "gen_db/balitmore_crime_db.sdb",
    "fake": "gen_db/balitmore_crime_db_fake.sdb"
}
study_order_file = "gen_study_order/study_order.json"
study_tasks_file = "assets/study_preparations/tasks.json"
maps_images = {
    "baltimore_wallsize": {
        "image": "assets/map_images/baltimore_wallsize_normal.jpg",
        "size": (7680, 3240),
        "left_top": {
            "lng": -76.94263707548828,
            "lat": 39.42782294013011
        },
        "right_bottom": {
            "lng": -76.28345738798828,
            "lat": 39.21268718630549
        }
    }
}
map_image = "baltimore_wallsize"

