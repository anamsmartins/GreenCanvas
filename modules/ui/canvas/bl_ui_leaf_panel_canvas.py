from .bl_ui_panel_canvas import *
from ...utils.drawing_utils import draw_stroke

class BL_UI_Leaf_Panel_Canvas(BL_UI_Panel_Canvas):

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)
        self._brush_size = 2
        self.curvature_type = []

    def mouse_down(self, x, y):
        self.update_x_offset()

        if self.is_widget_active and self.is_in_rect(x,y):
            if len(self.curvature_type) > 0:
                return False

            self.is_drawing = True
            self.curvature_type.append((x - self.x_offset, y))
           
            return True
        
        return False

    def mouse_move(self, x, y):
        if self.is_widget_active and self.is_drawing and self.is_in_rect(x, y):
            self.curvature_type.append((x - self.x_offset, y))

    def mouse_up(self, x, y):
        if self.is_widget_active and self.is_drawing:
            self.is_drawing = False

            self.curvature_type.append((x - self.x_offset, y))

            # save to scene
            x_norm_factor = self.x_screen 
            y_norm_factor = self.get_area_height() - self.y_screen - self.height

            normed_curvature_type = [] 
            for pt in self.curvature_type:
                normed_curvature_type.append((pt[0] - x_norm_factor, pt[1] - y_norm_factor))

            curvature_type = self.format_curvature_type(normed_curvature_type)

            # normalize so first point of curvature type is (0,0) and store in scene variable
            dx, dy = curvature_type[0]
            new_curvature_type = [(x - dx, y - dy) for (x, y) in curvature_type]

            curvature_points = bpy.context.scene.leaf_curvature_type_canvas_settings.stroke
            for point in new_curvature_type:
                new_point = curvature_points.add()
                new_point.x = point[0]
                new_point.y = point[1]

    def format_curvature_type(self, curvature_type):
        # If reversed (left to right or top to bottom)
        init_x, init_y = curvature_type[0][0], curvature_type[0][1]
        last_x, last_y = curvature_type[-1][0], curvature_type[-1][1]

        if last_x < init_x or last_y < init_y:
            reversed_curvature_type = curvature_type[::-1]
            curvature_type.clear()
            for pt in reversed_curvature_type:
                curvature_type.append((pt[0], pt[1]))
                
        # If vertical then convert to horizontal
        init_x, init_y = curvature_type[0][0], curvature_type[0][1]
        last_x, last_y = curvature_type[-1][0], curvature_type[-1][1]

        if  last_y - init_y > last_x - init_x:
            curvature_type = [(p[1], p[0]) for p in curvature_type]
        
        return curvature_type

    def draw(self):
        if not self.is_widget_active:
            return

        if len(self.curvature_type) > 1:
            draw_stroke(self.curvature_type, self._brush_color, self._brush_size)

    def clear(self):
        self.curvature_type.clear()
        bpy.context.scene.leaf_curvature_type_canvas_settings.stroke.clear()
        self.context.area.tag_redraw()
