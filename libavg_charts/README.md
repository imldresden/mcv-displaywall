# Chart Implementation for libavg

This is a implementation for different kind of charts in combination with the framework [libavg]. It contains different 
classes for charts (e.g. line chart, bar chart, ...) and basic components (e.g. chart axis). It also provides a basic
data object structure to use different kind of data with the axis and charts.

[libavg]: https://www.libavg.de/site/

## Requirements

This library runs at python 2.7 and needs the following frameworks and libraries to run correctly:
  + libavg (>=1.8.2) (https://www.libavg.de/site/)
  + enum32 (>= 1.1.6)
  + enum-compact (>= 0.0.2)
  
## Classes

Description for the different classes can be found in the corresponding folders/modules of those classes.

## Usage Description

### Chart creation (TwoChartAxis)

To create a chart its only necessary to create a object of this chart. Its worth to note that the `size` of the `TwoAxisChart` 
that will be used at the construction of a chart object isn't the same size as it will cover on the screen after the 
creation. The size only refers to the axis lengths in both directions and don't calculate the markings or the labels within. 
To counter this problem its possible to set `padding` on the axis.

At the moment its necessary to redraw the whole chart to apply changed settings, like the axis config. The same goes for
the data lines in a chart. But this can be easily changed if wished.

If the default intersection and selection aid lines should be used the user has to call the methods `add_intersections_methods_to_method_holder`
and/or `add_selection_methods_to_method_holder` at the beginning of the program.

### Creation of new chart classes

If a user wishes to add a new chart to its program he should inherit from the `ChartBase` class. It provide necessary
method structures for the aid lines controller that can be used on it. The methods `add_aid_line_controller` needs to be
overwritten in the new chart.

If the user wants to create a chart with only two axis (y left and x bottom) he can also use the `TwoAxisChart` as a base
class.

If the new class should work with intersections and/or selections on the aid line its necessary to add proper methods to
the helper. For the intersection a method for the wished aid lines types should be added to the `IntersectionMethodHolder`.
If a selection is wished its also necessary to add methods to the `SelectionMethodHolder`.

### Aid line usage

At default the charts don't have an aid line controller after the creation. If a user wishes to add a specific controller
it's only necessary to call the `aid_aid_line_controller` method. If some properties of the controller should be changed
it's possible to call the `set_aid_line_controller_attributes` and to call special events on the controller the method
`invoke_aid_line_controller_event` is callable.

### Creation of data

It's possible to read a given data set from a .csv file. It should have a header and be separated by comma (`,`). If a 
special data type for some columns should be used its possible to add a special .setting file in the same folder as the
.csv file. To understand the structure of this file look at the example files in `/examples/data/..`. 

To read a .csv file the method `get_data_from_csv_file` can be used. It will return two objects. The first is the 
dictionary of possible keys in the file and their different values it can have. The second object is a list with all 
objects. Each object is hereby a dict with their properties as keys and the values an value.

#### Conversion in DataDescription

`generate_data_descriptions_from_key_and_data` needs to be changed.

It's also possible to convert a given set of `MultivariateDataObjects` in a `DataDescription`. To generate objects in this
way the method `generate_data_description_from_data_object` is usable.


#### Conversion in MultivariateDataObject

To convert the second object of the `get_data_from_csv_file` methods it's possible to use the `generate_data_object_from_key_and_data`.

