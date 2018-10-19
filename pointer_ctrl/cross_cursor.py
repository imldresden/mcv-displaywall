
from libavg import avg

from pointer_ctrl.pointer import Pointer


class CrossCursor(Pointer):

    cross_bg_width = 11
    cross_width = 1
    cross_half_length = 35
    cross_center_offset = 3
    colors = {
        # 'Healthy': {
        #     'bg': 'ffc107',
        #     'fc': '000'
        # },
        # 'Bumpy': {
        #     'bg': '00bcd4',
        #     'fc': '000'
        # },
        'Healthy': {
            'bg': '000',
            'fc': '000'
        },
        'Bumpy': {
            'bg': '000',
            'fc': '000'
        },
    }
    bg_opacity = .15
    circle_size = 20
    circle_bg_width = 7
    circle_width = 2
    circle_color = '666'

    def __init__(self, parent=None, **kwargs):
        super(CrossCursor, self).__init__(**kwargs)
        self.registerInstance(self, parent)

        color = self.colors['Healthy']
        if 'Bumpy' in self._device.rui_proxy_name:
            color = self.colors['Bumpy']

        if 'Bumpy' not in self._device.rui_proxy_name:
            avg.CircleNode(
                parent=self,
                r=self.circle_size,
                strokewidth=self.circle_bg_width,
                fillopacity=0,
                color=color['bg'],
                opacity=self.bg_opacity
            )
            avg.CircleNode(
                parent=self,
                r=self.circle_size,
                strokewidth=self.circle_width,
                fillopacity=0,
                color=self.circle_color
            )
        else:
            w = self.circle_size * 1.75
            hW = w * .5
            avg.RectNode(
                parent=self,
                size=(w, w),
                pos=(-hW, -hW),
                strokewidth=self.circle_bg_width,
                fillopacity=0,
                color=color['bg'],
                opacity=self.bg_opacity
            )
            avg.RectNode(
                parent=self,
                size=(w, w),
                pos=(-hW, -hW),
                strokewidth=self.circle_width,
                fillopacity=0,
                color=self.circle_color
            )

        # draw cross
        diff = (self.cross_bg_width-self.cross_width) * .5
        avg.LineNode(
            parent=self,
            pos1=(-self.cross_half_length+diff, 0),
            pos2=(-self.cross_center_offset-diff, 0),
            strokewidth=self.cross_width,
            color=color['fc']
        )
        avg.LineNode(
            parent=self,
            pos1=(self.cross_half_length-diff, 0),
            pos2=(self.cross_center_offset+diff, 0),
            strokewidth=self.cross_width,
            color=color['fc']
        )
        avg.LineNode(
            parent=self,
            pos1=(0, -self.cross_half_length+diff),
            pos2=(0, -self.cross_center_offset-diff),
            strokewidth=self.cross_width,
            color=color['fc']
        )
        avg.LineNode(
            parent=self,
            pos1=(0, self.cross_half_length-diff),
            pos2=(0, self.cross_center_offset+diff),
            strokewidth=self.cross_width,
            color=color['fc']
        )
