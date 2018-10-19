from libavg import avg
from libavg.avg import DivNode
from pointer_ctrl.configurations.device_pointer_configurations import DevicePointerConfigurations
from pointer_ctrl.pointer import Pointer


class PointerControl(avg.DivNode):
    def __init__(self, parent=None, **kwargs):
        """
        :param parent: The parent that the pointer controller uses to show the pointer.
        :type parent: DivNode
        """
        super(PointerControl, self).__init__(**kwargs)
        self.registerInstance(self, parent)

        self._pointer_div = avg.DivNode(parent=self)

        # dict: key -> device id     values -> pointer
        self._pointer = {}

    @property
    def pointers(self):
        """
        :rtype: dict[int, Pointer]
        """
        return self._pointer

    def add_new_pointer(self, device, pointer_mode):
        """
        Adds a new pointer for the given device to this control.

        :param device: The device the new pointer is associated with.
        :type device: id
        :param pointer_mode: The id of the mode the new pointer should be in.
        :type pointer_mode: DevicePointerConfigurations
        :param color: the specific color for this pointer.
        :type color: avg.Color
        """
        if device.id in self._pointer:
            return

        self._pointer[device.id] = pointer_mode.pointer_div_node_class(device=device, parent=self._pointer_div)

    def change_mode_of_pointer(self, device_id, device_pointer_config):
        """
        Changes the mode of a pointer for the given device id.

        :param device_id: The id of the device the pointer is linked to.
        :type device_id: int
        :param device_pointer_config: The id of the mode the new pointer should be in.
        :type device_pointer_config: DevicePointerConfigurations
        """
        # TODO: Implement this.
        pass

    def remove_pointer(self, device_id):
        """
        Removes the pointer connected to the device given through the id.

        :param device_id: The id of the device the pointer is linked to.
        :type device_id: int
        """
        if device_id not in self._pointer:
            return

        self._pointer[device_id].unlink(True)

    def move_pointer(self, device_id, pos):
        """
        Moves the pointer at a new position.

        :param device_id: The id of the device that is connected to the pointer.
        :type device_id: int
        :param pos: The new position of the pointer.
        :type pos: tuple[float, float]
        """
        if device_id not in self._pointer:
            return

        self._pointer[device_id].pos = pos
