from enum import Enum


class AidLineType(Enum):
    """
    All types of possible aid lines.
    """
    AxisDragX = 0
    AxisDragY = 1
    Cursor = 2
    CursorHorizontal = 3
    CursorVertical = 4
    SelectionHorizontal = 5
    SelectionVertical = 6
    Selection = 7
    CircleSelection = 8
    Lasso = 9,
    Deposit = 10,
    DepositHorizontal = 11,
    DepositVertical = 12

    @staticmethod
    def can_select(aid_line_type):
        """
        Checks if the given type is a type for selection

        :param aid_line_type: The type to check.
        :type aid_line_type: AidLineType
        :return: Can the controller of this type select?
        :rtype: bool
        """
        return aid_line_type in [AidLineType.SelectionHorizontal, AidLineType.SelectionVertical, AidLineType.Selection, AidLineType.CircleSelection, AidLineType.Lasso]


class AidLineLabelPos(Enum):
    """
    The position of the label for the aid lines. Top is at horizontal aid lines the right side, bottom the right.
    """
    Top = 0,
    Bottom = 1
