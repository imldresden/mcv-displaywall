from libavg import avg

from pointer_ctrl.pointer import Pointer


class PointerExample(Pointer):
    def __init__(self, parent=None, **kwargs):
        super(PointerExample, self).__init__(**kwargs)
        self.registerInstance(self, parent)

        avg.RectNode(
            parent=self,
            size=(80, 80),
            pos=(-40, -40),
            strokewidth=4,
            color="000000"
        )
        avg.CircleNode(
            parent=self,
            r=4,
            strokewidth=0,
            fillcolor="ff0000" if "Bumpy" in self._device.rui_proxy_name else "0000ff",
            fillopacity=1
        )
