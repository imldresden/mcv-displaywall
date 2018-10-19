import math
from configs import config_app


class CommonRecognizerDefaults(object):
    HOLD_DELAY = 500
    HOLD_MAX_DIST = 10 if not config_app.LONG_RECOGNIZER_MODE else 15

    TAP_MAX_TIME = 200 if not config_app.LONG_RECOGNIZER_MODE else 350
    TAP_MAX_DIST = 10 if not config_app.LONG_RECOGNIZER_MODE else 15

    DOUBLE_TAP_MAX_TIME = 350 if not config_app.LONG_RECOGNIZER_MODE else 550
    DOUBLE_TAP_MAX_DIST = 35 if not config_app.LONG_RECOGNIZER_MODE else 50

    DRAG_MIN_DIST = 5

    SWIPE_DIRECTION_TOLERANCE = 65.0 * math.pi / 180
    SWIPE_MIN_DIST = 25

    TWO_CONTACT_MAX_DIST_CM = 15


class PointerCanvasRecognizerDefaults(CommonRecognizerDefaults):
    HOLD_DELAY = 200
    HOLD_MAX_DIST = 20 if not config_app.LONG_RECOGNIZER_MODE else 35

    SWIPE_MAX_TIME = 350 if not config_app.LONG_RECOGNIZER_MODE else 500
    DOUBLE_TAP_HOLD_MAX_TIME = 200 if not config_app.LONG_RECOGNIZER_MODE else 350
