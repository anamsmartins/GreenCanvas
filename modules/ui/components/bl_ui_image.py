from ..bl_ui_widget import *
import bpy
import gpu
from gpu_extras.batch import batch_for_shader

class BL_UI_Image(BL_UI_Widget):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)
        self.__image = "Image"
        self.__size = (width, height)
        self.__position = (0, 0)

        self.base_size = self.__size[0]

        self.shader_img = gpu.shader.from_builtin('IMAGE' if bpy.app.version[0] >= 4 else '2D_IMAGE')

    def set_size(self, size):
        self.__size = size
        self.base_size = self.__size[0]

    def set_position(self, position):
        self.__position = position

    def set_image(self, rel_filepath):
        try:
            self.__image = bpy.data.images.load(rel_filepath, check_existing=True)   

            self.__image.gl_load()
        except:
            pass

    def update(self, x, y):        
        super().update(x, y)
        self.draw_image()  

    def draw(self):
        if not self.visible or not self.is_widget_active:
            return

        self.shader.bind()
        
        gpu.state.blend_set("ALPHA")
        self.draw_image()   
        gpu.state.blend_set("NONE")

    def draw_image(self):
        if self.__image is not None:
            try:
                if self.__image.bindcode == 0:
                    self.__image.gl_load()

                y_screen_flip = self.get_area_height() - self.y_screen
                off_x, off_y =  self.__position
                sx, sy = self.__size
                
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
                print("Draw image failed:", e)

        return False   
    