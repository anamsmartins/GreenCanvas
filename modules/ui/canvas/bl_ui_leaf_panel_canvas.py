from .bl_ui_panel_canvas import *
from ...utils.drawing_utils import draw_stroke

class BL_UI_Leaf_Panel_Canvas(BL_UI_Panel_Canvas):

    def mouse_down(self, x, y):
        self.update_x_offset()

        if self.is_widget_active and self.is_in_rect(x,y):
            leaf_curvature_type_canvas_settings = bpy.context.scene.leaf_curvature_type_canvas_settings
            points = leaf_curvature_type_canvas_settings.stroke.points
            if len(points) > 0:
                return False
            
            points.add()
            p = points[-1]
            p.point = (x - self.x_offset, y)
            self.is_drawing = True

            leaf_curvature_type_canvas_settings.x_norm_factor = self.x_screen 
            leaf_curvature_type_canvas_settings.y_norm_factor = self.get_area_height() - self.y_screen - self.height
           
            return True
        
        return False

    def mouse_move(self, x, y):
        if self.is_widget_active and self.is_drawing and self.is_in_rect(x, y):
            points = bpy.context.scene.leaf_curvature_type_canvas_settings.stroke.points
            points.add()
            p = points[-1] 
            p.point = (x - self.x_offset, y)

    def mouse_up(self, x, y):
        if self.is_widget_active:
            self.is_drawing = False

    def draw(self):
        if not self.is_widget_active:
            return
        
        leaf_curvature_type_canvas_settings = bpy.context.scene.leaf_curvature_type_canvas_settings
        y_offset = self.get_area_height() - (leaf_curvature_type_canvas_settings.y_norm_factor + self.y_screen + self.height)

        points = leaf_curvature_type_canvas_settings.stroke.points
        if len(points) > 1:
            stroke_data = [(p.point[0], p.point[1] + y_offset) for p in points]
            draw_stroke(stroke_data, self._brush_color, self._brush_size)

    def clear(self):
        bpy.context.scene.leaf_curvature_type_canvas_settings.stroke.points.clear()
        self.context.area.tag_redraw()
