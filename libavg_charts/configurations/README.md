## AidLineConfiguration

A class that can save all necessary attributes for aid line representations.

### Member

+ **extra_length : float**  
    The length that can be added to the beginning and the end of the aid line to be shown over the aid line area in the
    `AidLineControllerBase`.
+ **width: float**  
    The (stroke)width of the aid lines.
+ **color : libavg.avg.Color**  
    The color of the aid lines.
+ **circle_radius : float**  
    The radius of the the aid line if it should be a circle.
+ **show_label : bool**  
    Should a label be shown the value of an axis somewhere on the aid line?
    
## IntersectionConfiguration

A class that can save all necessary attributes for the representations of intersection between a aid line and a data 
object.

### Member

+ **show_intersections : bool**  
    Should the intersection be displayed on the chart?
+ **show_label : bool**  
    Should a label with a value for the intersection be displayed.
+ **radius : float**  
    The radius of the intersection circles.
+ **filled : bool**  
    Should the circle for the intersection be filled?
+ **color : libavg.avg.Color**  
    The color for the intersection circle.
+ **stroke_width : float**  
    The width of the circle border.
+ **label_content : str**  
    The content that the label of the intersection should display. This should have the same name as an axis to use this
    axis. Its also possible to use the string `ObjName` to show the name of the object the intersection is with.
+ **marking_text_config : TextMarkingConfiguration**  
    The configuration for the text of the label at the intersections.

## SelectionLineConfiguration

A class that can save all necessary attributes for the representations of selection lines.

### Member

+ **extra_length : float**  
    The length that can be added to the beginning and the end of the selection line to be shown over the aid line area 
    in the `AidLineControllerBase`.
+ **width : float**  
    The (stroke)width of the selection line.
+ **color : libavg.avg.Color**  
    The color of the selection line.
    
## TextLabelConfiguration

A class that can save all necessary attributes for all label texts that can be used with a chart.

### Member

+ **color : libavg.avg.Color**  
    The color of the text.
+ **font_size : float**  
    The size of the font for the text.
+ **offset_to_other_element : float**  
    The offset between the text created with this configuration and the element this text is assigned to.

## TextMarkingConfiguration
Base: `charts.configurations.TextLabelConfiguration`

A class that can save all necessary attribute for all marking texts that can be used with a chart.

## ChartConfiguration

A class that can save all necessary attributes for an chart.

### Member

+ **show_label : bool**  
    Should the label of this chart be shown?
+ **label_pos: LabelPosition**  
    The position the abel should be placed.
+ **padding_left : float**  
    Readonly. The left padding of this chart. This value should be positive.
+ **padding_top : float**  
    Readonly. The top padding of this chart. This value should be positive.
+ **padding_bottom : float**  
    Readonly. The bottom padding of this chart. This value should be positive.
+ **padding_right : float**  
    Readonly. The right padding of this chart. This value should be positive.
+ **label_text_config : TextLabelConfiguration**  
    The configuration for all text for labels on this axis

## ChartAxisConfiguration

A class that can save all necessary attribute for an axis.

### Member

+ **bottom_offset : float**  
    The offset between the beginning of the axis and the first value tick.
+ **top_offset : float**  
    The offset between the end of the axis and the last value tick.
+ **axis_orientation : Orientation**  
    In which direction should this axis be placed.
+ **axis_width : float**  
    The width of the axis.
+ **data_direction : DataDirection**  
    In which direction should the data be placed on the axis. Positive means that the smallest value is at the base 
    of the axis.
+ **tick_side : TickSide**  
    On which side of the axis should the ticks be. If this is not `Center` the `marking_side` has no effect.
+ **marking_side : MarkingSide**  
    On which side of the axis the markings for the ticks should be placed. It has no effect if the `tick_side` is not 
    `Center`.
+ **marking_steps : int**  
    What is the distance between markings on the ticks. The first and last tick are always with a marking.
+ **data_steps : int**  
    The number of steps between the highest and the lowest value of this axis.
+ **show_label : bool**  
    Should the label be displayed?
+ **show_scale_unit : bool**  
    Should the scale unit be displayed? Not implemented yet.
+ **label_pos : LabelPosition**  
    Where should the label be positioned. Top in the vertical axis alignment is on the right side.
+ **axis_color : libavg.avg.Color**  
    The color for the axis.
+ **tick_overhang : float**  
    The extra width of the ticks on both sites of the axis.
+ **label_text_config : TextLabelConfiguration**  
    The configuration for all text for labels on this axis
+ **marking_text_config : TextMarkingConfiguration**  
    The configuration for all text for markings on this axis.
