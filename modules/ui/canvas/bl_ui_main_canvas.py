
from ..bl_ui_widget import *
from ...utils.curves_utils import stroke_horizontal_center
from ...utils.drawing_utils import attach_stroke_to_nearest_point, stretch_stroke_to_tips, draw_stroke
from ...sp_branch_shape_canvas_op import GC_OT_incomplete_branch_shape_popup
from ...sp_leaf_curvature_type_canvas_op import GC_OT_no_leaf_curvature_type_popup, GC_OT_no_branches_popup


class BL_UI_Main_Canvas(BL_UI_Widget):
    
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)

        self._brush_color = (0.2, 0.2, 0.2, 1.0)
        self.leaf_brush_size = 2

        self.is_drawing = False
        self.current_stroke = []

        self.branches = []
        self.leaves = []
        self.current_leaf = [] # store the 3 strokes of the leaf (outline1, outline2, inner)
        self.current_leaf_tips = []

        self.undo_branches_stack = []
        self.undo_leaves_stack = []
        self.undo_current_leaf_stack = []

    @property
    def brush_color(self):
        return self._brush_color

    @brush_color.setter
    def brush_color(self, value):
        self._brush_color = value

    def updateStrokes(self, offset_x, offset_y):
        self.branches = [
            {
                **branch,
                "stroke": [(x + offset_x, y - offset_y) for (x, y) in branch["stroke"]]
            }
            for branch in self.branches
        ]

        self.leaves = [
            {
                **leaf,
                "outline1": [(x + offset_x, y - offset_y) for (x, y) in leaf["outline1"]],
                "outline2": [(x + offset_x, y - offset_y) for (x, y) in leaf["outline2"]],
                "inner": [(x + offset_x, y - offset_y) for (x, y) in leaf["inner"]],
            }
            for leaf in self.leaves
        ]

        
        self.current_leaf = [
            [(x + offset_x, y - offset_y) for (x, y) in stroke]
            for stroke in self.current_leaf
        ]

        self.current_leaf_tips = [(x + offset_x, y - offset_y) for (x, y) in self.current_leaf_tips]

    def update(self, x, y):
        self.updateStrokes(x - self.x_screen, y - self.y_screen)
        super().update(x, y)

    def mouse_down(self, x, y):
        if self.is_in_rect(x,y):
            active_tool = bpy.context.scene.panel_settings.active_tool

            if active_tool == 'BRANCH' and len(bpy.context.scene.branch_shape_canvas_settings.strokes) == 1:
                bpy.context.window_manager.popup_menu(
                    GC_OT_incomplete_branch_shape_popup.draw,
                    title=GC_OT_incomplete_branch_shape_popup.bl_label,
                    icon='INFO'
                )
                return False

            elif active_tool == 'LEAF':
                if len(bpy.context.scene.leaf_curvature_type_canvas_settings.stroke.points) == 0:
                    bpy.context.window_manager.popup_menu(
                        GC_OT_no_leaf_curvature_type_popup.draw,
                        title=GC_OT_no_leaf_curvature_type_popup.bl_label,
                        icon='INFO'
                    )
                    return False
                
                if len(bpy.context.scene.branch_collection.branches) == 0:
                    bpy.context.window_manager.popup_menu(
                        GC_OT_no_branches_popup.draw,
                        title=GC_OT_no_branches_popup.bl_label,
                        icon='INFO'
                    )
                    return False

            
            self.current_stroke = [(x, y)]
            self.is_drawing = True
           
            return True
        
        return False

    def mouse_move(self, x, y):
        if self.is_drawing and self.is_in_rect(x,y):
            self.current_stroke.append((x, y))

    def mouse_up(self, x, y):
        if len(self.current_stroke) >= 4:
            active_tool = bpy.context.scene.panel_settings.active_tool

            if active_tool == 'BRANCH':     
                if len(self.branches)  > 0:
                    widget_x = self.x_offset + self.x_screen
                    widget_y = self.get_area_height() - self.y_screen    
                    self.current_stroke = attach_stroke_to_nearest_point(self.current_stroke, [branch["stroke"] for branch in self.branches], limit = {"xmin": widget_x, "xmax": widget_x + self.width, "ymin": widget_y - self.height, "ymax": widget_y})

                new_branch = {
                    "stroke": self.current_stroke, 
                    "brush_size": bpy.context.scene.branch_slider_settings.brush_size, 
                    "branch_shape": [
                        [(pt.point[0] - bpy.context.scene.branch_shape_canvas_settings.x_norm_factor, pt.point[1] - bpy.context.scene.branch_shape_canvas_settings.y_norm_factor) for pt in stroke.points]
                        for stroke in bpy.context.scene.branch_shape_canvas_settings.strokes
                    ]
                }
                self.branches.append(new_branch)
                self.add_branch_to_scene(new_branch)

                self.undo_branches_stack = []

            elif active_tool == 'LEAF':
                current_leaf_len = len(self.current_leaf)
                if current_leaf_len == 0: # start position
                    self.current_leaf_tips = [self.current_stroke[0], self.current_stroke[-1]]

                if current_leaf_len == 3: # recent leaf added
                    self.undo_current_leaf_stack = []
                    self.undo_leaves_stack = []
                    self.current_leaf = []
                    self.current_leaf_tips = []

                    self.current_leaf_tips = [self.current_stroke[0], self.current_stroke[-1]]
                
                if current_leaf_len > 0:
                    self.current_stroke = stretch_stroke_to_tips(self.current_stroke, self.current_leaf_tips[0], self.current_leaf_tips[1])

                self.current_leaf.append(self.current_stroke)

                if len(self.current_leaf) == 3:
                    left, center, right = sorted(self.current_leaf, key=stroke_horizontal_center)
                    if len(self.branches) > 0:
                        widget_x = self.x_offset + self.x_screen
                        widget_y = self.get_area_height() - self.y_screen   
                        center_attached = attach_stroke_to_nearest_point(center, [branch["stroke"] for branch in self.branches], limit = {"xmin": widget_x, "xmax": widget_x + self.width, "ymin": widget_y - self.height, "ymax": widget_y})

                        dx = center_attached[0][0] - center[0][0]
                        dy = center_attached[0][1] - center[0][1]
                        left  = [(x + dx, y + dy) for x, y in left]
                        right = [(x + dx, y + dy) for x, y in right]
                        center = center_attached

                    new_leaf = {
                        "outline1": left,
                        "outline2": right,
                        "inner": center,
                        "curvature_type": [(pt.point[0] - bpy.context.scene.leaf_curvature_type_canvas_settings.x_norm_factor, pt.point[1] - bpy.context.scene.leaf_curvature_type_canvas_settings.y_norm_factor) for pt in bpy.context.scene.leaf_curvature_type_canvas_settings.stroke.points]
                    }
                    self.leaves.append(new_leaf)
                    self.add_leaf_to_scene(new_leaf)
                    
        self.is_drawing = False
        self.current_stroke = []

    def draw(self):
        # Draw all finished branch strokes
        for branch in self.branches:
            draw_stroke(branch["stroke"], self._brush_color, branch["brush_size"])

        # Draw all finished leaf strokes
        for leaf in self.leaves:
            draw_stroke(leaf["outline1"], self._brush_color, self.leaf_brush_size)
            draw_stroke(leaf["outline2"], self._brush_color, self.leaf_brush_size)
            draw_stroke(leaf["inner"], self._brush_color, self.leaf_brush_size)

        if len(self.current_leaf) < 3:
            for stroke in self.current_leaf:
                draw_stroke(stroke, self._brush_color, self.leaf_brush_size)

        # Draw current in-progress stroke
        if len(self.current_stroke) > 1:
            brush_size = bpy.context.scene.branch_slider_settings.brush_size if bpy.context.scene.panel_settings.active_tool == 'BRANCH' else self.leaf_brush_size
            draw_stroke(self.current_stroke, self._brush_color, brush_size)

    def undo(self):
        active_tool = bpy.context.scene.panel_settings.active_tool

        if active_tool == "BRANCH" and self.branches:
            last_branch = self.branches.pop()
            self.remove_branch_from_scene()

            self.undo_branches_stack.append(last_branch)

        elif active_tool == "LEAF" and (self.leaves or self.current_leaf):
            current_leaf_len = len(self.current_leaf) 
            if current_leaf_len > 0:
                if current_leaf_len == 3:
                    last_leaf = self.leaves.pop()
                    self.remove_leaf_from_scene()
                    self.undo_leaves_stack.append(last_leaf)

                last_leaf = self.current_leaf.pop()
                self.undo_current_leaf_stack.append(last_leaf)

        self.context.area.tag_redraw()

    def redo(self):
        active_tool = bpy.context.scene.panel_settings.active_tool

        if active_tool == "BRANCH" and self.undo_branches_stack:
            branch = self.undo_branches_stack.pop()
            self.branches.append(branch)
            self.add_branch_to_scene(branch)
        
        elif active_tool == "LEAF" and self.undo_leaves_stack:
            if len(self.undo_leaves_stack) > 0:
                leaf = self.undo_leaves_stack.pop()
                self.leaves.append(leaf)
                self.add_leaf_to_scene(leaf)

            if len(self.undo_current_leaf_stack) > 0:
                leaf = self.undo_current_leaf_stack.pop()
                self.current_leaf.append(leaf)

        self.context.area.tag_redraw()

    def clear(self):
        active_tool = bpy.context.scene.panel_settings.active_tool

        if active_tool == "BRANCH" and self.branches:
            self.branches.clear()
            bpy.context.scene.branch_collection.branches.clear()
            self.undo_branches_stack.clear()
        
        elif active_tool == "LEAF" and (self.leaves or self.current_leaf):
            self.leaves.clear()
            self.undo_leaves_stack.clear()

            self.current_leaf.clear()
            self.current_leaf_tips.clear()
            self.undo_current_leaf_stack.clear()
        
        self.context.area.tag_redraw()

    def add_gp_points_to_stroke(self, gp_stroke, stroke):
        for x, y in stroke:
            pt = gp_stroke.add()
            pt.point = (x - self.x_screen + self.x, y - self.y_screen + self.y)

    def add_branch_to_scene(self, branch):
        scene_branch = bpy.context.scene.branch_collection.branches.add()

        # stroke
        self.add_gp_points_to_stroke(scene_branch.stroke, branch["stroke"])

        # start and end positions
        start_x, start_y = branch["stroke"][0]
        end_x, end_y   = branch["stroke"][-1]
        scene_branch.start_position.point = (start_x - self.x_screen + self.x, start_y - self.y_screen + self.y)
        scene_branch.end_position.point   = (end_x - self.x_screen + self.x, end_y - self.y_screen + self.y)

        # brush size
        scene_branch.brush_size = branch["brush_size"]

        # If optional branch shape exists
        if len(branch["branch_shape"]) > 0:
            for bs_stroke in branch["branch_shape"]:
                bs = scene_branch.branch_shape.add()
                for point in bs_stroke:
                    pt = bs.points.add()
                    pt.point = point

    def remove_branch_from_scene(self):
        branches = bpy.context.scene.branch_collection.branches
        if len(branches) > 0:
            branches.remove(len(branches) - 1)
            
    def add_leaf_to_scene(self, leaf):
        scene_leaf = bpy.context.scene.leaf_collection.leaves.add()

        self.add_gp_points_to_stroke(scene_leaf.outline1, leaf["outline1"])
        self.add_gp_points_to_stroke(scene_leaf.outline2, leaf["outline2"])
        self.add_gp_points_to_stroke(scene_leaf.inner, leaf["inner"])
        self.add_gp_points_to_stroke(scene_leaf.curvature_type, leaf["curvature_type"])

    def remove_leaf_from_scene(self):
        leaves = bpy.context.scene.leaf_collection.leaves
        if len(leaves) > 0:
            leaves.remove(len(leaves) - 1)