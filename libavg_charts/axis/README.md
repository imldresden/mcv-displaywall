## ChartAxisEnums

Different enums for the usage with an axis.

### Enums

+ **Orientation** In which direction should the axis be facing.      
    Horizontal, Vertical
+ **DataDirection** In which direction should the data be positioned.  
    Positive, Negative
+ **MarkingSide** On which side of an axis should be the marking placed.  
    Left, Right
+ **TickSide** On which side of an axis should the ticks be placed.  
    Left, Center, Right
    
## ChartAxisBase
Base: [libavg.avg.DivNode], `events.EventDispatcher`

The base for all chart axis. It provides the possibility to interact with an axis. It can be provide interactions for 
clicking and dragging in the axis (with the ticks), the label and the marking.

### Member

+ **ChartAxisBase([parent : DivNode], \*\*kwargs)**


+ **start_listening([axis_or_tick_click, marking_click, label_or_unit_click, axis_or_tick_drag_start, marking_drag_start, label_or_unit_drag_start, axis_or_tick_drag, marking_drag, label_or_unit_drag, axis_or_tick_drag_end, marking_drag_end, label_or_unit_drag_end])**  
    Registers different callbacks to listen to changes on the chart axis base.
+ **stop_listening([axis_or_tick_click, marking_click, label_or_unit_click, axis_or_tick_drag_start, marking_drag_start, label_or_unit_drag_start, axis_or_tick_drag, marking_drag, label_or_unit_drag, axis_or_tick_drag_end, marking_drag_end, label_or_unit_drag_end])**  
    Removes different callbacks from listening to changes from the chart axis base.
    
## InteractiveDivNode
Base: [libavg.avg.DivNode], `events.EventDispatcher`

A specialized node class from libavg, which has several events to listen.

### Member

+ **InteractiveDivNode([parent : DivNode], \*\*kwargs)**


+ **start_listening([clicked, drag_started, dragged, drag_ended])**  
    Registers different callbacks to listen to changes on the interactive div node.
+ **stop_listening([clicked, drag_started, dragged, drag_ended])**  
    Removes different callbacks from listening to changes from the interactive div node.
    
## ChartAxis
Base: `charts.components.ChartAxisBase`

Represents an axis for any kind of chart. It can be customized in many ways.

### Member

+ **ChartAxis(data_desc : DataDescription, axis_length : float, [axis_config : ChartAxisConfiguration, parent : 
              DivNode], \*\*kwargs)**
        

+ **tick_distance : float**  
    Readonly. The distance between each tick on the axis.
+ **tick_positions : list[float]**  
    Readonly. All positions of the ticks on the axis. Descending order.
+ **axis_length : float**  
    Readonly. The length of the axis without the label or other components.
+ **axis_size : tuple[float, float]**  
    Readonly. The whole size of the axis. Without the label or other components.
+ **complete_axis_size : tuple[float, float]**  
    Readonly. The complete size this axis can have. It also includes the label and other components.
+ **data_desc : DataDescription**  
    Readonly. The `DataDescription` that was used to create this axis. The axis only works with data objects with this 
    kind of data.
    
    
+ **get_pos_from_data_value(data_value, [add_to_pos=True])**  
    Calculates the position of a value on the axis. The calculations will use all the offsets, labels and other 
    components and will return the position on the whole axis.
+ **get_data_value_from_pos(pos, [subtract_from_pos=True])**  
    Calculates the data value from the given position on the axis. The calculation will use all the offsets, labels and
    other components and will return the correct data value.

[libavg.avg.DivNode]: https://www.libavg.de/reference/svn/areanodes.html?highlight=divnode#libavg.avg.DivNode
