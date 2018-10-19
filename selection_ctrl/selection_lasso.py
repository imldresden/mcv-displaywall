from libavg import avg
from events.event_dispatcher import EventDispatcher
from selection import Selection
import configs.visual_data as vs_config


class SelectionLasso(Selection, EventDispatcher):
    __LASSO_UP = "lassoUp"

    def __init__(self, parent, event):
        """
        This class uses an initial touch event to track subsequent moves draw a line between them in a div node.
        It is mainly used to draw a selection lasso and record a polygon of it. This polygon can later be used to check
        for if the lasso contains nodes.

        Args:
            parent (avg.DivNode): Parent node that should contain the drawn line.
            event (Event): Initial event that is used to track touches / mouse moves.
        """
        EventDispatcher.__init__(self)

        self.__parent = parent
        self.__node = avg.PolygonNode(
            strokewidth=2,
            parent=self.__parent,
            color=vs_config.SELECTION_FEEDBACK_COLOR,
            fillopacity=0.5,
            opacity=0.5,
            fillcolor='ccc',
            sensitive=False,
            pos=[self.__parent.getRelPos((event.x, event.y))]
        )
        self.__event = event
        self.__touch_id = event.cursorid

        self.__event.contact.subscribe(avg.Contact.CURSOR_MOTION, self.__on_move)
        self.__event.contact.subscribe(avg.Contact.CURSOR_UP, self.__on_up)

    def polygon(self, relative_div=None):
        """
        To be used to get the outline of the lasso.

        Returns (list): A list of the recorded positions of move events that make up the lasso path.
        """
        if self.__node is None:
            return []
        if relative_div is not None:
            points = self.__node.pos[:]
            for i in range(len(points)):
                points[i] -= relative_div.pos
            return points
        return self.__node.pos[:]

    def update(self, pos=None, size=None):
        pass

    def clear(self):
        if self.__node:
            self.__node.unlink()
            self.__node = None

        del self

    def __on_up(self, event):
        self.dispatch(self.__LASSO_UP, sender=self, event=event)

        # delete the lasso when the inital touch event ends
        if self.__touch_id == event.contact.id and self.__node is not None:
            self.__event.contact.unsubscribe(avg.Contact.CURSOR_MOTION, self.__on_move)
            self.__event.contact.unsubscribe(avg.Contact.CURSOR_UP, self.__on_up)
            self.__node.unlink(True)

    def __on_move(self, event):
        # add a position to the lasso path
        if self.__touch_id != event.contact.id or self.__node == None:
            return
        pos = self.__node.pos
        # pos.append((event.x, event.y))
        rel_pos = self.__parent.getRelPos((event.x, event.y))
        pos.append(rel_pos)
        self.__node.pos = pos

    def start_listening(self, lasso_up):
        """
        Registers a callback to listen to changes or events of this lasso. Listeners can register to any number of the
        provided events. For the required structure of the callbacks see below.

        :param lasso_up: Called when the contact for the lasso got dispatched an up event.
        :type lasso_up: function(sender:SelectionLasso, event:CursorEvent)
        """
        self.bind(self.__LASSO_UP, lasso_up)

    def stop_listening(self, lasso_up):
        """
        Stops listening to an event the listener has registered to previously. The provided callback needs to be the
        same that was used to listen to the event in the fist place.

        :param lasso_up: Called when the contact for the lasso got dispatched an up event.
        :type lasso_up: function(sender:SelectionLasso, event:CursorEvent)
        """
        self.unbind(self.__LASSO_UP, lasso_up)
