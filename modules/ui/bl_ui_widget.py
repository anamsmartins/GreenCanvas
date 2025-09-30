import gpu
import bpy

from gpu_extras.batch import batch_for_shader

class BL_UI_Widget:
    
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.x_screen = x
        self.y_screen = y
        self.width = width
        self.height = height
        self._bg_color = (0.8, 0.8, 0.8, 1.0)
        self._outline_color = (0, 0, 0, 1.0)
        self._outline_size = 0
        self._tag = None
        self.context = None
        self.__inrect = False
        self._mouse_down = False
        self._is_visible = True
        self._is_widget_active = None
        self._region_type = "WINDOW"
        self.x_offset = 0

        self.base_x = self.x
        self.base_y = self.y
        self.base_width = self.width
        self.base_height = self.height
        self.last_height = self.height
        
    def set_location(self, x, y):
        self.x = x
        self.y = y
        self.x_screen = x
        self.y_screen = y
        self.update(x,y)

    @property
    def bg_color(self):
        return self._bg_color

    @bg_color.setter
    def bg_color(self, value):
        self._bg_color = value

    @property
    def outline_color(self):
        return self._outline_color

    @outline_color.setter
    def outline_color(self, value):
        self._outline_color = value

    @property
    def outline_size(self):
        return self._outline_size

    @outline_size.setter
    def outline_size(self, value):
        self._outline_size = value

    @property
    def visible(self):
        return self._is_visible

    @visible.setter
    def visible(self, value):
        self._is_visible = value

    @property
    def tag(self):
        return self._tag

    @tag.setter
    def tag(self, value):
        self._tag = value

    @property
    def is_widget_active(self):
        return self._is_widget_active() if self._is_widget_active else True

    @is_widget_active.setter
    def is_widget_active(self, function):
        self._is_widget_active = function

    @property
    def region_type(self):
        return self._region_type

    @region_type.setter
    def region_type(self, value):
        self._region_type = value
                		    
    def draw(self):
        if not self.visible or not self.is_widget_active:
            return
        
        if self.region_type == "UI":
            self.update_to_ui_scale()
                
        gpu.state.blend_set("ALPHA")

        # Draw background
        self.shader.bind()
        self.shader.uniform_float("color", self._bg_color)
        self.batch_panel.draw(self.shader) 

        gpu.state.blend_set("NONE")
        
        self.draw_outline(self._outline_size)

    def get_vertices(self):
        area_height = self.get_area_height()
                
        y_screen_flip = area_height - self.y_screen

        # bottom left, top left, top right, bottom right, 
        return (
            (self.x_screen, y_screen_flip), 
            (self.x_screen, y_screen_flip - self.height), 
            (self.x_screen + self.width, y_screen_flip - self.height),
            (self.x_screen + self.width, y_screen_flip),
        )

    def draw_outline(self, size=5.0):
        vertices = self.get_vertices()
        x0 = vertices[0][0]  # left
        x1 = vertices[2][0]  # right
        y0 = vertices[1][1]  # bottom
        y1 = vertices[0][1]  # top

        verts = [
            (x0 - size, y0 - size),
            (x0, y0),
            (x0, y1),
            (x0 - size, y1 + size),

            (x0, y1),
            (x1, y1),
            (x1 + size, y1 + size),
            (x0 - size, y1 + size),

            (x1, y1),
            (x1, y0),
            (x1 + size, y0 - size),
            (x1 + size, y1 + size),

            (x1, y0),
            (x0, y0),
            (x0 - size, y0 - size),
            (x1 + size, y0 - size),
        ]


        # Two triangles per quad
        indices = [
            (0, 1, 2), (0, 2, 3),     # left
            (4, 5, 6), (4, 6, 7),     # top
            (8, 9,10), (8,10,11),     # right
            (12,13,14), (12,14,15),   # bottom
        ]

        shader = gpu.shader.from_builtin('UNIFORM_COLOR' if bpy.app.version[0] >= 4 else '2D_UNIFORM_COLOR')
        batch = batch_for_shader(shader, 'TRIS', {"pos": verts}, indices=indices)

        gpu.state.blend_set("ALPHA")
        shader.bind()
        shader.uniform_float("color", self._outline_color)
        batch.draw(shader)
        gpu.state.blend_set("NONE")

    def update_x_offset(self):
        if self.region_type == "UI":
            area_width = self.get_area_width()
            region_width = self.get_region_width("UI")
            self.x_offset = area_width - region_width

    def update_to_ui_scale(self):
        region_w = self.get_region_width(self.region_type)
        region_h = self.get_region_height(self.region_type)

        new_width = int((self.base_width  * region_w) / (self.base_region_width))
        self.width  = new_width

        new_x = int((self.base_x  * region_w) / (self.base_region_width))

        if region_h == self.last_height:
            self.set_location(new_x, self.y)
            return
        
        self.last_height = region_h
        
        height_factor = ((self.base_height * 100) / self.base_width) / 100
        self.height  = int(self.width * height_factor)

        y_factor = ((self.base_y * 100) / max(self.base_x, 0.01)) / 100
        new_y = int(new_x * y_factor)

        self.set_location(new_x, new_y)

    def init(self, context):
        self.context = context

        if self.region_type == "WINDOW":
            self.base_region_width = 1378
            self.base_region_height = 820
        elif self.region_type == "UI":
            self.base_region_width = 220
            self.base_region_height = 800

        self.update_x_offset()

        self.update(self.x, self.y)

    def update(self, x, y):

        self.x_screen = x
        self.y_screen = y
                
        indices = ((0, 1, 2), (0, 2, 3))

        vertices = self.get_vertices()
                    
        self.shader = gpu.shader.from_builtin('UNIFORM_COLOR' if bpy.app.version[0] >= 4 else '2D_UNIFORM_COLOR')
        self.batch_panel = batch_for_shader(self.shader, 'TRIS', {"pos" : vertices}, indices=indices)
    
    def handle_event(self, event):
        x = event.mouse_region_x
        y = event.mouse_region_y

        if(event.type == 'LEFTMOUSE'):
            if(event.value == 'PRESS'):
                self._mouse_down = True
                return self.mouse_down(x, y)
            else:
                self._mouse_down = False
                self.mouse_up(x, y)
                
        
        elif(event.type == 'MOUSEMOVE'):
            self.mouse_move(x, y)

            inrect = self.is_in_rect(x, y)

            # we enter the rect
            if not self.__inrect and inrect:
                self.__inrect = True
                self.mouse_enter(event, x, y)

            # we are leaving the rect
            elif self.__inrect and not inrect:
                self.__inrect = False
                self.mouse_exit(event, x, y)

            return False

        elif event.value == 'PRESS' and (event.ascii != '' or event.type in self.get_input_keys()):
            return self.text_input(event)
                        
        elif event.type == 'U' and event.value == 'PRESS' and event.ctrl:
            return self.undo()
        
        elif event.type == 'Y' and event.value == 'PRESS' and event.ctrl:
            return self.redo()

        return False 

    def get_input_keys(self):
        return []

    def get_area_height(self):
        return self.context.area.height    
    
    def get_area_width(self):
        return self.context.area.width

    def get_region_width(self, region_type):
        for region in self.context.area.regions:
            if region.type == region_type:
                return region.width

        return None
    
    def get_region_height(self, region_type):
        for region in self.context.area.regions:
            if region.type == region_type:
                return region.height
            
        return None

    def is_in_rect(self, x, y):
        widget_x = self.x_offset + self.x_screen
        widget_y = self.get_area_height() - self.y_screen

        if (
            (widget_x <= x <= (widget_x + self.width)) and 
            ((widget_y - self.height) <= y <= widget_y)
            ):
            return True
           
        return False      

    def text_input(self, event):       
        return False

    def mouse_down(self, x, y):       
        return self.is_in_rect(x,y)

    def mouse_up(self, x, y):
        pass

    def set_mouse_enter(self, mouse_enter_func):
        self.mouse_enter_func = mouse_enter_func  
 
    def call_mouse_enter(self):
        try:
            if self.mouse_enter_func:
                self.mouse_enter_func(self)
        except:
            pass

    def mouse_enter(self, event, x, y):
        self.call_mouse_enter()

    def set_mouse_exit(self, mouse_exit_func):
        self.mouse_exit_func = mouse_exit_func  
 
    def call_mouse_exit(self):
        try:
            if self.mouse_exit_func:
                self.mouse_exit_func(self)
        except:
            pass

    def mouse_exit(self, event, x, y):
        self.call_mouse_exit()

    def mouse_move(self, x, y):
        pass

    def undo(self):
        pass

    def redo(self):
        pass

    def clear_locals(self):
        pass