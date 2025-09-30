from ..bl_ui_widget import *

import blf
import bpy

class BL_UI_Button(BL_UI_Widget):
    
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)
        self._text_color        = (1.0, 1.0, 1.0, 1.0)
        self._hover_bg_color    = (0.5, 0.5, 0.5, 1.0)
        self._select_bg_color   = (0.7, 0.7, 0.7, 1.0)
        
        self._text = "Button"
        self._text_size = 16
        self._textpos = (x, y)

        self.__state = 0
        self.__image = None
        self.__image_size = (24, 24)
        self.__image_position = (4, 2)

        self.base_image_size = self.__image_size[0]

        self.shader_img = gpu.shader.from_builtin('IMAGE' if bpy.app.version[0] >= 4 else '2D_IMAGE')

    @property
    def text_color(self):
        return self._text_color

    @text_color.setter
    def text_color(self, value):
        self._text_color = value

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        self._text = value
                
    @property
    def text_size(self):
        return self._text_size

    @text_size.setter
    def text_size(self, value):
        self._text_size = value

    @property
    def hover_bg_color(self):
        return self._hover_bg_color

    @hover_bg_color.setter
    def hover_bg_color(self, value):
        self._hover_bg_color = value

    @property
    def select_bg_color(self):
        return self._select_bg_color

    @select_bg_color.setter
    def select_bg_color(self, value):
        self._select_bg_color = value 
        
    def set_image_size(self, image_size):
        self.__image_size = image_size
        self.base_image_size = self.__image_size[0]

    def set_image_position(self, image_position):
        self.__image_position = image_position

    def set_image(self, rel_filepath):
        try:
            self.__image = bpy.data.images.load(rel_filepath, check_existing=True)   

            self.__image.gl_load()
        except:
            pass

    def update(self, x, y):        
        super().update(x, y)
        self._textpos = [x, y]

    def update_to_ui_scale(self):
        super().update_to_ui_scale()

        new_size  =  int(self.base_image_size - ((self.base_image_size - (self.base_image_size * bpy.context.preferences.view.ui_scale)) * 0.8))
        if new_size == self.__image_size[0]:
            return

        self.__image_size = (new_size, new_size)
        
    def draw(self):
        if not self.visible or not self.is_widget_active:
            return
            
        area_height = self.get_area_height()

        self.shader.bind()
        self.set_colors()
        
        gpu.state.blend_set("ALPHA")
        self.batch_panel.draw(self.shader) 
        self.draw_image()   
        gpu.state.blend_set("NONE")

        
        # Draw text
        self.draw_text(area_height)

    def set_colors(self):
        color = self._bg_color
        text_color = self._text_color

        # pressed
        if self.__state == 1:
            color = self._select_bg_color

        # hover
        elif self.__state == 2:
            color = self._hover_bg_color

        self.shader.uniform_float("color", color)

    def draw_text(self, area_height):
        if bpy.app.version[0] < 4:
            blf.size(0, self._text_size, 72)
        else:
            blf.size(0, self._text_size)

        size = blf.dimensions(0, self._text)

        textpos_y = area_height - self._textpos[1] - (self.height + size[1]) / 2.0
        blf.position(0, self._textpos[0] + (self.width - size[0]) / 2.0, textpos_y + 1, 0)

        r, g, b, a = self._text_color
        blf.color(0, r, g, b, a)

        blf.draw(0, self._text)

    def draw_image(self):
        if self.__image is not None:
            try:
                if self.__image.bindcode == 0:
                    self.__image.gl_load()

                y_screen_flip = self.get_area_height() - self.y_screen
                off_x, off_y =  self.__image_position
                sx, sy = self.__image_size
                
                # bottom left, top left, top right, bottom right
                vertices = (
                            (self.x_screen + off_x, y_screen_flip - off_y), 
                            (self.x_screen + off_x, y_screen_flip - sy - off_y), 
                            (self.x_screen + off_x + sx, y_screen_flip - sy - off_y),
                            (self.x_screen + off_x + sx, y_screen_flip - off_y))
                
                self.batch_img = batch_for_shader(
                    self.shader_img, 'TRI_FAN', 
                    { "pos" : vertices, 
                    "texCoord": ((0, 1), (0, 0), (1, 0), (1, 1)) 
                    },
                )

                tex = gpu.texture.from_image(self.__image)

                gpu.state.blend_set('ALPHA')

                self.shader_img.bind()
                self.shader_img.uniform_sampler("image", tex)
                self.batch_img.draw(self.shader_img)

                gpu.state.blend_set('NONE')

                return True
            except Exception as e:
                print("Button draw image failed:", e)

        return False     
        
    def set_mouse_down(self, mouse_down_func):
        self.mouse_down_func = mouse_down_func   
                 
    def mouse_down(self, x, y):    
        self.update_x_offset()
        
        if self.is_in_rect(x,y):
            self.__state = 1
            try:
                self.mouse_down_func()
            except Exception as e:
                print("Button click error:", e)
                
            return True
        
        return False
    
    def mouse_move(self, x, y):
        if self.is_in_rect(x,y):
            if(self.__state != 1):
                
                # hover state
                self.__state = 2
        else:
            self.__state = 0
 
    def mouse_up(self, x, y):
        if self.is_in_rect(x,y):
            self.__state = 2
        else:
            self.__state = 0