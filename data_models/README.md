## DataTypes
Base: `Enum`

An enum with all possible types for the data objects.

The values are: Integer, IntegerSum, Float, FloatSum, String, Date, Time

### Member

+ **is_number(data_type)**  
    Checks if a given data type is number type.
+ **def is_sum(data_type)**  
    Checks if a given data type is a sum number type.
    
## DataSelectedState
Base `Enum`

All possible selection states of an multivariate data object.

The values are: Nothing, Selected, Highlighted

## Attribute

Represents a single attribute.

### Member

+ **Attribute(data_name : str, data_type : DataType, values : list)**


+ **data_name : str**  
    Readonly. The name of this data object.
+ **data_type : DataTypes**  
    Readonly. The type for this data. See the enum `DataTypes`.
+ **values : list[object]**  
    Readonly. A list of different values for this kind of data object.
     
## DataObject

Represents a multivariate data object. It contains different normal data objects.

### Member

+ **DataObject(obj_id : object, data_objects : list[Attribute], [color : libavg.avg.Color])**


+ **obj_id : object**  
    The name of this specific multivariate object.
+ **data_objects list[Attribute]**  
    Readonly. All data objects that are in this multivariate data object.
+ **data_value_length : int**  
    This could be deleted
+ **color : libavg.avg.Color**
    The color for this multivariate data object.
+ **data_selection_state : DataSelectionState**  
    The selection state of this data object.    


+ **generate_data_object_from_key_and_data(separation_key, orig_data, [search_key_values=None])**  
    _Static._ It will generate from a given data set a multivariate data object. The data set will be split in different objects 
    at the `obj_name_keys`. It will only get those objects that `obj_name_keys` value is in the `search_key_values`.
+ **start_listening([selection_state_change])**      
    Registers different callbacks to listen to changes on the multivariate data object.
+ **stop_listening([selection_state_change])**      
    Removes different callbacks from listening to changes from the multivariate data object.
   
## DataDescription

It describes a specific data object with its type, a unit, a name and other attributes.

### Member

+ **DataDescription(data_type : DataType, data : list, key_name: str, [label : str, unit : str])**


+ **data_type : DataTypes**  
    Readonly. The type for this kind of data. See the enum `DataTypes`.
+ **data : list[object]**  
    Readonly. A list of all possible different data values. If the data type is a number, this list has only the 
    smallest and the highest value of this data.
+ **key_name: str**
    The key addressing the data (for attribute access).
+ **label : str**  
    The label for this kind of data. If not given is equal to key_name.
+ **unit : str**  
    The unit for this kind of data.
    
    
+ **generate_data_descriptions_from_key_and_data(data_separation_key, orig_data, [separation_key_values, keys_as_sum])**  
    _Static._ Generates from a data set from a given key with a value a number of lists from the data rest. **Needs to be changed!**
+ **generate_data_description_from_data_object(data_objects, description_name)**
    _Static._ Generates a data description from a given data object. The `description_name` is the description that will be created.
    If this parameter is `obj_name` the `obj_name`s of all data objects will be used as a new description.

## data_provider.py

File that holds methods for the loading of data from a .csv file.

### Member

+ **get_data_from_csv_file(filename, [with_settings=False]) : tuple[dict[string, list[object]], list[dict[string, object]]]**  
    Loads a .csv file and reads it. It can also use a settings file that describes the data type of the different data 
    values It will save it in a two separated lists/dicts. The first dict contains all possible data keys and a list of 
    there values. The second list contains all different data objects in dicts. Each key in this dict is a data property 
    (key is the name and the value is the value) of this object.
