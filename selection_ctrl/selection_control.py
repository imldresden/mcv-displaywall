from selection_lasso import SelectionLasso
from selection_rect import SelectionRect
from selection import SelectionType


class SelectionControl(object):
    def __init__(self, elements, div, relative_div=None):
        """
        Controller class to handle selection lasso and selection rect.

        Args:
            graph (Graph): graph containing the nodes that are getting selected
            div (avg.DivNode): Node to paint the selection indicator on.
            graph_div (avg.DivNode): div node that is used to get relative position
                of selection to (to compare with graph node positions)
        """
        self.__elements = elements
        self.__div = div
        self.__relative_div = relative_div
        self.__selections = {}

    @property
    def selections(self):
        return self.__selections

    def get_nodes_in_selection(self, index):
        """
        Get the nodes that are covered by a currently active selection, indicated by index.

        Args:
            index (int): The index of a selection.

        Returns (list): A list of selected nodes.

        """

        # Check if the selection indicated by the index exists, if not return an empty list.
        if index not in self.__selections:
            return []

        # If the selection type is lasso and the length of the lass is less than 3, return an empty list.
        # If the lasso length is less than 3, it can not contain any nodes.
        if isinstance(self.__selections[index], SelectionLasso):
            if len(self.__selections[index].polygon()) < 3:
                return []

        poly = self.__selections[index].polygon(relative_div=self.__relative_div)

        # flashing when selecting is Rect
        if isinstance(self.__selections[index], SelectionRect):
            self.__selections[index].flash()

        return SelectionControl.points_in_poly(poly, self.__elements)

    # def draw(self):
    #     for selection in self.__active_selections.itervalues():
    #         selection.draw()

    def update(self, pos=None, size=None):
        for selection in self.__selections.itervalues():
            selection.update(pos, size)

    def get_selection_index_for_device(self, device_id):
        if "d_" + str(device_id) in self.__selections:
            return "d_" + str(device_id)
        return None

    def get_selection_index_for_touch(self, event_contact_id):
        if "t_" + str(event_contact_id) in self.__selections:
            return "t_" + str(event_contact_id)
        return None

    def create_selection(self, selection_type, event=None, device_id=None):
        """
        Add a selection type to the controller.

        :param selection_type: Type of the selection.
        :type selection_type: SelectionType
        :param event: Initial touch event, used to track subsequent touches for lasso selection.
        :type event: CursorEvent
        :param device_id: The id of the device.
        :type device_id: int
        :return: The newly created selection.
        :rtype: Selection
        """

        if event is not None:
            index = "t_" + str(event.contact.id)
        else:
            index = "d_" + str(device_id)

        if index not in self.__selections:
            if selection_type == SelectionType.RECT_SELECTION:
                self.__selections[index] = SelectionRect(self.__div)
            elif selection_type == SelectionType.LASSO_SELECTION:
                self.__selections[index] = SelectionLasso(self.__div, event)

        return self.__selections[index]

    def remove_selection(self, index):
        if index in self.__selections:
            self.__selections.pop(index)

    def remove_all_selections(self):
        for i in self.__selections.keys()[:]:
            self.__selections.pop(i).clear()

    @staticmethod
    def contains(point, poly):
        """
        Standard point in polygon implementation. Used to determine if a selection contains a given point.
        Args:
            point (Node): Point (x,y) to be checked.
            poly (list): List of points that define a polygon. Must contain at least three points.

        Returns:
            bool: True if the polygon contains the point, False if it does not.
        """
        pos = point.pos_x, point.pos_y

        length = len(poly)
        in_poly = False

        j = length - 1
        for i in range(length):
            if ((poly[i][1] > pos[1]) != (poly[j][1] > pos[1])) and \
                    (pos[0] < (poly[j][0] - poly[i][0]) * (pos[1] - poly[i][1]) / (poly[j][1] - poly[i][1]) + poly[i][0]):
                in_poly = not in_poly
            j = i
        return in_poly

    @staticmethod
    def points_in_poly(polygon, points):
        """
        Wrapper around contains() that filters a list of points and returns only those in the given polygon.

        Args:
            polygon (list): List of points that define a polygon. Must contain at least three points.
            points (list): List of points to be checked.

        Returns:
            list: A list of points that are contained within the given polygon.
        """
        return filter(lambda p: SelectionControl.contains(p, polygon), points)
