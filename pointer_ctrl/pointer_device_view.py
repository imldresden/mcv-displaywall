from libavg.gesture import SwipeRecognizer, DragRecognizer, TapRecognizer
from libavg import avg, player
from device_tracking.device import Device
from logging_base.study_logging import StudyLog
from pointer_ctrl.configurations.device_pointer_configurations import DevicePointerConfigurations
from events.event_dispatcher import EventDispatcher
from libavg.avg import CursorEvent


class PointerDeviceView(avg.DivNode, EventDispatcher):
    __CURSOR_DOWN = "cursorDown"
    __CURSOR_MOTION = "cursorMotion"
    __CURSOR_UP = "cursorUp"
    __SWIPE = "swipe"
    __DRAG = "drag"
    __DOUBLE_TAP = "doubleTap"
    __HOLD = "hold"
    __DOUBLE_TAP_HOLD = "doubleTapHold"
    __DOUBLE_TAP_HOLD_DRAG = "doubleTapHoldDrag"
    __DOUBLE_TAP_HOLD_END = "doubleTapHoldEnd"

    def __init__(self, device, device_pointer_config, **kwargs):
        """

        :param device: The device this view should represent.
        :type device: Device
        :param device_pointer_config: The configuration for the pointer device.
        :type device_pointer_config: DevicePointerConfigurations
        :param kwargs:
        """
        super(PointerDeviceView, self).__init__(**kwargs)
        EventDispatcher.__init__(self)
        self.registerInstance(self, device.canvas)

        self.__device = device
        self.__device_pointer_config = None
        self.__internal_div = avg.DivNode()

        self.change_configuration(device_pointer_config)

        self.__swipe_rec_right = SwipeRecognizer(
            node=self.__internal_div,
            direction=SwipeRecognizer.RIGHT,
            directionTolerance=self.__device_pointer_config.swipe_direction_tolerance,
            detectedHandler=self.__on_swipe_right,
            minDist=self.__device_pointer_config.swipe_min_dist
        )
        self.__swipe_rec_left = SwipeRecognizer(
            node=self.__internal_div,
            direction=SwipeRecognizer.LEFT,
            directionTolerance=self.__device_pointer_config.swipe_direction_tolerance,
            detectedHandler=self.__on_swipe_left,
            minDist=self.__device_pointer_config.swipe_min_dist
        )
        self.__swipe_rec_right = SwipeRecognizer(
            node=self.__internal_div,
            direction=SwipeRecognizer.UP,
            directionTolerance=self.__device_pointer_config.swipe_direction_tolerance,
            detectedHandler=self.__on_swipe_up,
            minDist=self.__device_pointer_config.swipe_min_dist
        )
        self.__swipe_rec_left = SwipeRecognizer(
            node=self.__internal_div,
            direction=SwipeRecognizer.DOWN,
            directionTolerance=self.__device_pointer_config.swipe_direction_tolerance,
            detectedHandler=self.__on_swipe_down,
            minDist=self.__device_pointer_config.swipe_min_dist
        )
        self.__drag_recognizer = DragRecognizer(
            eventNode=self.__internal_div,
            minDragDist=self.__device_pointer_config.min_drag_dist,
            direction=DragRecognizer.ANY_DIRECTION,
            moveHandler=self.__on_drag,
            endHandler=self.__on_drag_end,
            friction=-1
        )
        self.__tap_recognizer = TapRecognizer(
            node=self.__internal_div,
            maxDist=self.__device_pointer_config.tap_max_dist,
            maxTime=self.__device_pointer_config.tap_max_time,
            detectedHandler=self.__on_tap
        )

        self.__event_id = None
        self.__event = None
        self.__event_time = None
        self.__event_movement_dist = None

        self.__last_drag_offset = (0, 0)
        self.__last_tap_time = 0
        self.__double_tap_hold_active = False
        self.__hold_active = False

        self.subscribe(avg.Node.CURSOR_DOWN, self.__on_cursor_down)
        self.subscribe(avg.Node.CURSOR_MOTION, self.__on_cursor_motion)
        self.subscribe(avg.Node.CURSOR_UP, self.__on_cursor_up)

    @property
    def device_id(self):
        """
        :rtype: int
        """
        return self.__device.id

    def __on_cursor_down(self, event):
        """
        Called when a cursor down was recognized on this view.

        :type event: CursorEvent
        """
        StudyLog.get_instance().write_device_canvas_touch(self.__device, "CURSOR DOWN", event)
        self.dispatch(self.__CURSOR_DOWN, sender=self, event=event)

        if self.__event:
            return

        self.__event = event
        self.__event_id = event.cursorid
        if player.getFrameTime() - self.__last_tap_time < self.__device_pointer_config.double_tap_hold_max_time:
            self.__double_tap_hold_active = True
            StudyLog.get_instance().write_device_canvas_event(self.__device, "DOUBLE TAP HOLD")
            self.dispatch(self.__DOUBLE_TAP_HOLD, sender=self, event=event)
        else:
            self.__event_time = player.getFrameTime()
            self.__event_movement_dist = 0

    def __on_cursor_motion(self, event):
        """
        Called when a cursor motion was recognized on this view.

        :type event: CursorEvent
        """
        StudyLog.get_instance().write_device_canvas_touch(self.__device, "CURSOR MOTION", event)
        self.dispatch(self.__CURSOR_MOTION, sender=self, event=event)

        if not self.__event:
            return
        if self.__event.cursorid != event.cursorid:
            return

        self.__event = event
        if event.contact.distancefromstart > self.__event_movement_dist:
            self.__event_movement_dist = event.contact.distancefromstart

    def __on_cursor_up(self, event):
        """
        Called when a cursor up was recognized on this view.

        :type event: CursorEvent
        """
        StudyLog.get_instance().write_device_canvas_touch(self.__device, "CURSOR UP", event)
        self.dispatch(self.__CURSOR_UP, sender=self, event=event)

        if not self.__event:
            return
        if self.__event.cursorid != event.cursorid:
            return

        self.__event_id = None
        self.__event = None
        self.__event_movement_dist = None

        self.__hold_active = False
        if self.__double_tap_hold_active:
            StudyLog.get_instance().write_device_canvas_event(self.__device, "DOUBLE TAP HOLD END")
            self.dispatch(self.__DOUBLE_TAP_HOLD_END, sender=self)
        self.__double_tap_hold_active = False

    def on_frame(self):
        """
        Needed to be called every frame.
        """
        if not self.__event:
            return
        if self.__double_tap_hold_active or self.__hold_active:
            return

        now = player.getFrameTime()
        down_time = now - self.__event_time
        if down_time <= self.__device_pointer_config.hold_delay:
            return
        if self.__event_movement_dist > self.__device_pointer_config.hold_max_dist * player.getPixelsPerMM():
            return

        else:
            self.__hold_active = True
            StudyLog.get_instance().write_device_canvas_event(self.__device, "HOLD")
            self.dispatch(self.__HOLD, sender=self, event=self.__event)

    def __on_swipe_right(self):
        """
        Called when a swipe to the right was recognized.
        """
        if self.__hold_active or self.__double_tap_hold_active:
            return

        event_time = player.getFrameTime() - self.__event_time
        if event_time > self.__device_pointer_config.swipe_max_time:
            return

        StudyLog.get_instance().write_device_canvas_event(self.__device, "SWIPE RIGHT")
        self.dispatch(self.__SWIPE, sender=self, direction=SwipeRecognizer.RIGHT)

    def __on_swipe_left(self):
        """
        Called when a swipe to the left was recognized.
        """
        if self.__hold_active or self.__double_tap_hold_active:
            return

        event_time = player.getFrameTime() - self.__event_time
        if event_time > self.__device_pointer_config.swipe_max_time:
            return

        StudyLog.get_instance().write_device_canvas_event(self.__device, "SWIPE LEFT")
        self.dispatch(self.__SWIPE, sender=self, direction=SwipeRecognizer.LEFT)

    def __on_swipe_up(self):
        """
        Called when a swipe to the right was recognized.
        """
        if self.__hold_active or self.__double_tap_hold_active:
            return

        event_time = player.getFrameTime() - self.__event_time
        if event_time > self.__device_pointer_config.swipe_max_time:
            return

        StudyLog.get_instance().write_device_canvas_event(self.__device, "SWIPE UP")
        self.dispatch(self.__SWIPE, sender=self, direction=SwipeRecognizer.UP)

    def __on_swipe_down(self):
        """
        Called when a swipe to the left was recognized.
        """
        if self.__hold_active or self.__double_tap_hold_active:
            return

        event_time = player.getFrameTime() - self.__event_time
        if event_time > self.__device_pointer_config.swipe_max_time:
            return

        StudyLog.get_instance().write_device_canvas_event(self.__device, "SWIPE DOWN")
        self.dispatch(self.__SWIPE, sender=self, direction=SwipeRecognizer.DOWN)

    def __on_tap(self):
        """
        Called when a tap event has occurred.
        """
        self.__last_tap_time = player.getFrameTime()
        StudyLog.get_instance().write_device_canvas_event(self.__device, "TAP")

    def __on_drag(self, offset):
        """
        Called when a drag has started.

        :param offset: The offset to the start pos.
        :type offset: tuple[float, float]
        """
        if self.__hold_active:
            return

        pos_change = offset[0] - self.__last_drag_offset[0], offset[1] - self.__last_drag_offset[1]
        self.__last_drag_offset = offset

        event = self.__DOUBLE_TAP_HOLD_DRAG if self.__double_tap_hold_active else self.__DRAG
        if self.__double_tap_hold_active:
            StudyLog.get_instance().write_device_canvas_event(self.__device, "DOUBLE TAP HOLD DRAG")
        self.dispatch(event, sender=self, pos_change=pos_change)

    def __on_drag_end(self):
        """
        Called when a drag has ended.
        """
        StudyLog.get_instance().write_device_canvas_event(self.__device, "DRAG END")

        self.__last_drag_offset = (0, 0)
        self.__hold_active = False

        if self.__double_tap_hold_active:
            StudyLog.get_instance().write_device_canvas_event(self.__device, "DOUBLE TAP HOLD END")
            self.dispatch(self.__DOUBLE_TAP_HOLD_END, sender=self)
        self.__double_tap_hold_active = False

    def change_configuration(self, device_pointer_config):
        """
        Changes the device pointer configuration and draws the view anew.

        :param device_pointer_config: The new configuration.
        :type device_pointer_config: DevicePointerConfigurations
        """
        internal_div_nodes = [self.__internal_div.getChild(i) for i in range(self.__internal_div.getNumChildren())]
        for node in internal_div_nodes:
            node.unlink(True)

        self.__device_pointer_config = device_pointer_config
        self.__internal_div = avg.DivNode(parent=self)
        avg.RectNode(
            parent=self.__internal_div,
            strokewidth=0,
            fillcolor=self.__device_pointer_config.device_canvas_color,
            fillopacity=1,
            size=self.__device.size
        )
        avg.WordsNode(
            parent=self.__internal_div,
            text=self.__device_pointer_config.device_canvas_text,
            alignment="center",
            fontsize=self.__device_pointer_config.text_configuration.font_size,
            color=self.__device_pointer_config.text_configuration.color,
            pos=(self.__device.size[0] / 2, self.__device.size[1] / 2))

    def start_listening(self, swipe=None, drag=None, double_tap=None, hold=None, double_tap_hold=None, double_tap_hold_drag=None,
                        double_tap_hold_end=None, cursor_down=None, cursor_motion=None, cursor_up=None):
        """
        Registers a callback to listen to changes to this device view. Listeners can register to any number of the provided
        events. For the required structure of the callbacks see below.

        :param swipe: Called when a swipe to the left was entered.
        :type swipe: function(sender:PointerDeviceView, direction:int)
        :param drag: Called when a drag was entered.
        :type drag: function(sender:PointerDeviceView, offset:tuple[float, float])
        :param double_tap: Called when a double tap was entered.
        :type double_tap: function(sender:PointerDeviceView)
        :param hold: Called when a hold was entered.
        :type hold: function(sender:PointerDeviceView, event:CursorEvent)pass
        :param double_tap_hold: Called when a tap and then a hold has occurred.
        :type double_tap_hold: function(sender:PointerDeviceView, event:CursorEvent)
        :param double_tap_hold_drag: Called when a drag happened after a double tap hold occurred.
        :type double_tap_hold_drag: function(sender:PointerDeviceView, pos_change:tuple[float, float]
        :param double_tap_hold_end: Called when a double tap hold has ended.
        :type double_tap_hold_end: function(sender:PointerDeviceView)
        :param cursor_down: Called when a cursor down event on this view occurred.
        :type cursor_down: function(sender:PointerDeviceView, event:CursorEvent)
        :param cursor_motion: Called when a cursor motion event on this view occurred.
        :type cursor_motion: function(sender:PointerDeviceView, event:CursorEvent)
        :param cursor_up: Called when a cursor up event on this view occurred.
        :type cursor_up: function(sender:PointerDeviceView, event:CursorEvent)
        """
        self.bind(self.__SWIPE, swipe)
        self.bind(self.__DRAG, drag)
        self.bind(self.__DOUBLE_TAP, double_tap)
        self.bind(self.__HOLD, hold)
        self.bind(self.__DOUBLE_TAP_HOLD, double_tap_hold)
        self.bind(self.__DOUBLE_TAP_HOLD_DRAG, double_tap_hold_drag)
        self.bind(self.__DOUBLE_TAP_HOLD_END, double_tap_hold_end)
        self.bind(self.__CURSOR_DOWN, cursor_down)
        self.bind(self.__CURSOR_MOTION, cursor_motion)
        self.bind(self.__CURSOR_UP, cursor_up)

    def stop_listening(self, swipe=None, drag=None, double_tap=None, hold=None, double_tap_hold=None, double_tap_hold_drag=None,
                       double_tap_hold_end=None, cursor_down=None, cursor_motion=None, cursor_up=None):
        """
        Stops listening to an event the listener has registered to previously. The provided callback needs to be the
        same that was used to listen to the event in the fist place.

        :param swipe: Called when a swipe to the left was entered.
        :type swipe: function(sender:PointerDeviceView, direction:int)
        :param drag: Called when a drag was entered.
        :type drag: function(sender:PointerDeviceView, offset:tuple[float, float])
        :param double_tap: Called when a double tap was entered.
        :type double_tap: function(sender:PointerDeviceView)
        :param hold: Called when a hold was entered.
        :type hold: function(sender:PointerDeviceView, event:CursorEvent
        :param double_tap_hold: Called when a tap and then a hold has occurred.
        :type double_tap_hold: function(sender:PointerDeviceView, event:CursorEvent)
        :param double_tap_hold_drag: Called when a drag happened after a double tap hold occurred.
        :type double_tap_hold_drag: function(sender:PointerDeviceView, pos_change:tuple[float, float]
        :param double_tap_hold_end: Called when a double tap hold has ended.
        :type double_tap_hold_end: function(sender:PointerDeviceView)
        :param cursor_down: Called when a cursor down event on this view occurred.
        :type cursor_down: function(sender:PointerDeviceView, event:CursorEvent)
        :param cursor_motion: Called when a cursor motion event on this view occurred.
        :type cursor_motion: function(sender:PointerDeviceView, event:CursorEvent)
        :param cursor_up: Called when a cursor up event on this view occurred.
        :type cursor_up: function(sender:PointerDeviceView, event:CursorEvent)
        """
        self.unbind(self.__SWIPE, swipe)
        self.unbind(self.__DRAG, drag)
        self.unbind(self.__DOUBLE_TAP, double_tap)
        self.unbind(self.__HOLD, hold)
        self.unbind(self.__DOUBLE_TAP_HOLD, double_tap_hold)
        self.unbind(self.__DOUBLE_TAP_HOLD_DRAG, double_tap_hold_drag)
        self.unbind(self.__DOUBLE_TAP_HOLD_END, double_tap_hold_end)
        self.unbind(self.__CURSOR_DOWN, cursor_down)
        self.unbind(self.__CURSOR_MOTION, cursor_motion)
        self.unbind(self.__CURSOR_UP, cursor_up)
