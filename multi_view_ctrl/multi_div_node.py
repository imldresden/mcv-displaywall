from libavg import avg
from libavg.avg import MouseEvent, CursorEvent
from libavg.avg import Color
from libavg.avg import DivNode, Node
from multi_view_ctrl.configurations.grid_element_div_configuration import GridElementDivConfigurations
from multi_view_ctrl.grid_element import GridElement
from multi_view_ctrl.grid_element_div import GridElementDiv
from multi_view_ctrl.utils.default_values import MultiDivNodeDefaults


class MultiDivNode(avg.DivNode):
    def __init__(self, grid_size, grid_elements, background_color=MultiDivNodeDefaults.BACKGROUND_COLOR, grid_element_div_configs=None,
                 parent=None, **kwargs):
        """
        :param grid_size: The size of the grid. First value the cell number in x direction, the second value the cell
                          number in y direction.
        :type grid_size: tuple[int, int]
        :param grid_elements: All possible elements in this grid. Its only necessary to give elements that overlap multiple
                                 cells. All other free cell will be automatically generated.
        :type grid_elements: list[GridElement]
        :param background_color: The color of the background of this div.
        :type background_color: Color
        :param grid_element_div_configs: A dict of grid element div configs for given grid element divs (by id).
        :type grid_element_div_configs: Dict[str, ]
        :param parent: The parent of this div.
        :type parent: DivNode
        :param kwargs: All other parameters that are possible for the DivNode.
        """
        super(MultiDivNode, self).__init__(**kwargs)
        self.registerInstance(self, parent)

        self._grid_element_div_configs = grid_element_div_configs or {}
        self._grid_size = grid_size
        # dict: key -> id     value -> GridElement
        self._grid_elements = {ge.id: ge for ge in grid_elements}
        # self.__fill_missing_grid_elements()

        self._cell_size = self.size[0] / grid_size[0], self.size[1] / grid_size[1]

        avg.RectNode(
            parent=self,
            size=self.size,
            strokewidth=0,
            fillopacity=1,
            fillcolor=background_color
        )
        self._grid_div = avg.DivNode(parent=self)
        # dict: key -> grid element id     value -> GridElementDiv
        self._grid_element_divs = {}
        self.__create_grid_divs()

    @property
    def grid_size(self):
        """
        :rtype: tuple[int, int]
        """
        return self._grid_size

    @property
    def cell_size(self):
        """
        :rtype: tuple[float, float]
        """
        return self._cell_size

    @property
    def grid_elements(self):
        """
        :rtype: list[GridElement]
        """
        return self._grid_elements.values()

    @property
    def grid_element_divs(self):
        """
        :rtype: dict[int, GridElementDiv]
        """
        return self._grid_element_divs

    def __fill_missing_grid_elements(self):
        """
        Generate the missing grid elements.
        """
        free_cells = []
        # Get all remaining free cells.
        for cell in [(a, b) for a in range(self._grid_size[0]) for b in range(self._grid_size[1])]:
            free_cells.append(cell)
            for grid_element in self._grid_elements.itervalues():
                if grid_element.is_cell_in(cell=cell):
                    free_cells.remove(cell)
                    break
        # Create the missing grid elements for the free cells.
        for cell in free_cells:
            new_grid_element = GridElement(-1, cell[0], cell[1], cell[0], cell[1])
            self._grid_elements[new_grid_element.id] = new_grid_element

    def __create_grid_divs(self):
        """
        Create all divs that are used for each grid element.
        """
        for grid_element in self._grid_elements.itervalues():
            new_div = GridElementDiv(
                parent=self._grid_div,
                grid_element=grid_element,
                pos=(self._cell_size[0] * grid_element.left, self._cell_size[1] * grid_element.top),
                size=(self._cell_size[0] * grid_element.cell_width, self._cell_size[1] * grid_element.cell_height),
                grid_element_div_config=self._grid_element_div_configs[grid_element.id] if grid_element.id in self._grid_element_div_configs else GridElementDivConfigurations()

            )
            self._grid_element_divs[grid_element.id] = new_div

    def add_node_to_grid_element(self, grid_element_id, node):
        """
        Adds a node to a given grid element given through the id.

        :param grid_element_id: The id of the grid element the node should be added.
        :type grid_element_id: int
        :param node: The node to add.
        :type node: Node
        """
        if grid_element_id not in self._grid_element_divs:
            return

        node.unlink()
        self._grid_element_divs[grid_element_id].append_child_for_grid(node)

    def add_node_to_grid_element_with_cell(self, cell, node):
        """
        Adds a node to a grid element that lies in the given cell.

        :param cell: The cell the node should lie in.
        :type cell: tuple[int, int]
        :param node: The node to add.
        :type node: Node
        """
        for grid_element in self._grid_elements.itervalues():
            if grid_element.is_cell_in(cell):
                node.unlink()
                self._grid_element_divs[grid_element.id].append_child_for_grid(node)
                return

    def add_node_to_grid_element_on_pos(self, pos, node):
        """
        Adds a node to a grid element that has the given coordinates in it.

        :param pos: The position the node should be added. This pos should be the relative pos inside of this MultiDivNode.
        :type pos: tuple[float, float]
        :param node: The node to add.
        :type node: Node
        """
        for grid_element_div in self._grid_element_divs.itervalues():
            if grid_element_div.is_pos_in(pos):
                node.unlink()
                grid_element_div.append_child_for_grid(node)
                return

    def get_grid_element_from_pos(self, pos):
        """
        Searches for a grid element at the given pos.

        :param pos: The position.
        :type pos: tuple[float, float]
        :return: The found grid element. If no was found its None.
        :rtype: GridElementDiv
        """
        for grid_element_div in self._grid_element_divs.itervalues():
            if grid_element_div.is_pos_in(pos):
                return grid_element_div
        return None
