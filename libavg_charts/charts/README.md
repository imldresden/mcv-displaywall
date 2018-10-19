## Label
Base: `Enum`

The possible positions of an label of an axis.

The values are: Top, Bottom

## LineChart
Base: `TwoAxisChart`

A line chart.

### Member

+ **LineChart([data_line_width : float], \*\*kwargs)**

## BarChartOneObject
Base: `BarChartBase`

A bar chart. This bar chart used only one `MultivariateDataObject` to be created. Bot axis are a different `DataObject`
from this.

### Member

+ **BarChartOneObject(data_objects : MultivariateDataObject, \*\*kwargs)**

## BarChartManyObjects
Base: `BarChartBase`

A bar chart. This bar chart will use many different `MulticvariateDataObjects` to be created. The x axis displays the
names of the different data objects, while the y axis shows one chosen `DataObject` that all data objects have in 
common.

### Member

+ **BarChartMandyObjects(data : list[MultivariateDataObject], \*\*kwargs)**

## ScatterPlot
Base: `TwoAxisChart`

A scatter plot.

### Member

+ **ScatterPlot([data_object_radius : float], \*\*kwargs)**

## ParallelCoordinatesPlot
Base: `ChartBase`

A parallel coordinates plot.

### Member

+ **ParallelCoordinatesPlot(axis_data : list[DataDescription], [axis_config : list[ChartAxisConfiguration], 
                            data_line_width : float], \*\*kwargs)**
