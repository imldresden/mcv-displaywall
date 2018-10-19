from libavg import avg, gesture, player

from configs.config_recognizer import CommonRecognizerDefaults
from events.event_dispatcher import EventDispatcher


class InteractiveDivNode(avg.DivNode, EventDispatcher):
    """
    An UI element that can handle user input.
    """
    __CLICKED = "clicked"
    __DRAG_STARTED = "dragStarted"
    __DRAGGED = "dragged"
    __DRAG_ENDED = "dragEnded"

    def __init__(self, parent=None, **kwargs):
        super(InteractiveDivNode, self).__init__(**kwargs)
        self.registerInstance(self, parent)
        EventDispatcher.__init__(self)

        self.__drag_recognizer = gesture.DragRecognizer(
            eventNode=self,
            minDragDist=CommonRecognizerDefaults.DRAG_MIN_DIST,
            detectedHandler=self._on_drag_started,
            moveHandler=self._on_drag,
            upHandler=self._on_drag_ended,
            friction=-1
        )
        self.subscribe(avg.Node.CURSOR_DOWN, self.__on_cursor_down)
        self.subscribe(avg.Node.CURSOR_UP, self.__on_cursor_up)

        self._drag_start_pos = 0, 0
        self._last_drag_change = 0, 0

        # key -> event id     value -> start time
        self.__down_events = {}

    @property
    def drag_start_pos(self):
        """
        :rtype: tuple[float, float]
        """
        return self._drag_start_pos

    @drag_start_pos.setter
    def drag_start_pos(self, value):
        """
        :type value: tuple[float, float]
        """
        self._drag_start_pos = value

    @property
    def last_absolute_drag_offset(self):
        """
        :rtype: tuple[float, float]
        """
        return self._last_drag_change

    def __on_cursor_down(self, event):
        """
        :type event: avg.CursorEvent
        """
        if event.cursorid in self.__down_events:
            return

        self.__down_events[event.cursorid] = player.getFrameTime()

    def __on_cursor_up(self, event):
        """
        :type event: avg.CursorEvent
        """
        if event.cursorid not in self.__down_events:
            return

        start_time = self.__down_events.pop(event.cursorid)
        if player.getFrameTime() - start_time <= CommonRecognizerDefaults.TAP_MAX_TIME:
            if event.contact.distancefromstart <= CommonRecognizerDefaults.TAP_MAX_DIST:
                self.dispatch(self.__CLICKED, sender=self, event=event)

    def _on_drag_started(self):
        """
        Called whenever a drag event has started.
        """
        self._last_drag_change = 0, 0
        self._drag_start_pos = self.pos
        self.dispatch(self.__DRAG_STARTED, sender=self)

    def _on_drag(self, offset):
        """
        Called whenever the drag event, after it has started, occurred.

        :param offset: The offset the node has from its position before the drag has started.
        :type offset: tuple[int, int]
        """
        pos_change = offset[0] - self._last_drag_change[0], offset[1] - self._last_drag_change[1]
        self._last_drag_change = offset
        self.dispatch(self.__DRAGGED, sender=self, pos_change=pos_change)

    def _on_drag_ended(self, offset):
        """
        Called whenever the drag event hast ended.

        :param offset: The offset the node has from its position before the drag has started.
        :type offset: tuple[int, int]
        """
        pos_change = offset[0] - self._last_drag_change[0], offset[1] - self._last_drag_change[1]
        self.dispatch(self.__DRAG_ENDED, sender=self, pos_change=pos_change)

    def start_listening(self, clicked=None, drag_started=None, dragged=None, drag_ended=None):
        """
        Registers a callback to listen to changes to this div node. Listeners can register to any number of the provided
        events. For the required structure of the callbacks see below.

        :param clicked: Called when this div node was clicked.
        :type clicked: function(sender:InteractiveDivNode, event:CursorEvent)
        :param drag_started: Called when a drag on this div has started.
        :type drag_started: function(sender:InteractiveDivNode)
        :param dragged: Called when this div node was dragged.
        :type dragged: function(sender:InteractiveDivNode, pos_change:tuple[float, float])
        :param drag_ended: Called when a drag on this div has ended.
        :type drag_ended: function(sender:InteractiveDivNode, pos_change:tuple[float, float])
        """
        self.bind(self.__CLICKED, clicked)
        self.bind(self.__DRAG_STARTED, drag_started)
        self.bind(self.__DRAGGED, dragged)
        self.bind(self.__DRAG_ENDED, drag_ended)

    def stop_listening(self, clicked=None, drag_started=None, dragged=None, drag_ended=None):
        """
        Stops listening to an event the listener has registered to previously. The provided callback needs to be the
        same that was used to listen to the event in the fist place.

        :param clicked: Called when this div node was clicked.
        :type clicked: function(sender:InteractiveDivNode, event:CursorEvent)
        :param drag_started: Called when a drag on this div has started.
        :type drag_started: function(sender:InteractiveDivNode)
        :param dragged: Called when this div node was dragged.
        :type dragged: function(sender:InteractiveDivNode, pos_change:tuple[float, float])
        :param drag_ended: Called when a drag on this div has ended.
        :type drag_ended: function(sender:InteractiveDivNode, pos_change:tuple[float, float])
        """
        self.unbind(self.__CLICKED, clicked)
        self.unbind(self.__DRAG_STARTED, drag_started)
        self.unbind(self.__DRAGGED, dragged)
        self.unbind(self.__DRAG_ENDED, drag_ended)
