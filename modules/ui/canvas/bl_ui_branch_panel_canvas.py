from .bl_ui_panel_canvas import *
from ...utils.drawing_utils import draw_stroke, attach_stroke_to_nearest_point

class BL_UI_Branch_Panel_Canvas(BL_UI_Panel_Canvas):

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)

    def mouse_down(self, x, y): 
        self.update_x_offset()

        if self.is_widget_active and self.is_in_rect(x,y): 
            branch_shape_settings = bpy.context.scene.branch_shape_canvas_settings
            strokes = branch_shape_settings.strokes 
            if len(strokes) == 2: 
                return False
            
            p = strokes.add().points.add() 
            p.point = (x - self.x_offset, y) 

            self.is_drawing = True 

            branch_shape_settings.x_norm_factor = self.x_screen 
            branch_shape_settings.y_norm_factor = self.get_area_height() - self.y_screen - self.height

            return True 
        
        return False

    def mouse_move(self, x, y):
        if self.is_drawing and self.is_in_rect(x, y):
            strokes = bpy.context.scene.branch_shape_canvas_settings.strokes
            if len(strokes) > 0:
                p = strokes[-1].points.add()
                p.point = (x - self.x_offset, y)

    def mouse_up(self, x, y):
        if self.is_drawing:
            self.is_drawing = False

            strokes = bpy.context.scene.branch_shape_canvas_settings.strokes
            if len(strokes) > 1:           
                existing_points = strokes[0].points
                new_stroke_points = [tuple(p.point) for p in strokes[-1].points]
                comparison_points = [tuple(existing_points[0].point), tuple(existing_points[-1].point)]
            
                widget_x = self.x_screen
                widget_y = self.get_area_height() - self.y_screen
                attached_stroke = attach_stroke_to_nearest_point(new_stroke_points, [comparison_points], limit = {"xmin": widget_x, "xmax": widget_x + self.width, "ymin": widget_y - self.height, "ymax": widget_y})
                
                # Clear
                while strokes[-1].points:
                    strokes[-1].points.remove(0)

                for point in attached_stroke:
                    p = strokes[-1].points.add()
                    p.point = (point[0], point[1])

    def draw(self):
        if not self.is_widget_active:
            return

        branch_shape_canvas_settings = bpy.context.scene.branch_shape_canvas_settings
        y_offset = self.get_area_height() - (branch_shape_canvas_settings.y_norm_factor + self.y_screen + self.height)

        for stroke in branch_shape_canvas_settings.strokes:
            if len(stroke.points) > 1:
                stroke_data = [(p.point[0], p.point[1] + y_offset) for p in stroke.points]
                draw_stroke(stroke_data, self._brush_color, self._brush_size)

    def clear(self):
        strokes = bpy.context.scene.branch_shape_canvas_settings.strokes
        for i in reversed(range(len(strokes))):
            strokes.remove(i)

        if self.context and self.context.area:
            self.context.area.tag_redraw()
