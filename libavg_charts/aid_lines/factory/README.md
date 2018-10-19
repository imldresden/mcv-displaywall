## AidLineControllerFactory

A class that can create a new aid line controller. It holds all methods to do so.

+ **add_aid_line_method(aid_line_type, creation_methods)**  
    Adds a new method for the aid line type of the controller to this class.
+ **def create_aid_line_controller(aid_line_type, chart, aid_line_area, \*\*kwargs)**  
    Creates a new aid line controller from the given type. It will work on the chart and in the given area. Its possible
    to give the creation method more parameters.
    
## aid_line_to_factory.py

File that contains methods to create different aid line controllers.

### Member

+ **add_aid_lines_to_factory()**  
    Adds the default aid line controller creation methods to the `AidLineControllerFactory`.