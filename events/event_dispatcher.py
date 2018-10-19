class EventDispatcher(object):

    # Static members that tell if the event output should be shown or not
    SHOW_MESSAGES = False
    SHOW_ERROR_MESSAGES = True
    CATCH_EXCEPTIONS = True

    def __init__(self):
        self._events = {}

    def bind(self, event_name, callable_method):
        """
        Adds a new method to a event name.

        :param event_name: The name of a event.
        :type event_name: str
        :param callable_method: The method to call if this event is dispatched.
        :type callable_method:
        """
        if callable_method is not None:
            try:
                if callable_method in self._events[event_name]:
                    if self.SHOW_MESSAGES:
                        print "Already Bound", str(callable_method), "to event", event_name
                    return
                # Add a new event method
                self._events[event_name].append(callable_method)
            except KeyError:
                # If no events with the name was added yet, add it
                self._events[event_name] = [callable_method]

            if self.SHOW_MESSAGES:
                print "Bound", str(callable_method), "to event", event_name

    def unbind(self, event_name, callable_method):
        """
        Remove a method from a beforehand added event (name).

        :param event_name: The name if a event.
        :type event_name: str
        :param callable_method: The method to remove from the event.
        :type callable_method:
        """
        if callable_method is not None:
            try:
                # Delete a event method
                self._events[event_name].remove(callable_method)
                if len(self._events[event_name]) is 0:
                    self._events.pop(event_name)
            except KeyError as inst:
                if self.CATCH_EXCEPTIONS:
                    if self.SHOW_ERROR_MESSAGES:
                        print "Not a registered callback of event" + event_name
                else:
                    raise KeyError(inst)

    def _unbind_all_from_one_event(self, event_name):
        """
        Remove all method from a event (name).

        :param event_name: The name if a event.
        :type event_name: str
        """
        if event_name in self._events:
            self._events.pop(event_name)

    def _unbind_all(self):
        """
        Remove all methods for events.
        """
        self._events.clear()

    def dispatch(self, event_name, **kwargs):
        """
        Calls all events associated with the given event name. It sends all other parameter straight to the methods.

        :param event_name: The event name.
        :type event_name: str
        :param kwargs: All arguments that the methods associated to this event need.
        """
        if event_name not in self._events:
            return

        if self.SHOW_MESSAGES:
            # Print all arguments and there value of this event
            print event_name + ": ", self._events[event_name]
            for arg in kwargs.iteritems():
                print "-", arg

        for callback in self._events[event_name]:
            try:
                callback(**kwargs)
            except Exception as inst:
                if self.CATCH_EXCEPTIONS:
                    if self.SHOW_ERROR_MESSAGES:
                        print "ERROR:", str(inst), "in", event_name, "from method", callback
                else:
                    raise Exception(inst)

    def dispatch_with_returns(self, event_name, **kwargs):
        """
        A generator for all returns the methods can give.
        Calls all events associated with the given event name. It sends all other parameter straight to the methods.

        :param event_name: The event name.
        :type event_name: str
        :param kwargs: All arguments that the methods associated to this event need.
        :returns: The next return value of all methods bind to this event.
        :rtype:
        """
        if event_name not in self._events:
            return

        if self.SHOW_MESSAGES:
            # Print all arguments and there value of this event
            print "yield", event_name + ": ", self._events[event_name]
            for arg in kwargs.iteritems():
                print "-", arg

        for callback in self._events[event_name]:
            try:
                # Returns all return values of the methods for this event.
                yield callback(**kwargs)
            except Exception as inst:
                if self.CATCH_EXCEPTIONS:
                    if self.SHOW_ERROR_MESSAGES:
                        print "ERROR:", str(inst), "in", event_name, "from method", callback
                else:
                    raise Exception(inst)

