## IntersectionMethodHolder

A class that holds all methods for the calculation of intersections with the aid lines on a chart.
This class will be used in the aid line controllers.

### Member

+ **add_intersection_method(diagram_type, line_orientation, intersection_method)**  
    Adds a new method for the diagram type and the orientation of the line to this class.
+ **get_intersection_with_data_objects(diagram_type, line_orientation, data_objects, line_pos)**  
    Calculates all intersections from the aid line (given through the `line_pos`) with the data objects (as a list of 
    nodes for the data object). It will return a dict with the data object nodes as keys and the intersection pos as 
    value.

## SelectionTypes
Base: `Enum`

The possible selection types that can occur from a aid line controller.

The values are: HorizontalLine, VerticalLine, Rectangle, Circle

## SelectionMethodHolder

A class that holds all methods for the calculation of selections with the aid lines on a chart.
This class will be used in the aid line controllers.

### Member

+ **add_selection_method(diagram_type, selection_type, selection_method)**  
    Adds a new method for the diagram type and the selection type.
+ **get_intersection_with_data_objects(diagram_type, selection_type, data_objects, value1, value2)**  
    Calculates all selected data objects (given as a dict with name of node as key and the node itself as value). The 
    selection will be represented through the `value1` and `value2` parameters.
    + `value1` is one side of a line/rect selection or the pos of the circle.
    + `value2` is the other side of a line/rect selection or the radius of the circle.
    
    It will return the same structure as the `data_object` parameter.

## intersection_methods.py

File that has written in all the default methods for the intersection calculation of data objects and aid lines.

### Member

+ **add_intersection_methods_to_method_holder()**  
    Adds the default intersection methods to the `IntersectionMethodHolder`.
+ **get_intersection_line_chart_horizontal(data_objects, line_pos)**  
    Calculates intersection between a `LineChart` and a horizontal aid line.
+ **get_intersection_line_chart_vertical(data_objects, line_pos)**  
    Calculates intersection between a `LineChart` and a vertical aid line.
+ **get_intersection_bar_chart_horizontal(data_objects, line_pos)**  
    Calculates intersection between a `BarChartBase` and a horizontal aid line.
+ **get_intersection_bar_chart_vertical(data_objects, line_pos)**  
    Calculates intersection between a `BarChartBase` and a vertical aid line.
+ **get_intersection_scatter_plot_horizontal(data_objects, line_pos)**  
    Calculates intersection between a `ScatterPlot` and a horizontal aid line.
+ **get_intersection_scatter_plot_vertical(data_objects, line_pos)**  
    Calculates intersection between a `ScatterPlot` and a vertical aid line.
    
## selection_methods.py

File that has written in all the default methods for the selection calculation of data objects and aid lines. For the
definition of the parameters for the selection methods look at 
`SelectionMethodHolder.get_intersection_with_data_objects()`.

### Member

+ **add_selection_methods_to_method_holder()**  
    Adds the default intersection methods to the `SelectionMethodHolder`.
+ **get_selection_line_chart_horizontal_rect(data_objects, value1, value2)**  
    Calculates the selection of data objects in a `LineChart` that lies in a horizontal rect, given through horizontal 
    aid lines.
+ **get_selection_line_chart_vertical_rect(data_objects, value1, value2)**  
    Calculates the selection of data objects in a `LineChart` that lies in a vertical rect, given through vertical 
    aid lines.
+ **get_selection_line_chart_rect(data_objects, value1, value2)**  
    Calculates the selection of data objects in a `LineChart` that lies in a arbitrary rect, given through vertical and 
    horizontal aid lines.
+ **get_selection_bar_chart_horizontal_rect(data_objects, value1, value2)**  
    Calculates the selection of data objects in a `BarChartBase` that lies in a horizontal rect, given through horizontal 
    aid lines.
+ **get_selection_bar_chart_vertical_rect(data_objects, value1, value2)**  
    Calculates the selection of data objects in a `BarChartBase` that lies in a vertical rect, given through vertical 
    aid lines.
+ **get_selection_bar_chart_rect(data_objects, value1, value2)**  
    Calculates the selection of data objects in a `BarChartBase` that lies in a arbitrary rect, given through vertical 
    and horizontal aid lines.
+ **get_selection_scatter_plot_horizontal_rect(data_objects, value1, value2)**  
    Calculates the selection of data objects in a `ScatterPlot` that lies in a horizontal rect, given through horizontal 
    aid lines.
+ **get_selection_scatter_plot_vertical_rect(data_objects, value1, value2)**  
    Calculates the selection of data objects in a `ScatterPlot` that lies in a vertical rect, given through vertical 
    aid lines.
+ **get_selection_scatter_plot_rect(data_objects, value1, value2)**  
    Calculates the selection of data objects in a `ScatterPlot` that lies in a arbitrary rect, given through vertical 
    and horizontal aid lines.
+ **get_selection_scatter_plot_circle(data_objects, value1, value2)**  
    Calculates the selection of data objects in a `ScatterPlot` that lies in a circle, given through a circle aid line.
