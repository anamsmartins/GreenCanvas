import numpy as np

from .bl_ui_panel_canvas import *
from ...utils.drawing_utils import draw_stroke, attach_stroke_to_nearest_point

class BL_UI_Branch_Panel_Canvas(BL_UI_Panel_Canvas):

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)
        self._brush_size = 1
        self.branches = []

    def mouse_down(self, x, y): 
        self.update_x_offset()

        if self.is_widget_active and self.is_in_rect(x,y): 
            if len(self.branches) == 2:
                return False
            
            self.branches.append([(x - self.x_offset, y)])
            self.is_drawing = True

            return True 
        
        return False

    def mouse_move(self, x, y):
        if self.is_drawing and self.is_in_rect(x, y):
            if len(self.branches) > 0:
                self.branches[-1].append((x - self.x_offset, y))

    def mouse_up(self, x, y):
        if self.is_drawing:
            self.is_drawing = False
            
            if len(self.branches) == 0:
                return

            existing_branch_points = self.branches[0]
            branch_shape_canvas_settings = bpy.context.scene.branch_shape_canvas_settings

            if len(self.branches) < 2:
                branch_shape_canvas_settings.left_stroke.add()    
            else:
                new_branch_points = self.branches[-1]
                existing_branch_ends = [existing_branch_points[0], existing_branch_points[-1]]
            
                widget_x = self.x_screen
                widget_y = self.get_area_height() - self.y_screen
                attached_stroke, _, tip = attach_stroke_to_nearest_point(new_branch_points, [existing_branch_ends], limit = {"xmin": widget_x, "xmax": widget_x + self.width, "ymin": widget_y - self.height, "ymax": widget_y})
                
                self.branches[-1].clear()
                for point in attached_stroke:
                    self.branches[-1].append((point[0], point[1]))
                
                x_norm_factor = widget_x
                y_norm_factor = widget_y - self.height

                branch_tip = (tip[0] - x_norm_factor, tip[1] - y_norm_factor)

                normed_branches = [] 
                for branch in self.branches:
                    normed_branch = []
                    for pt in branch:
                        normed_branch.append((pt[0] - x_norm_factor, pt[1] - y_norm_factor))
                    normed_branches.append(normed_branch)

                left_branch, right_branch = self.normalize_branches(normed_branches[0], normed_branches[1], branch_tip)

                # normalize so first point of first stroke is (0,0) and store in scene variable
                dx, dy = left_branch[0]
                new_left_branch = [(x - dx, y - dy) for (x, y) in left_branch]
                new_right_branch = [(x - dx, y - dy) for (x, y) in right_branch]

                # Adjust shape size to match main canvas
                canvas_width, canvas_height = 160, 65
                target_width, target_height = 700, 700
                
                branch_shape_canvas_settings.left_stroke.clear()
                
                for point in new_left_branch:
                    new_point = branch_shape_canvas_settings.left_stroke.add()
                    new_point.x = point[0]  / canvas_width * target_width
                    new_point.y = point[1]  / canvas_height * target_height

                for point in new_right_branch:
                    new_point = branch_shape_canvas_settings.right_stroke.add()
                    new_point.x = point[0]  / canvas_width * target_width
                    new_point.y = point[1]  / canvas_height * target_height

    def normalize_branches(self, branch_A, branch_B, branch_shape_tip):

        def ensure_tip_last_position(stroke):
            tol = 1e-6
            p0, pN = np.array(stroke[0], float), np.array(stroke[-1], float)
            if np.linalg.norm(p0 - np.array(branch_shape_tip, dtype=float)) <= tol:
                return stroke[::-1]  # reverse so tip is last
            
            return stroke[:]  # already last
        
        branch_A = ensure_tip_last_position(branch_A)
        branch_B = ensure_tip_last_position(branch_B)

        base_branch_A, base_branch_B = np.array(branch_A[0], float), np.array(branch_B[0], float)

        diff_x = base_branch_B[0] - base_branch_A[0] 
        diff_y = base_branch_B[1] - base_branch_A[1]

        # If horizontal (x = y, y = x)
        if abs(diff_y) > abs(diff_x):
            def swap_xy(stroke):
                return [(p[1], p[0]) for p in stroke]
            base_branch_A = swap_xy(branch_A)
            base_branch_B = swap_xy(branch_B)
            branch_shape_tip = (branch_shape_tip[1], branch_shape_tip[0])

        base_branch_A, base_branch_B = np.array(branch_A[0], float), np.array(branch_B[0], float)
        
        # If 1st stroke isn't left then order
        if base_branch_A[0] > base_branch_B[0]:
            left_branch = branch_B
            right_branch = branch_A
        else:
            left_branch = branch_A
            right_branch = branch_B

        base_branch_A, base_branch_B = np.array(left_branch[0], float), np.array(right_branch[0], float)

        # If upside down
        if branch_shape_tip[1] < base_branch_A[1]:
            for branch in [left_branch, right_branch]:
                reversed_branch = branch[::-1]
                for i, point in enumerate(branch):
                    branch[i] = [point[0], reversed_branch[i][1]]

        return left_branch, right_branch


    def draw(self):
        if not self.is_widget_active:
            return

        for branch in self.branches:
            if len(branch) > 1:
                draw_stroke(branch, self._brush_color, self._brush_size)


    def clear(self):
        bpy.context.scene.branch_shape_canvas_settings.left_stroke.clear()
        bpy.context.scene.branch_shape_canvas_settings.right_stroke.clear()
        
        self.branches.clear()

        if self.context and self.context.area:
            self.context.area.tag_redraw()

    def rescale_point(self, x, y, src_size=(160, 65), tgt_size=(700, 700)):
        src_w, src_h = src_size
        tgt_w, tgt_h = tgt_size
        
        X = x / src_w * tgt_w
        Y = y / src_h * tgt_h
        return (X, Y)