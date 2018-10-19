from libavg import avg

from events.event_dispatcher import EventDispatcher
from libavg_charts.axis.interactive_div_node import InteractiveDivNode


class ChartAxisBase(avg.DivNode, EventDispatcher):
    """
    The base for an axis for a chart. It handles all the events for the axis.
    """
    _AXIS_OR_TICK_TAP = "axisOrTickTap"
    _AXIS_OR_TICK_DRAG_START = "axisOrTickDragStart"
    _AXIS_OR_TICK_DRAG = "axisOrTickDrag"
    _AXIS_OR_TICK_DRAG_END = "axisOrTickDragEnd"
    _MARKING_TAP = "markingTap"
    _MARKING_DRAG_START = "markingDragStart"
    _MARKING_DRAG = "markingDrag"
    _MARKING_DRAG_END = "markingDragEnd"
    _LABEL_OR_UNIT_TAP = "labelOrUnitTap"
    _LABEL_OR_UNIT_DRAG_START = "labelOrUnitDragStart"
    _LABEL_OR_UNIT_DRAG = "labelOrUnitDrag"
    _LABEL_OR_UNIT_DRAG_END = "labelOrUnitDragEnd"

    def __init__(self, parent=None, **kwargs):
        """
        :type parent: DivNode
        :param kwargs: All other parameter for the div node.
        """
        super(ChartAxisBase, self).__init__(**kwargs)
        self.registerInstance(self, parent)
        EventDispatcher.__init__(self)

        self._marking_div = InteractiveDivNode(parent=self)
        self._marking_div.start_listening(
            clicked=self._on_tap,
            drag_started=self._on_drag_start,
            dragged=self._on_drag,
            drag_ended=self._on_drag_end
        )
        self._label_and_unit_div = InteractiveDivNode(parent=self)
        self._label_and_unit_div.start_listening(
            clicked=self._on_tap,
            drag_started=self._on_drag_start,
            dragged=self._on_drag,
            drag_ended=self._on_drag_end
        )
        self._axis_and_tick_div = InteractiveDivNode(parent=self)
        self._axis_and_tick_div.start_listening(
            clicked=self._on_tap,
            drag_started=self._on_drag_start,
            dragged=self._on_drag,
            drag_ended=self._on_drag_end
        )

    def _on_tap(self, sender, event):
        """
        Called when an div node in this axis was clicked.

        :type sender: InteractiveDivNode
        :type event: avg.CursorEvent
        """
        if sender is self._axis_and_tick_div:
            self.dispatch(self._AXIS_OR_TICK_TAP, sender=self)
            # Check if an marking lies under the axis or tick div.
            marking_node = self._marking_div.getElementByPos(self.getRelPos(event.pos))
            if marking_node:
                self.dispatch(self._MARKING_TAP, sender=self, marking_node=marking_node)
        elif sender is self._marking_div:
            marking_node = self._marking_div.getElementByPos(self.getRelPos(event.pos))
            self.dispatch(self._MARKING_TAP, sender=self, marking_node=marking_node)
        elif sender is self._label_and_unit_div:
            self.dispatch(self._LABEL_OR_UNIT_TAP, sender=self)

    def _on_drag_start(self, sender):
        """
        Called when a drag on a div node has started.

        :type sender: InteractiveDivNode
        """
        if sender is self._axis_and_tick_div:
            self.dispatch(self._AXIS_OR_TICK_DRAG_START, sender=self)
        elif sender is self._marking_div:
            self.dispatch(self._MARKING_DRAG_START, sender=self)
        elif sender is self._label_and_unit_div:
            self.dispatch(self._LABEL_OR_UNIT_DRAG_START, sender=self)

    def _on_drag(self, sender, pos_change):
        """
        Called when a div node in this axis was dragged.

        :type sender: InteractiveDivNode
        :type pos_change: tuple[float, float]
        """
        if sender is self._axis_and_tick_div:
            self.dispatch(self._AXIS_OR_TICK_DRAG, sender=self, pos_change=pos_change)
        elif sender is self._marking_div:
            self.dispatch(self._MARKING_DRAG, sender=self, pos_change=pos_change)
        elif sender is self._label_and_unit_div:
            self.dispatch(self._LABEL_OR_UNIT_DRAG, sender=self, pos_change=pos_change)

    def _on_drag_end(self, sender, pos_change):
        """
        Called when a drag on a div node has ended.

        :type sender: InteractiveDivNode
        :type pos_change: tuple[float, float]
        """
        if sender is self._axis_and_tick_div:
            self.dispatch(self._AXIS_OR_TICK_DRAG_END, sender=self, pos_change=pos_change)
        elif sender is self._marking_div:
            self.dispatch(self._MARKING_DRAG_END, sender=self, pos_change=pos_change)
        elif sender is self._label_and_unit_div:
            self.dispatch(self._LABEL_OR_UNIT_DRAG_END, sender=self, pos_change=pos_change)

    def start_listening(self, axis_or_tick_tap=None, marking_tap=None, label_or_unit_tap=None,
                        axis_or_tick_drag_start=None, marking_drag_start=None, label_or_unit_drag_start=None,
                        axis_or_tick_drag=None, marking_drag=None, label_or_unit_drag=None,
                        axis_or_tick_drag_end=None, marking_drag_end=None, label_or_unit_drag_end=None):
        """
        Registers a callback to listen to changes to this axis. Listeners can register to any number of the provided
        events. For the required structure of the callbacks see below.

        :param axis_or_tick_tap: Called when the axis or the ticks are clicked.
        :type axis_or_tick_tap: function(sender:ChartAxisBase)
        :param marking_tap: Called when the markings are clicked.
        :type marking_tap: function(sender:ChartAxisBase)
        :param label_or_unit_tap: Called when the label or the unit are clicked.
        :type label_or_unit_tap: function(sender:ChartAxisBase)
        :param axis_or_tick_drag_start: Called when a drag event has started on the axis or the ticks.
        :type axis_or_tick_drag_start: function(sender:ChartAxisBase)
        :param marking_drag_start: Called when a drag event has started on the markings.
        :type marking_drag_start: function(sender:ChartAxisBase)
        :param label_or_unit_drag_start: Called when a drag event has started on the label or the unit.
        :type label_or_unit_drag_start: function(sender:ChartAxisBase)
        :param axis_or_tick_drag: Called when the axis or the ticks are dragged.
        :type axis_or_tick_drag: function(sender:ChartAxisBase, pos_change:tuple[float, float])
        :param marking_drag: Called when the markings are dragged.
        :type marking_drag: function(sender:ChartAxisBase, pos_change:tuple[float, float])
        :param label_or_unit_drag: Called when the label or the unit are dragged.
        :type label_or_unit_drag: function(sender:ChartAxisBase, pos_change:tuple[float, float])
        :param axis_or_tick_drag_end: Called when a drag event has ended on the axis or the ticks.
        :type axis_or_tick_drag_end: function(sender:ChartAxisBase, pos_change:tuple[float, float])
        :param marking_drag_end: Called when a drag event has ended on the markings.
        :type marking_drag_end: function(sender:ChartAxisBase, pos_change:tuple[float, float])
        :param label_or_unit_drag_end: Called when a drag event has ended on the unit or the label.
        :type label_or_unit_drag_end: function(sender:ChartAxisBase, pos_change:tuple[float, float])
        """
        self.bind(self._AXIS_OR_TICK_TAP, axis_or_tick_tap)
        self.bind(self._MARKING_TAP, marking_tap)
        self.bind(self._LABEL_OR_UNIT_TAP, label_or_unit_tap)
        self.bind(self._AXIS_OR_TICK_DRAG_START, axis_or_tick_drag_start)
        self.bind(self._MARKING_DRAG_START, marking_drag_start)
        self.bind(self._LABEL_OR_UNIT_DRAG_START, label_or_unit_drag_start)
        self.bind(self._AXIS_OR_TICK_DRAG, axis_or_tick_drag)
        self.bind(self._MARKING_DRAG, marking_drag)
        self.bind(self._LABEL_OR_UNIT_DRAG, label_or_unit_drag)
        self.bind(self._AXIS_OR_TICK_DRAG_END, axis_or_tick_drag_end)
        self.bind(self._MARKING_DRAG_END, marking_drag_end)
        self.bind(self._LABEL_OR_UNIT_DRAG_END, label_or_unit_drag_end)

    def stop_listening(self, axis_or_tick_tap=None, marking_tap=None, label_or_unit_tap=None,
                       axis_or_tick_drag_start=None, marking_drag_start=None, label_or_unit_drag_start=None,
                       axis_or_tick_drag=None, marking_drag=None, label_or_unit_drag=None,
                       axis_or_tick_drag_end=None, marking_drag_end=None, label_or_unit_drag_end=None):
        """
        Stops listening to an event the listener has registered to previously. The provided callback needs to be the
        same that was used to listen to the event in the fist place.

        :param axis_or_tick_tap: Called when the axis or the ticks are clicked.
        :type axis_or_tick_tap: function(sender:ChartAxisBase)
        :param marking_tap: Called when the markings are clicked.
        :type marking_tap: function(sender:ChartAxisBase)
        :param label_or_unit_tap: Called when the label or the unit are clicked.
        :type label_or_unit_tap: function(sender:ChartAxisBase)
        :param axis_or_tick_drag_start: Called when a drag event has started on the axis or the ticks.
        :type axis_or_tick_drag_start: function(sender:ChartAxisBase)
        :param marking_drag_start: Called when a drag event has started on the markings.
        :type marking_drag_start: function(sender:ChartAxisBase)
        :param label_or_unit_drag_start: Called when a drag event has started on the label or the unit.
        :type label_or_unit_drag_start: function(sender:ChartAxisBase)
        :param axis_or_tick_drag: Called when the axis or the ticks are dragged.
        :type axis_or_tick_drag: function(sender:ChartAxisBase, pos_change:tuple[float, float])
        :param marking_drag: Called when the markings are dragged.
        :type marking_drag: function(sender:ChartAxisBase, pos_change:tuple[float, float])
        :param label_or_unit_drag: Called when the label or the unit are dragged.
        :type label_or_unit_drag: function(sender:ChartAxisBase, pos_change:tuple[float, float])
        :param axis_or_tick_drag_end: Called when a drag event has ended on the axis or the ticks.
        :type axis_or_tick_drag_end: function(sender:ChartAxisBase, pos_change:tuple[float, float])
        :param marking_drag_end: Called when a drag event has ended on the markings.
        :type marking_drag_end: function(sender:ChartAxisBase, pos_change:tuple[float, float])
        :param label_or_unit_drag_end: Called when a drag event has ended on the unit or the label.
        :type label_or_unit_drag_end: function(sender:ChartAxisBase, pos_change:tuple[float, float])
        """
        self.unbind(self._AXIS_OR_TICK_TAP, axis_or_tick_tap)
        self.unbind(self._MARKING_TAP, marking_tap)
        self.unbind(self._LABEL_OR_UNIT_TAP, label_or_unit_tap)
        self.unbind(self._AXIS_OR_TICK_DRAG_START, axis_or_tick_drag_start)
        self.unbind(self._MARKING_DRAG_START, marking_drag_start)
        self.unbind(self._LABEL_OR_UNIT_DRAG_START, label_or_unit_drag_start)
        self.unbind(self._AXIS_OR_TICK_DRAG, axis_or_tick_drag)
        self.unbind(self._MARKING_DRAG, marking_drag)
        self.unbind(self._LABEL_OR_UNIT_DRAG, label_or_unit_drag)
        self.unbind(self._AXIS_OR_TICK_DRAG_END, axis_or_tick_drag_end)
        self.unbind(self._MARKING_DRAG_END, marking_drag_end)
        self.unbind(self._LABEL_OR_UNIT_DRAG_END, label_or_unit_drag_end)
