from libavg import avg
from utils.canvas_manager import CanvasManager
import configs.visual_data as config_visual
import configs.config_app as config_app


class ColoredCircleView(avg.DivNode):

    def __init__(self, point_model, parent=None, **kwargs):
        super(ColoredCircleView, self).__init__(**kwargs)
        self.registerInstance(self, parent)

        self.__point_model = point_model
        size = (self.__point_model.width, self.__point_model.height)
        self.__current_scale = 1.0

        color = self.__point_model.color
        # selecting color by attribute
        # value = self.__point_model.get_attribute(config_visual.MAP_POINT_COLOR_ATTRIBUTE['name'])
        # if value is not None and value != 'None':
        #     start_color = avg.Color(config_visual.MAP_POINT_COLOR_ATTRIBUTE["start_color"])
        #     end_color = avg.Color(config_visual.MAP_POINT_COLOR_ATTRIBUTE["end_color"])
        #     min_val = config_visual.MAP_POINT_COLOR_ATTRIBUTE['min']
        #     max_val = config_visual.MAP_POINT_COLOR_ATTRIBUTE['max']
        #     if value == 0.0:
        #         color = avg.Color('888')
        #     else:
        #         val = (value - min_val) / (max_val - min_val)
        #         val = self.clamp(val, 0.0, 1.0)
        #         # logarithmic scale
        #         val = math.logging_base(val+1, 1.5) / math.logging_base(2, 1.5)
        #         color = avg.Color.mix(end_color, start_color, val)
        # elif "CrimeCode" in self.__point_model.attribute_dict:
        #     crime_description = self.__point_model.get_attribute("Description")
        #     if crime_description is not None and crime_description in config_visual.CRIME_DESCRIPTION_COLOR:
        #         color = avg.Color(config_visual.CRIME_DESCRIPTION_COLOR[crime_description])

        # selecting size by attribute (if it exists)
        value = self.__point_model.get_attribute(config_visual.MAP_POINT_SIZE_ATTRIBUTE['name'])
        if value is not None and value != 'None':
            val = (value - config_visual.MAP_POINT_SIZE_ATTRIBUTE['min']) / \
                  (config_visual.MAP_POINT_SIZE_ATTRIBUTE['max'] - config_visual.MAP_POINT_SIZE_ATTRIBUTE['min'])
            val = self.clamp(val, 0.0, 1.0)
            size_in_cm = config_visual.MIN_MAX_MAP_POINT_SIZE_IN_CM[0] + val * \
                    (config_visual.MIN_MAX_MAP_POINT_SIZE_IN_CM[1] - config_visual.MIN_MAX_MAP_POINT_SIZE_IN_CM[0])
            size_x = config_app.pixel_per_cm * size_in_cm
            size = (size_x, size_x)

        self.pos = (-size[0] / 2, -size[1] / 2)

        # Creates an image to represent this point.
        self.__circle = avg.ImageNode(
            size=size,
            href=CanvasManager.get_circle_canvas_from_color(color),
            parent=self,
            opacity=self.__point_model.color_opacity
        )
        self.__color = color

    @property
    def size(self):
        # return super(ColoredCircleView, self).size
        return self.__circle.size

    @size.setter
    def size(self, size):
        self.__circle.size = size

    def update_scale(self, scale_factor):
        self.size = self.size / self.__current_scale * scale_factor
        self.pos = (-self.size[0] / 2, -self.size[1] / 2)
        self.__current_scale = scale_factor

    @property
    def color(self):
        return self.__color

    @color.setter
    def color(self, color):
        self.__circle.href = CanvasManager.get_circle_canvas_from_color(color)
        self.__color = color

    @staticmethod
    def clamp(x, min_val, max_val):
        if x < min_val:
            return min_val
        if x > max_val:
            return max_val
        return x

    def set_visual_props(self, color, opacity):
        self.__circle.opacity = opacity
        self.__circle.href = CanvasManager.get_circle_canvas_from_color(color)
        self.__color = color
