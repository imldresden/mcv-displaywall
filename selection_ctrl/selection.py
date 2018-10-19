from abc import ABCMeta, abstractmethod
from enum import Enum


class SelectionType(Enum):
    LASSO_SELECTION = 0
    RECT_SELECTION = 1


class SelectionStatus(Enum):
    inactive = 0
    active = 1
    trigger_select = 2


class Selection(object):
    """
    Abstract base class for all selection classes.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def polygon(self):
        raise NotImplementedError('Derived classes must implement the "polygon" method.')

    @abstractmethod
    def update(self, pos=None, size=None):
        raise NotImplementedError('Derived classes must implement the "update" method.')

    @abstractmethod
    def clear(self):
        raise NotImplementedError('Derived classes must implement the "clear" method.')
