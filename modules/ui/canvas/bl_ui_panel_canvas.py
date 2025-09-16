from ..bl_ui_widget import *

class BL_UI_Panel_Canvas(BL_UI_Widget):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)
        self._brush_color = (1, 1, 1, 1)
        self.is_drawing = False

    @property
    def brush_color(self):
        return self._brush_color

    @brush_color.setter
    def brush_color(self, value):
        self._brush_color = value

    @property
    def brush_size(self):
        return self._brush_size

    @brush_size.setter
    def brush_size(self, value):
        self._brush_size = value
