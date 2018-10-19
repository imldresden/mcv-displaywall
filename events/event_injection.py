from libavg import avg, player

from configs import config_app
from logging_base.study_logging import StudyLog

__helper = player.getTestHelper()


def inject_touch_event(event_type, pos, event_id):
    """
    Injects a touch event in the system.

    :param event_type: The type of event to inject.
    :type event_type: int
    :param pos: The position the event should take place.
    :type pos: tuple[float, float]
    :param event_id: The id for the event.
    :type event_id: int
    """
    # print "Inject event: id={!s}, type={!s}, pos={!s}".format(event_id, event_type, pos)

    global __helper
    if config_app.study_mode:
        StudyLog.get_instance().write_touch(pos_x=pos[0], pos_y=pos[1], event_type=event_type, to_injection=True)
    __helper.fakeTouchEvent(event_id, event_type, avg.Event.TOUCH, pos)
