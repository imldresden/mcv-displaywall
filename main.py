from libavg import app
from examples.application import Application
import configs.config_app as config


if __name__ == '__main__':
    # Init application
    lib_app = app.App()

    # Run application
    if config.SETTING == "Desktop":
        lib_app.run(Application(), app_resolution='3840x1030')
    elif config.SETTING == "Wall":
        lib_app.run(Application(), app_resolution='7680x3240', app_fullscreen="false")
    elif config.SETTING == "SurfaceHub":
        lib_app.run(Application(), app_resolution='3840x2140', app_fullscreen="true")
