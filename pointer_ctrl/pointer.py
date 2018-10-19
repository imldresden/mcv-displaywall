from libavg import avg
from libavg.avg import Color, DivNode


class Pointer(avg.DivNode):
    def __init__(self, device, parent=None, **kwargs):
        """
        :param device: The device this pointer should be coupled with.
        :type device: Device
        :type parent: DivNode
        :param kwargs:
        """
        super(Pointer, self).__init__(**kwargs)
        self.registerInstance(self, parent)
        self.sensitive = False

        self._device = device
