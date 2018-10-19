# Communication Guide (Protocol)

This file describes the values which will be used to allow the communication between the server and any given website
that is called through this server. Most of the communication will be handled through the `DataWebSocketHandler`.

## `DataWebSocketHandler` Requests

The `DataWebSocketHandler` prepares a bidirectional connection between the server and the websites to send data between 
these two. In the following section the possible request from either side will be listed. Also the form of the data will
be described as well.

### Data body form

The body of each request looks like this:
```python
request = {
    "requestType": "",
    "data": {
        # ...
    }
}
```
The "data" key can be filled with any data needed or requested.

### Request types

There exists the following types for requests:

| key               | description                                                                                                                         |
|-------------------|-------------------------------------------------------------------------------------------------------------------------------------|
| IdRequest         | Requests the id of the used web socket. This is need to identify each connection and following each device used.                    |
| ViewRequest       | Requests a given view. This requests uses the cursor linked to the device/connection.                                               |
| ViewUpdateRequest | Requests an update for a given view. This is used if the device and the wall should be linked.                                      |
| ViewSend          | Sends a view. A new view should be send to the parent application. This can show the new view at the position of the linked cursor. |
| ViewUpdateSend    | Sends an update for an view. This is used of the device and the wall should be linked.                                              |
|                   |                                                                                                                                     |

### Request data (device -> server)

The following structure for the "data" in a request from the **device** to the **server** is used:

| messageType       | data                                                                 |
|-------------------|----------------------------------------------------------------------|
| IdRequest         | -                                                                    |
| ViewRequest       |                                                                      |
| ViewUpdateRequest |                                                                      |
| ViewSend          |                                                                      |
| ViewUpdateSend    |                                                                      |
|                   |                                                                      |

### Request data (server -> device)

The following structure for the "data" in a request from the **server** to the **device** is used:

| messageType       | data type        | data                                                                 |
|-------------------|------------------|----------------------------------------------------------------------|
| IdRequest         | int              | - **id**: The id linked to the the device that started this request. |
| ViewRequest       | viewData         | - **viewData**: The specific data for this view.                     |
|                   | str              | - **viewType**: The type this view represents.                       |
|                   | list[int, int]   | - **size**: The size of the view on the wall.                        |
|                   | str              | - **label**: The label of the view.                                  |
|                   | list[DataObject] | - **data**: All data elements that are shown in the view.            |
| ViewUpdateRequest |                  |                                                                      |
| ViewSend          |                  |                                                                      |
| ViewUpdateSend    |                  |                                                                      |
|                   |                  |                                                                      |

## Other data body

Here the other information and their structure are shown.
First the different kinds of `viewData`:

| `viewData` types | data type | data                                        |
|------------------|-----------|---------------------------------------------|
| for charts       | Axis      | - **xAxis**: The axis that lies horizontal. |
|                  | Axis      | - **yAxis**: The axis that lies vertical.   |
| for maps         |           |                                             |
|                  |           |                                             |
| for graphs       |           |                                             |
|                  |           |                                             |

Second all other information bodies:


| type      | data type        | body                                                                    |
|-----------|------------------|-------------------------------------------------------------------------|
| Axis      | str              | - **type**: The type of the values on this axis.                        |
|           | list[DataObject] | - **dataElements**: All values that this axis shows.                    |
|           | str              | - **label**: The label of the axis.                                     |
|           | str              | - **keyName**: The name of the data this axis represents.               |
|           | str              | - **unit**: The unit for the data on this axis.                         |
| Databject | list[Attribute]  | - **attributes**: All attributes and there value for this data object.  |
|           | str              | - **color**: The color of this data object.                             |
|           | obj              | - **id**: The id for this data object.                                  |
|           | int              | - **levelOfDetail**: The level of detail this object shows on the wall. |
|           | str              | - **selectionState**: The state of selection for this data object.      |
| Attribute | str              | - **dataName**: The name for this attribute.                            |
|           | str              | - **dataType**: The type of this attribute.                             |
|           | list[obj]        | - **values** (list): The values this attribute containts.               |