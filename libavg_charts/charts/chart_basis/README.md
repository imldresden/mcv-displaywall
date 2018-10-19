## ChartBase
Base: [libavg.avg.DivNode], `EventDispatcher`

The base for all possible charts that could be created with this library.

### Member

+ **ChartBase(data : list[MultivariateDataObject], label : str, [chart_config : ChartConfiguration, parent : DivNode], 
              \*\*kwargs)**  


+ **horizontal_axis_data : dict[str, DataDescription]**  
    Readonly. A dict of all `DataDescrition` for horizontal axis in this chart. The key is the label of the axis data 
    descriptor.
+ **vertical_axis_data : dict[str, DataDescription]**  
    Readonly. A dict of all `DataDescrition` for vertical axis in this chart. The key is the label of the axis data 
    descriptor.
+ **horizontal_axis_views : dict[str, ChartAxis]**  
    Readonly. A dict with all `ChartAxis` for the horizontal axis in this chart. The key is the label of the axis.
+ **vertical_axis_views : dict[str, ChartAxis]**  
    Readonly. A dict with all `ChartAxis` for the vertical axis in this chart. The key is the label of the axis.


+ **draw_chart()**
    Draws and also redraws this chart if called.
+ **add_aid_line_controller(aid_line_controller_type)**  
    Abstract. Adds a new aid line controller with the given type to the chart.
+ **remove_aid_line_controller(aid_line_controller_type)**  
    Removes an already added aid line controller with the given type from the chart.
+ **set_aid_line_controller_attributes(aid_line_controller_type, [\*\*kwargs])**  
    Sets different attributes, given in the `**kwargs`, for a aid controller with the given type. If no 
    `aid_line_controller_type` is given, all aid line controller will set the new value for an attribute. For the 
    attributes to set look at the set able members of all children of `AidLineControllerBase`. 
+ **invoke_aid_line_controller_event(event_name, [aid_line_controller_type, \*\*kwargs])**  
    Invokes an event with the given event name from the given aid line controller with the additional parameters from 
    `**kwargs`. If no `aid_line_controller_type` is given, all aid line controller will invoke the event. For the events
     to invoke look at all children of `AidLineControllerBase`.
    
## TwoAxisChart
Base: `charts.chart_basis.ChartBase`

A simple base for all charts with to axis. One horizontal and one vertical. They will always be at the left and the 
bottom.

### Member

+ **TwoAxisChart(x_axis_data : DataDescription, y_axis_data : DataDescription, size : tuple[float, float], [x_axis_config
                 : ChartAxisConfiguration, y_axis_config : ChartAxisConfiguration], \*\*kwargs)**


+ **data_object_nodes : dict[str, libavg.avg.Node]**  
    Readonly. A dict with all nodes for the data objects that are represented through the chart. The key is the data 
    object name.


+ **add_aid_line_controller(aid_line_controller_type)**  
    Look at `charts.chart_basis.ChartBase`.
    
## BarChartBase
Base: `charts.chart_basis.TwoAxisChart`

The base for bar charts with two axis.

### Member

+ **BarChartBase([bar_line_width : float, bar_spacing : float], \*\*kwargs)**
    
    
[libavg.avg.DivNode]: https://www.libavg.de/reference/svn/areanodes.html?highlight=divnode#libavg.avg.DivNode
