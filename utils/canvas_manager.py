from libavg import avg, player


class CanvasManager(object):
    __radius = 200
    __circle_canvases = []
    __image_nodes_from_files = {}

    @staticmethod
    def get_circle_canvas_from_color(color, radius=__radius, stroke_width=1.0, stroke_color=avg.Color("c0c0c0"),
                                     fake_opacity=1.0):
        if color is None:
            raise ValueError("CanvasManager.get_circle_canvas_from_color: color for canvas cannot be None.")
        if isinstance(color, str):
            color = avg.Color(color)
        if not isinstance(color, avg.Color):
            raise ValueError("CanvasManager.get_circle_canvas_from_color: color for canvas must be type avg.Color.")

        # TODO: Fix the problem with the wrong stroke color string.
        canvas_id = "circle_%d-%d-%d_%d_%s_%d" % (color.r, color.g, color.b, stroke_width, "c0c0c0", fake_opacity)

        # check if color in already existing canvases
        if canvas_id in CanvasManager.__circle_canvases:
            return "canvas:%s" % canvas_id  # CanvasManager.__circle_canvases[color]

        # create canvas and add to circle canvases
        size = avg.Point2D(CanvasManager.__radius, CanvasManager.__radius) * 2 + (2, 2)
        canvas = player.createCanvas(id=canvas_id, autorender=False, multisamplesamples=8, size=size)
        if fake_opacity != 1.0:
            avg.CircleNode(
                pos=(size / 2) + (1, 1),
                r=CanvasManager.__radius,
                strokewidth=0.0,
                fillopacity=1.0,
                fillcolor='fff',
                parent=canvas.getRootNode()
            )
        avg.CircleNode(
                pos=(size / 2) + (1, 1),
                r=CanvasManager.__radius,
                color=stroke_color,
                strokewidth=stroke_width,
                fillopacity=fake_opacity,
                fillcolor=color,
                parent=canvas.getRootNode()
        )
        canvas.render()
        CanvasManager.__circle_canvases.append(canvas_id)
        return "canvas:%s" % canvas_id
