from multi_view_ctrl.configurations.grid_element_div_configuration import GridElementDivConfigurations
from multi_view_ctrl.multi_div_node import MultiDivNode
from multi_view_ctrl.grid_element import GridElement


class ExampleMultiDivNode1(MultiDivNode):
    def __init__(self, **kwargs):
        super(ExampleMultiDivNode1, self).__init__(
            grid_size=(24, 12),
            grid_elements=[GridElement(0, 2, 0, 3, 0),
                           GridElement(1, 4, 0, 5, 0),
                           GridElement(2, 2, 2, 3, 2),
                           GridElement(3, 4, 2, 5, 2),
                           GridElement(4, 0, 4, 0, 5),
                           GridElement(5, 1, 4, 1, 5),
                           GridElement(6, 2, 4, 2, 5),
                           GridElement(7, 3, 4, 3, 5),
                           GridElement(8, 4, 4, 4, 5),
                           GridElement(9, 5, 4, 5, 5),
                           GridElement(10, 0, 6, 0, 7),
                           GridElement(11, 1, 6, 3, 7),
                           GridElement(12, 18, 4, 21, 7),
                           GridElement(13, 18, 0, 23, 0),
                           GridElement(14, 6, 0, 13, 3),
                           GridElement(15, 6, 4, 11, 11),
                           GridElement(16, 16, 4, 17, 9),
                           GridElement(17, 20, 2, 21, 2),
                           GridElement(21, 12, 4, 15, 7),
                           GridElement(22, 12, 10, 23, 11),
                           GridElement(23, 16, 2, 17, 2),
                           GridElement(24, 16, 0, 17, 0),
                           GridElement(25, 22, 2, 23, 7),
                           GridElement(26, 14, 0, 15, 0),
                           GridElement(27, 14, 2, 15, 2),
                           GridElement(32, 0, 8, 5, 9),
                           GridElement(33, 0, 0, 1, 3),
                           GridElement(34, 21, 8, 23, 8),
                           GridElement(35, 19, 8, 20, 8),
                           GridElement(36, 18, 8, 18, 8),
                           GridElement(37, 4, 6, 5, 7),
                           GridElement(38, 14, 8, 14, 8),
                           GridElement(39, 15, 8, 15, 8),
                           GridElement(40, 18, 2, 19, 2),
                           GridElement(41, 12, 8, 13, 8),
                           ],
            **kwargs
        )


class ExampleMultiDivNode2(MultiDivNode):
    def __init__(self, **kwargs):
        super(ExampleMultiDivNode2, self).__init__(
            grid_size=(24, 12),
            grid_elements=[
                GridElement(25, 0, 0, 1, 11),
                GridElement(32, 2, 8, 3, 11),
                GridElement(41, 4, 8, 5, 9),
                GridElement(11, 4, 10, 5, 11),
                GridElement(33, 2, 0, 3, 2),
                GridElement(0, 4, 0, 4, 2),
                GridElement(1, 5, 0, 5, 2),
                GridElement(2, 6, 0, 6, 2),
                GridElement(3, 7, 0, 7, 2),
                GridElement(21, 2, 4, 5, 7),
                GridElement(16, 6, 4, 7, 11),
                GridElement(16, 6, 4, 7, 11),
                GridElement(15, 12, 0, 17, 7),
                GridElement(22, 8, 10, 23, 11),
                GridElement(14, 20, 0, 23, 5),
                GridElement(12, 8, 0, 10, 2),
                GridElement(37, 8, 3, 10, 4),
                GridElement(4, 11, 0, 11, 0),
                GridElement(5, 11, 1, 11, 1),
                GridElement(6, 11, 2, 11, 2),
                GridElement(7, 11, 3, 11, 3),
                GridElement(8, 11, 4, 11, 4),
                GridElement(9, 11, 5, 11, 5),
                GridElement(10, 11, 6, 11, 6),
                GridElement(24, 4, 3, 5, 3),
                GridElement(23, 2, 3, 3, 3),
                GridElement(13, 18, 4, 19, 4),
                GridElement(17, 18, 5, 19, 5),
                GridElement(26, 18, 6, 19, 6),
                GridElement(27, 18, 7, 19, 7),
                GridElement(36, 20, 8, 21, 9),
                GridElement(35, 18, 8, 19, 8),
                GridElement(34, 18, 9, 19, 9),
                GridElement(38, 20, 6, 21, 7),
                GridElement(40, 6, 3, 7, 3),
                GridElement(39, 22, 6, 23, 7),
            ],
            **kwargs
        )


class ExampleMultiDivNode3(MultiDivNode):
    def __init__(self, **kwargs):
        super(ExampleMultiDivNode3, self).__init__(
            grid_size=(24, 12),
            grid_elements=[
                GridElement(25, 0, 1, 1, 10),
                GridElement(32, 2, 8, 3, 10),
                GridElement(41, 4, 8, 5, 10),
                GridElement(11, 6, 8, 7, 10),
                GridElement(33, 2, 1, 3, 2),
                GridElement(0, 4, 1, 4, 2),
                GridElement(1, 5, 1, 5, 2),
                GridElement(2, 6, 1, 6, 2),
                GridElement(3, 7, 1, 7, 2),
                GridElement(21, 2, 4, 5, 7),
                GridElement(16, 21, 6, 23, 8),
                GridElement(15, 12, 1, 17, 7),
                GridElement(22, 8, 9, 23, 10),
                GridElement(12, 8, 1, 10, 2),
                GridElement(37, 8, 3, 10, 5),
                GridElement(5, 11, 1, 11, 1),
                GridElement(6, 11, 2, 11, 2),
                GridElement(7, 11, 3, 11, 3),
                GridElement(8, 11, 4, 11, 4),
                GridElement(9, 11, 5, 11, 5),
                GridElement(10, 11, 6, 11, 6),
                GridElement(4, 11, 7, 11, 7),
                GridElement(24, 4, 3, 5, 3),
                GridElement(23, 2, 3, 3, 3),
                GridElement(13, 6, 4, 7, 4),
                GridElement(17, 6, 5, 7, 5),
                GridElement(26, 6, 6, 7, 6),
                GridElement(27, 6, 7, 7, 7),
                GridElement(36, 22, 1, 23, 1),
                GridElement(38, 22, 2, 23, 2),
                GridElement(39, 22, 3, 23, 3),
                GridElement(35, 22, 4, 23, 4),
                GridElement(34, 22, 5, 23, 5),
                GridElement(40, 6, 3, 7, 3),
                GridElement(42, 8, 8, 17, 8),
                GridElement(43, 8, 6, 10, 7),
                GridElement(44, 18, 1, 19, 1),
                GridElement(45, 18, 2, 19, 2),
                GridElement(46, 18, 3, 19, 3),
                GridElement(47, 18, 4, 19, 4),
                GridElement(48, 18, 5, 19, 5),
                GridElement(49, 20, 1, 21, 1),
                GridElement(50, 20, 2, 21, 2),
                GridElement(51, 20, 3, 21, 3),
                GridElement(52, 20, 4, 21, 4),
                GridElement(53, 20, 5, 21, 5),
                GridElement(54, 18, 6, 20, 8),
            ],
            grid_element_div_configs={
                15: GridElementDivConfigurations(background_color="ddd")
            },
            **kwargs
        )


class AllAloneMultiDivNode(MultiDivNode):
    """
    0/0:  0    1/0:  3    2/0:  6    3/0:  9
    0/1:  1    1/1:  4    2/1:  7    3/1:  10
    0/2:  2    1/2:  5    2/2:  8    3/2:  11
    """
    def __init__(self, **kwargs):
        super(AllAloneMultiDivNode, self).__init__(
            grid_size=(4, 3),
            grid_elements=[
                           GridElement(0, 0, 0, 0, 0),
                           GridElement(1, 0, 1, 0, 1),
                           GridElement(2, 0, 2, 0, 2),
                           GridElement(3, 1, 0, 1, 0),
                           GridElement(4, 1, 1, 1, 1),
                           GridElement(5, 1, 2, 1, 2),
                           GridElement(6, 2, 0, 2, 0),
                           GridElement(7, 2, 1, 2, 1),
                           GridElement(8, 2, 2, 2, 2),
                           GridElement(9, 3, 0, 3, 0),
                           GridElement(10, 3, 1, 3, 1),
                           GridElement(11, 3, 2, 3, 2),
                           ],
            **kwargs
        )
