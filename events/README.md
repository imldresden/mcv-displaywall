## EventDispatcher

A helper class that can handle events and their binding, unbinding and dispatching.

### Member

+ **SHOW_MESSAGES=False**  
    Should messages of the dispatching, binding and unbinding of events be shown in the console?
+ **SHOW_ERROR_MESSAGES=True**  
    Should messages of the errors that can be occur in the different methods be shown in the console?
    
  
+ **bind(event_name, callable_method)**  
    Adds a new method for a given event name to the event dispatcher.
+ **unbind(event_name, callable_method)**  
    Removes a given method from the given event name.
+ **unbind_all_from_one_event(event_name)**  
    Remove all events from a given event name.
+ **dispatch(event_name, \*\*kwargs)**  
    Calls all events connected to the event name. All arguments in \*\*kwargs will be used as parameters for the methods.
+ **dispatch_with_returns(event_name, \*\*kwargs)**  
    Works as `dispatch()`. The only different is, that events can return values. Those returned values will be returned 
    through this method with a yield statement.