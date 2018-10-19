## AidLineType
Base: `Enum`

The possible aid line controller that can be created.

The values are: AxisDragX, AxisDragY, Cursor, CursorHorizontal, CursorVertical, SelectionHorizontal, SelectionVertical,
Selection, CircleSelection

### Member

+ **can_select(aid_line_type) : bool**  
    Static. Checks if the given type can output a selection.

## AidLineLabelPos
Base: `Enum`

The position of the label for the aid lines. Top is at horizontal aid lines the right side, bottom the right.

The values are: Top, Bottom.

## AidLineControllerBase
Base: `EventDispatcher`

The base class for all aid line controllers.

### Member

+ **AidLineControllerBase(chart : ChartBase, aid_line_area : tuple[float, ...], [use_tick_snapping : bool, 
                          aid_line_config : AidLineConfiguration, intersection_config : IntersectionConfiguration])**


+ **aid_line_area : tuple**  
    The area in that the aid lines can be created and used.
+ **show_intersections : bool**  
    Forwarding from a `IntersectionConfiguration` object.
+ **show_intersection_labels : bool**  
    Forwarding from a `IntersectionConfiguration` object.
+ **show_aid_line_labels : bool**  
    Forwarding from a `AidLineConfiguration` object.
+ **use_tick_snapping : bool**  
    Should a aid line be snapping to the ticks of an axis?
+ **aid_line_config : AidLineConfiguration**  
    The configuration used to create aid lines.
+ **intersection_config : IntersectionConfiguration**  
    The configuration used to create intersections.
    
    
+ **set_attributes(\*\*kwargs)**  
    Sets, if possible, different attributes of this aid line controller.
+ **invoke_event(event_name, \*\*kwargs)**  
    Invokes an event for this aid line controller. Necessary parameters can be placed in `**kwargs`.
+ **delete()**
    Delete this controller and removes all events from the chart.

## AxisDragAidLine
Base: `AidLineControllerBase`

Special controller that allows the user to create an aid line with a drag on an axis.

### Member

+ **AxisDragAidLine(orientation : Orientation, [aid_line_to_axis_offset : float], \*\*kwargs)**


+ **orientation : Orientation**  
    The orientation this controller should be watch.
    
## CircleSelectionAidLine
Base: `AidLineControllerBase`

Special controller that uses a circle aid line and allows the user the select a subset of data objects through the 
circle.

### Member

+ **start_listening([data_objects_selected])**  
    Registers different callbacks to listen to changes on the circle selection aid line controller.
+ **stop_listening([data_objects_selected])**  
    Removes different callbacks from listening to changes from the circle selection aid line controller.

## CursorAidLine
Base: `AidLineControllerBase`

Special controller that follows the cursor of a user and draws a aid line horizontal and vertical.

## CursorHorizontalAidLine
Base: `CursorAidLine`

Only allows the cursor to draw a horizontal aid line.

## CursorVerticalAidLine
Base: `CursorAidLine`

Only allows the cursor to draw a vertical aid line.

## SelectionAidLine
Base: `CursorAidLine`

Special controller that allows the user to select an area in the chart through a click and hold. It will create through
this interaction a rectangle that will be used to select the data objects.

### Member

+ **SelectionAidLine([selection_line_config : SelectionLineConfiguration], \*\*kwargs)**


+ **selection_line_config : SelectionLineConfiguration**  
    The configuration used to create selection aid lines.
    
    
+ **start_listening([data_objects_selected])**  
    Registers different callbacks to listen to changes on the selection aid line controller.
+ **stop_listening([data_objects_selected])**  
    Removes different callbacks from listening to changes from the selection aid line controller.
    
## SelectionHorizontalAidLine
Base: `SelectionAidLine`

Only allows a horizontal selection and an aid line. The selection will select all data objects that are between the y 
values. 
    
## SelectionVerticalAidLine
Base: `SelectionAidLine`

Only allows a vertical selection and an aid line. The selection will select all data objects that are between the x 
values. 