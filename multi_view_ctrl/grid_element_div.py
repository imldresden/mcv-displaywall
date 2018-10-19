from libavg import avg
from events.event_dispatcher import EventDispatcher
from multi_view_ctrl.grid_element import GridElement
from multi_view_ctrl.configurations.grid_element_div_configuration import GridElementDivConfigurations


class GridElementDiv(avg.DivNode, EventDispatcher):
    def __init__(self, grid_element, grid_element_div_config=None, parent=None, **kwargs):
        """
        :param grid_element: The grid element that is the base for this div.
        :type grid_element: GridElement
        :param grid_element_div_config: The configuration that is used to create this grid element div.
        :type grid_element_div_config: GridElementDivConfigurations
        :param parent: The parent of this div.
        :type parent: DivNode
        :param kwargs: All other parameters that are possible for the DivNode.
        """
        super(GridElementDiv, self).__init__(**kwargs)
        self.registerInstance(self, parent)
        EventDispatcher.__init__(self)

        self._grid_element = grid_element
        self._grid_element_div_config = grid_element_div_config if grid_element_div_config else GridElementDivConfigurations()

        avg.RectNode(
            parent=self,
            pos=(self._grid_element_div_config.margin,self._grid_element_div_config. margin),
            size=(self.size[0] - 2 * self._grid_element_div_config.margin,
                  self.size[1] - 2 * self._grid_element_div_config.margin),
            strokewidth=self._grid_element_div_config.border_width,
            color=self._grid_element_div_config.border_color,
            fillcolor=self._grid_element_div_config.background_color,
            fillopacity=1
        )
        self._internal_div = avg.DivNode(
            parent=self,
            pos=(self._grid_element_div_config.margin, self._grid_element_div_config.margin),
            size=(self.size[0] - 2 * self._grid_element_div_config.margin,
                  self.size[1] - 2 * self._grid_element_div_config.margin),
            crop=True
        )
        self._child_nodes = []

    @property
    def grid_id(self):
        """
        :rtype: int
        """
        return self._grid_element.id

    @property
    def child_nodes(self):
        """
        :rtype: list[Node]
        """
        return self._child_nodes

    def get_rel_pos(self, pos):
        """
        Calculates a relative pos to this grid element div.

        :param pos: The source pos.
        :type pos: tuple[float, float]
        :return: The relative pos.
        :rtype: tuple[float, float]
        """
        return pos[0] - self.pos[0] - self._grid_element_div_config.margin, pos[1] - self.pos[1] - self._grid_element_div_config.margin

    def is_pos_in(self, pos):
        """
        Checks if a given pos lies inside in this grid element div.

        :param pos: The pos to check for.
        :type pos: tuple[float, float]
        :return: Is the given pos in this element?
        :rtype: bool
        """
        return self.pos[0] <= pos[0] <= self.pos[0] + self.size[0] and self.pos[1] <= pos[1] <= self.pos[1] + self.size[1]

    def append_child_for_grid(self, node):
        """
        Appends the given node. It also sets the size of the node to the size of this grid element div.

        :param node: The node to add to this grid element.
        :type node: Node
        """
        node.size = self._internal_div.size
        node.view_id = self.grid_id
        self._internal_div.appendChild(node)
        self._child_nodes.append(node)

    def start_listening(self):
        """
        Registers a callback to listen to changes to this grid elemen div. Listeners can register to any number of the provided
        events. For the required structure of the callbacks see below.
        """
        pass

    def stop_listening(self):
        """
        Stops listening to an event the listener has registered to previously. The provided callback needs to be the
        same that was used to listen to the event in the fist place.
        """
        pass
