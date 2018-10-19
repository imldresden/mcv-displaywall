from enum import Enum


class Orientation(Enum):
    """
    In which direction should the axis be facing.
    """
    Horizontal = 0
    Vertical = 1


class DataDirection(Enum):
    """
    In which direction should the data be positioned.
    """
    Positive = 0
    Negative = 1


class MarkingSide(Enum):
    """
    On which side of an axis should be the markings placed.
    """
    Left = 0
    Right = 1


class TickSide(Enum):
    """
    On which side of an axis should the ticks be placed.
    """
    Left = 0
    Center = 1
    Right = 2


class GridLines(Enum):
    """
    Should a fine grid be shown at the axis specific positions? This needs to be handled from the charts.
    """
    Nothing = 0
    Markings = 1
    Ticks = 2
