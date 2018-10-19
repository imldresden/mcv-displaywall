## GridElement

A element in a grid.

### Member

+ **GridElement(left : int, top : int, right : int, bottom : int)**


+ **left : int**  
    The left cell this elements is laying in.
+ **top : int**  
    The top cell this elements is laying in.
+ **right : int**  
    The right cell this elements is laying in.
+ **bottom : int**  
    The bottom cell this elements is laying in.
+ **id : int**  
    The id of this grid element.
+ **cell_width : int**  
    The width in cells of this element.
+ **cell_height : int**  
    The height in cells of this element.
    

+ **is_cell_in(cell)**  
    Checks if a given cell is inside in this grid element.
+ **get_current_max_id()**  
    _Static._ Gets the current max id that is used through the GridElements.
    
## GridElementDiv
Base: [libavg.avg.DivNode]

The div node that represents a grid element that lies on cells in a whole grid.

### Member

+ **GridElementDiv(grid_element : GridElement, [parent : DivNode], \*\*kwargs)**


+ **is_pos_in(pos)**  
    Checks if a given pos lies inside in this div node.
+ **appendChild(\*args, \*\*kwargs)**      
    Appends the given node (in \*args). It also sets the size of the node to the size of this grid element div.

## MultiDivNode
Base: [libavg.avg.DivNode]

A div node that allows the splitting of its area in a given grid. Each cell in this grid gets the same size. Grid
elements can be placed on this grid as the user wishes. The grid elements should not overlap each other. It's only
possible to add grid elements whose shape in some sorts a rectangle.

### Member

+ **MultiDivNode(grid_size : tuple[int, int], grid_elements : list[GridElement], [parent : DivNode], \*\*kwargs)**


+ **grid_size : tuple[int, int]**  
    The number of cells in each direction in this div.
+ **cell_size : tuple[float, float]**  
    The size in pixel of each single cell.
+ **grid_elements : list[GridElement]**  
    All grid elements that are placed in this grid.
+ **grid_element_divs : dict[int, GridElement]**  
    All divs that are placed in this div through the grid elements. The key is the id of the grid element corresponding
    to the div.


+ **add_node_to_grid_element(grid_element_id, node)**  
    Adds a node to a given grid element given through the id.
+ **add_node_to_grid_element_with_cell(cell, node)**  
    Adds a node to a grid element that lies in the given cell.
+ **add_node_to_grid_element_on_pos(pos, node)**  
    Adds a node to a grid element that has the given coordinates in it.
    

[libavg.avg.DivNode]: https://www.libavg.de/reference/svn/areanodes.html?highlight=divnode#libavg.avg.DivNode
