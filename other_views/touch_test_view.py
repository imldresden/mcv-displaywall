from libavg import avg, player
from libavg.avg import CursorEvent
from events.event_dispatcher import EventDispatcher


class TouchTestView(avg.DivNode, EventDispatcher):
    __ALL_NODES_CLICKED = "allNodesClicked"

    def __init__(self, parent=None, **kwargs):
        super(TouchTestView, self).__init__(**kwargs)
        self.registerInstance(self, parent)
        EventDispatcher.__init__(self)

        self.__touch_count = 0
        self.__rect_nodes = []
        rect_size = self.size[0] / 4, self.size[1] / 3
        for y in range(3):
            y = rect_size[1] * y
            for x in range(4):
                x = rect_size[0] * x
                rect_node = avg.RectNode(
                    parent=self,
                    pos=(x, y),
                    size=rect_size,
                    fillcolor="8c0707",
                    fillopacity=1,
                    strokewidth=0
                )
                rect_node.subscribe(avg.Node.CURSOR_DOWN, self.__on_cursor_down)

    def __on_cursor_down(self, event):
        """
        :type event: CursorEvent
        """
        event.node.sensitive = False
        event.node.fillcolor = "046d0e"
        self.__touch_count += 1

        if self.__touch_count >= 12:
            player.setTimeout(1, (lambda: self.dispatch(self.__ALL_NODES_CLICKED, sender=self)))

    def start_listening(self, all_nodes_clicked=None):
        self.bind(self.__ALL_NODES_CLICKED, all_nodes_clicked)

    def stop_listening(self, all_nodes_clicked=None):
        self.unbind(self.__ALL_NODES_CLICKED, all_nodes_clicked)
