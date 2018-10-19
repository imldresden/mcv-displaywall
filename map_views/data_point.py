from data_models.data_enums import DataSelectionState


class DataPoint(object):
    """
         base class for visual elements (e.g. in graph and map) that can be manipulated by lens
         contains some information from DataObject (such as data_object_id to link back) but not
         necessarily the complete dataobject (as defined in data.data_object)
    """

    def __init__(self, data_object_id=-1, pos_x=0, pos_y=0, width=20, height=20, attribute_dict=None, level_of_detail=0):
        self.__data_object_id = data_object_id
        self.__pos_x = pos_x
        self.__pos_y = pos_y
        self.__width = width
        self.__height = height
        self.__level_of_detail = level_of_detail
        self.__element_state = DataSelectionState.Nothing
        self.__visible = True
        self.__opacity_val = 1.0

        if attribute_dict is None:
            self.__attribute_dict = {}
        else:
            self.__attribute_dict = attribute_dict

        self.__current_highlight_color = None

        self.__callbacks_pos_changed = []
        self.__callbacks_size_changed = []
        self.__callbacks_visible_changed = []
        self.__callbacks_opacity_changed = []
        self.__callbacks_element_state_changed = []
        self.__callbacks_level_of_detail_changed = []

    # region Properties

    @property
    def data_object_id(self):
        return self.__data_object_id

    @property
    def attribute_dict(self):
        """
            contains all attributes of the data object as key, value pairs
        :rtype: dict
        """
        return self.__attribute_dict

    @attribute_dict.setter
    def attribute_dict(self, attribute_dict):
        """
            this appends all data values and does not replace the current list
        """
        self.__attribute_dict.update(attribute_dict)

    def get_attribute(self, attribute):
        return self.__attribute_dict.get(attribute)

    def set_attribute(self, attribute, value):
        self.__attribute_dict[attribute] = value

    @property
    def pos_x(self):
        """
            :rtype: int
        """
        return self.__pos_x

    @pos_x.setter
    def pos_x(self, pos_x):
        self.__pos_x = pos_x
        for callback in self.__callbacks_pos_changed:
            callback(sender=self, pos_x=pos_x, pos_y=self.__pos_y)

    @property
    def pos_y(self):
        """
            :rtype: int
        """
        return self.__pos_y

    @pos_y.setter
    def pos_y(self, pos_y):
        self.__pos_y = pos_y
        for callback in self.__callbacks_pos_changed:
            callback(sender=self, pos_x=self.__pos_x, pos_y=pos_y)

    def set_pos(self, pos_x, pos_y):
        self.pos_x = pos_x
        self.pos_y = pos_y
        for callback in self.__callbacks_pos_changed:
            callback(sender=self, pos_x=pos_x, pos_y=pos_y)

    @property
    def width(self):
        return self.__width

    @width.setter
    def width(self, width):
        self.__width = width
        for callback in self.__callbacks_size_changed:
            callback(sender=self, width=width, height=self.__height)

    @property
    def height(self):
        return self.__height

    @height.setter
    def height(self, height):
        self.__height = height
        for callback in self.__callbacks_size_changed:
            callback(sender=self, width=self.__width, height=height)

    @property
    def visible(self):
        return self.__visible

    @visible.setter
    def visible(self, visible):
        self.__visible = visible
        for callback in self.__callbacks_visible_changed:
            callback(sender=self, visible=self.__visible)

    @property
    def opacity_val(self):
        return self.__opacity_val

    @opacity_val.setter
    def opacity_val(self, opacity_val):
        self.__opacity_val = opacity_val
        for callback in self.__callbacks_opacity_changed:
            callback(sender=self, opacity_val=self.__opacity_val)

    @property
    def level_of_detail(self):
        """
            :rtype: int
        """
        return self.__level_of_detail

    @level_of_detail.setter
    def level_of_detail(self, level_of_detail):
        if level_of_detail == self.__level_of_detail:
            return

        self.__level_of_detail = level_of_detail
        for callback in self.__callbacks_level_of_detail_changed:
            callback(sender=self, level_of_detail=self.__level_of_detail)

    @property
    def element_state(self):
        """
        :rtype: ElementState
        """
        return self.__element_state

    @element_state.setter
    def element_state(self, element_state):
        if self.__element_state is element_state:
            return

        self.set_element_state(sender=self, element_state=element_state, highlight_color=None)

    def set_element_state(self, element_state, sender=None, highlight_color=None):
        """
        use this function and include sender if selection does not originate from Node/NodeView (tap),
        so that multiple node selection (e.g., sender=lasso) are propagated not by individual nodes but as one
        :param element_state:
        :param sender:
        :param highlight_color: the color with which to highlight the selection
        :return:
        """
        # removed: divico control sends state change anew with other highlight color
        # if self.__element_state is element_state:
        #     return

        self.__element_state = element_state
        self.__current_highlight_color = highlight_color
        for callback in self.__callbacks_element_state_changed:
            callback(sender=sender, element_state=self.__element_state, highlight_color=highlight_color)

    @property
    def current_highlight_color(self):
        return self.__current_highlight_color

    def start_listening(self, pos_changed=None, size_changed=None, visible_changed=None, opacity_val_changed=None,
                        element_state_changed=None, level_of_detail_changed=None):
        """
            Registers a callback to listen to changes to this node. Listeners can register to any number of the provided
            events. For the required structure of the callbacks see below.

            Args:
                pos_changed (function(sender:node, pos_x:float, pos_y:float): called whenever the position of this node
                    changes
                size_changed:
                element_state_changed:
                level_of_detail_changed:
        """
        events = [
            (pos_changed, self.__callbacks_pos_changed),
            (size_changed, self.__callbacks_size_changed),
            (visible_changed, self.__callbacks_visible_changed),
            (opacity_val_changed, self.__callbacks_opacity_changed),
            (element_state_changed, self.__callbacks_element_state_changed),
            (level_of_detail_changed, self.__callbacks_level_of_detail_changed)
        ]

        for callback, call_list in events:
            if callback is not None and callback not in call_list:
                call_list.append(callback)

    def stop_listening(self, pos_changed=None, size_changed=None, visible_changed=None, opacity_val_changed=None,
                       element_state_changed=None, level_of_detail_changed=None):
        """
            Stops listening to an event the listener has registered to previously. The provided callback needs to be the
            same that was used to listen to the event in the fist place.

            Args:
                pos_changed (function(sender:node, pos_x:float, pos_y:float): called whenever the position of this node
                    changes
                element_state_changed:
                level_of_detail_changed:
        """
        events = [
            (pos_changed, self.__callbacks_pos_changed),
            (size_changed, self.__callbacks_size_changed),
            (visible_changed, self.__callbacks_visible_changed),
            (opacity_val_changed, self.__callbacks_opacity_changed),
            (element_state_changed, self.__callbacks_element_state_changed),
            (level_of_detail_changed, self.__callbacks_level_of_detail_changed)
        ]

        for callback, call_list in events:
            if callback is not None:
                call_list.remove(callback)
