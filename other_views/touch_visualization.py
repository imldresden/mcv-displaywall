from libavg import avg, player
from libavg.app.touchvisualization import BaseTouchVisualization


class TouchVisualization(BaseTouchVisualization):
    sources = [avg.Event.TOUCH]
    bmp = avg.Bitmap("assets/touch_visualization/TouchFeedback_Dark.png")

    def __init__(self, event, **kwargs):
        BaseTouchVisualization.__init__(self, event, **kwargs)

        if event.source in self.sources:
            self.__circle = avg.ImageNode(parent=self)
            self.__circle.setBitmap(self.bmp)
            self.__setRadius(self._radius)
            avg.LinearAnim(self.__circle, "opacity", 200, 0.7, 0.4).start()
        else:
            self.unlink(True)
            self._abort()

    def _onMotion(self, event):
        BaseTouchVisualization._onMotion(self, event)
        self.__setRadius(self._radius)

    def _onUp(self, event):

        def gone(self):
            BaseTouchVisualization._onUp(self, event)
            self.unlink(True)
            del self

        avg.Anim.fadeIn(self.__circle, 100, 1)
        avg.LinearAnim(self.__circle, "size", 100, self.__circle.size, (4, 4)).start()
        avg.LinearAnim(self.__circle, "pos", 100, self.__circle.pos, (-2, -2)).start()
        player.setTimeout(100, lambda: gone(self))

    def __setRadius(self, radius):
        self.__circle.pos = (-radius, -radius)
        self.__circle.size = (radius * 2, radius * 2)
