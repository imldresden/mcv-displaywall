class GridElement(object):
    """
    A element in a grid.
    """
    def __init__(self, id, left, top, right, bottom):
        """
        :param left: The left cell this elements is laying in.
        :type left: int
        :param top: The top cell this elements is laying in.
        :type top: int
        :param right: The right cell this elements is laying in.
        :type right: int
        :param bottom: The bottom cell this elements is laying in.
        :type bottom: int
        """
        self._id = id

        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom

    @property
    def id(self):
        """
        :rtype: int
        """
        return self._id

    @property
    def cell_width(self):
        """
        :rtype: int
        """
        return self.right - self.left + 1

    @property
    def cell_height(self):
        """
        :rtype: int
        """
        return self.bottom - self.top + 1

    def __repr__(self):
        return "GridElement {} ({},{},{},{})".format(self._id, self.left, self.top, self.right, self.bottom)

    def is_cell_in(self, cell):
        """
        Checks if a given cell lies inside in this grid element.

        :param cell: The cell to check for.
        :type cell: tuple[int, int]
        :return: Is the given cell in this element?
        :rtype: bool
        """
        return self.left <= cell[0] <= self.right and self.top <= cell[1] <= self.bottom
