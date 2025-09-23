from ..bl_ui_widget import *

import blf

class BL_UI_Slider(BL_UI_Widget):
    
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)
        self._text_color        = (1.0, 1.0, 1.0, 1.0)
        self._color          = (0.5, 0.5, 0.7, 1.0)
        self._hover_color    = (0.5, 0.5, 0.8, 1.0)
        self._select_color   = (0.7, 0.7, 0.7, 1.0)
        self._bg_color       = (0.8, 0.8, 0.8, 0.6)

        self._min = 0
        self._max = 100
        
        self.x_screen = x
        self.y_screen = y
        
        self._text_size = 10
        self._font_id = 0
        self._decimals = 0

        self._show_min_max = True

        self.__state = 0
        self.__is_drag = False
        self.__slider_pos = 0
        self.__slider_value = round(0, self._decimals)
        self.__slider_width = 5 # handler width
        self.__slider_height = 13 # handler height
        self.__slider_offset_y = 3

        self.base_slider_width = self.__slider_width
        self.base_slider_height = self.__slider_height
        self.base_text_size = self._text_size

        self._region_type = "WINDOW"
        
    @property
    def text_color(self):
        return self._text_color

    @text_color.setter
    def text_color(self, value):
        self._text_color = value

    @property
    def text_size(self):
        return self._text_size

    @text_size.setter
    def text_size(self, value):
        self._text_size = value

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        self._color = value

    @property
    def hover_color(self):
        return self._hover_color

    @hover_color.setter
    def hover_color(self, value):
        self._hover_color = value

    @property
    def select_color(self):
        return self._select_color

    @select_color.setter
    def select_color(self, value):
        self._select_color = value

    @property
    def min(self):
        return self._min

    @min.setter
    def min(self, value):
        self._min = value

    @property
    def max(self):
        return self._max

    @max.setter
    def max(self, value):
        self._max = value

    @property
    def decimals(self):
        return self._decimals

    @decimals.setter
    def decimals(self, value):
        self._decimals = value

    @property
    def show_min_max(self):
        return self._show_min_max

    @show_min_max.setter
    def show_min_max(self, value):
        self._show_min_max = value

    @property
    def region_type(self):
        return self._region_type

    @region_type.setter
    def region_type(self, value):
        self._region_type = value

    def draw(self):   
        if not self.visible or not self.is_widget_active:
            return

        self.update_slider()
        area_height = self.get_area_height()

        self.shader.bind()
        
        color = self._color
        
        # pressed
        if self.__state == 1:
            color = self._select_color

        # hover
        elif self.__state == 2:
            color = self._hover_color

        # Draw background
        self.shader.uniform_float("color", self._bg_color)
        gpu.state.blend_set("ALPHA")

        self.batch_bg.draw(self.shader)

        # Draw slider   
        self.shader.uniform_float("color", color)
        self.batch_slider.draw(self.shader) 
        
        # Draw value text
        sFormat = "{:0." + str(self._decimals) + "f}"
        if bpy.app.version[0] < 4:
            blf.size(0, self._text_size, 72)
        else:
            blf.size(self._font_id, self._text_size)
        
        sValue = sFormat.format(self.__slider_value)
        size = blf.dimensions(self._font_id, sValue)

        blf.position(self._font_id, self.__slider_pos + 1 + self.x_screen - size[0] / 2.0, area_height - self.y_screen + self.__slider_offset_y, 0)

        r, g, b, a = self._text_color
        blf.color(self._font_id, r, g, b, a)
        blf.draw(self._font_id, sValue)


        # Draw min and max
        if self._show_min_max:
            sMin = sFormat.format(self._min)
            
            size = blf.dimensions(self._font_id, sMin)
                        
            r, g, b, a = self._text_color
            blf.color(self._font_id, r, g, b, a)
            blf.position(self._font_id, self.x_screen - size[0] / 2.0, 
                            area_height - self.height - self.y_screen, 0)
            blf.draw(self._font_id, sMin)

            sMax = sFormat.format(self._max)
            
            size = blf.dimensions(self._font_id, sMax)

            r, g, b, a = self._text_color
            blf.color(self._font_id, r, g, b, a)
                        
            blf.position(self._font_id, self.x_screen + self.width - size[0] / 2.0, 
                            area_height - self.height - self.y_screen, 0)
            blf.draw(self._font_id, sMax)

        gpu.state.blend_set("NONE")

    def update_slider(self):
        # Slider triangles
        # 
        #        0
        #     1 /\ 2
        #      |  |
        #     3---- 4

        # batch for slider

        self.update_slider_handler()

        self.update_slider_background()        
        
    def update_slider_handler(self):
        h = self.__slider_height
        w = self.__slider_width

        pos_y = self.get_area_height() - self.y_screen - self.height / 2.0 + self.__slider_height / 2.0 + self.__slider_offset_y
        pos_x = self.x_screen + self.__slider_pos
        
        indices = ((0, 1, 2), (1, 2, 3), (3, 2, 4))
        
        vertices = (
                    (pos_x    , pos_y    ),
                    (pos_x - w, pos_y - w),
                    (pos_x + w, pos_y - w),
                    (pos_x - w, pos_y - h),
                    (pos_x + w, pos_y - h)
                   )
                    
        self.shader = gpu.shader.from_builtin('UNIFORM_COLOR' if bpy.app.version[0] >= 4 else '2D_UNIFORM_COLOR')
        self.batch_slider = batch_for_shader(self.shader, 'TRIS', 
        {"pos" : vertices}, indices=indices)
        
    def update_slider_background(self):
        pos_y = self.get_area_height() - self.y_screen - self.height / 2.0
        pos_x = self.x_screen

        indices = ((0, 1, 2), (0, 2, 3))

        # bottom left, top left, top right, bottom right
        vertices = (
                    (pos_x, pos_y), 
                    (pos_x, pos_y + 4), 
                    (pos_x + self.width, pos_y + 4),
                    (pos_x + self.width, pos_y)
        )

        self.batch_bg = batch_for_shader(self.shader, 'TRIS', {"pos" : vertices}, indices=indices)
    
    def update(self, x, y): 
        # Min                      Max
        #  |---------V--------------|
        
        self.x_screen = x
        self.y_screen = y
        
        self.update_slider()

    def update_to_ui_scale(self):
        super().update_to_ui_scale()

        region_w = self.get_region_width(self.region_type)
        region_h = self.get_region_height(self.region_type)

        new_slider_width = int((self.base_slider_width * region_w) / (self.base_region_width))
        if new_slider_width == self.__slider_width:
            return

        self.__slider_width = new_slider_width
        self._text_size = int(self.base_text_size * bpy.context.preferences.view.ui_scale)
        self.__slider_pos = self.__value_to_pos(self.__slider_value)
 
    def set_value_change(self, value_change_func):
        self.value_change_func = value_change_func

    def set_on_mouse_down_popup(self, on_mouse_down_popup):
        self.on_mouse_down_popup = on_mouse_down_popup
    
    def is_in_rect(self, x, y):
        area_height = self.get_area_height()

        slider_y = area_height - self.y_screen - self.height / 2.0 + self.__slider_height / 2.0 + self.__slider_offset_y
        
        if (
            (self.x_offset + self.x_screen + self.__slider_pos - self.__slider_width <= x <= 
            (self.x_offset + self.x_screen + self.__slider_pos + self.__slider_width)) and 
            (slider_y >= y >= slider_y - self.__slider_height)
            ):
            return True
           
        return False

    def __value_to_pos(self, value):
        return self.width * (value - self._min) / (self._max - self._min)

    def __pos_to_value(self, pos):
        return self._min + round(((self._max - self._min) * self.__slider_pos / self.width), self._decimals)

    def get_value(self):
        return self.__slider_value

    def set_value(self, value):
        if value < self._min:
            value = self._min
        if value > self._max:
            value = self._max

        if value != self.__slider_value:
            self.__slider_value = round(value, self._decimals)

            try:
                self.value_change_func(self, self.__slider_value)
            except:
                pass

            self.__slider_pos = self.__value_to_pos(self.__slider_value)

            if self.context is not None:
                self.update_slider()


    def __set_slider_pos(self, x):
        offset = 0
        if self._region_type == "UI":
            offset = self.get_area_width() - self.get_region_width(self._region_type)
        
        if x <= self.x_screen + offset:
            self.__slider_pos = 0
        elif x >= self.x_screen + self.width + offset:
            self.__slider_pos = self.width
        else:
            self.__slider_pos = x - (offset + self.x_screen)

        newValue = self.__pos_to_value(self.__slider_pos)

        if newValue != self.__slider_value:
            self.__slider_value = newValue

            try:
                self.value_change_func(self, self.__slider_value)
            except:
                pass
                 
    def mouse_down(self, x, y):
        if not (self._is_visible and self.is_widget_active):
            return False

        self.update_x_offset()

        if self.is_in_rect(x,y):
            try:
                is_valid = self.on_mouse_down_popup()
                if not is_valid:
                    return
            except:
                pass

            self.__state = 1
            self.__is_drag = True
                
            return True
        
        return False
    
    def mouse_move(self, x, y):
        if self._is_visible and self.is_widget_active and self.is_in_rect(x,y):
            if(self.__state != 1):
                
                # hover state
                self.__state = 2
        else:
            self.__state = 0
        
        if self.__is_drag:
            self.__set_slider_pos(x)
            self.update(self.x_screen, self.y_screen)
 
    def mouse_up(self, x, y):
        if self._is_visible and self.is_widget_active:
            self.__state = 0
            self.__is_drag = False