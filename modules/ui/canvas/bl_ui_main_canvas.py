
from ..bl_ui_widget import *
from ...utils.stroke_utils import stroke_horizontal_center
from ...utils.drawing_utils import attach_stroke_to_nearest_point, stretch_stroke_to_tips, draw_stroke
from ...popups import GC_OT_incomplete_branch_shape_popup, GC_OT_no_leaf_curvature_type_popup, GC_OT_no_branches_popup, GC_OT_existing_leaves_popup

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
            if not self._is_visible:
                return
            
            active_tool = bpy.context.scene.panel_settings.active_tool
            bshape_canvas_settings = bpy.context.scene.branch_shape_canvas_settings

            if active_tool == 'BRANCH' and (len(bshape_canvas_settings.left_stroke) > 0 and len(bshape_canvas_settings.right_stroke) == 0):
                bpy.context.window_manager.popup_menu(
                    GC_OT_incomplete_branch_shape_popup.draw,
                    title=GC_OT_incomplete_branch_shape_popup.bl_label,
                    icon='INFO'
                )
                return False

            if active_tool == 'LEAF':
                if len(bpy.context.scene.leaf_curvature_type_canvas_settings.stroke) == 0:
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
            if not self._is_visible:
                return
            
            self.current_stroke.append((x, y))

    def mouse_up(self, x, y):
        if not self._is_visible:
            return
        
        if len(self.current_stroke) >= 4:
            active_tool = bpy.context.scene.panel_settings.active_tool

            if active_tool == 'BRANCH':   
                if len(self.branches)  > 0:
                    widget_x = self.x_offset + self.x_screen
                    widget_y = self.get_area_height() - self.y_screen    
                    self.current_stroke, parent_idx, _  = attach_stroke_to_nearest_point(self.current_stroke, [branch["stroke"] for branch in self.branches], limit = {"xmin": widget_x, "xmax": widget_x + self.width, "ymin": widget_y - self.height, "ymax": widget_y})
                    branch_type = "MAIN" if parent_idx == 0 else "CHILD"
                    parent = self.branches[parent_idx]
                    level = parent["level"] + 1
                    parent_id = parent["branch_id"]
                    branch_id = self.branches[-1]["branch_id"] + 1
                else:
                    branch_type = "TRUNK"
                    parent_idx = -1
                    parent_id = -1
                    branch_id = 0
                    level = 0 
                    if self.current_stroke[-1][1] < self.current_stroke[0][1]:
                        self.current_stroke.reverse()

                new_branch = {
                    "stroke": self.current_stroke, 
                    "brush_size": bpy.context.scene.branch_slider_settings.brush_size, 
                    "branch_shape_left": [
                        (p.x, p.y)
                        for p in bpy.context.scene.branch_shape_canvas_settings.left_stroke
                    ],
                    "branch_shape_right": [
                        (p.x, p.y)
                        for p in bpy.context.scene.branch_shape_canvas_settings.right_stroke
                    ],
                    "branch_type": branch_type,
                    "parent_id": parent_id,
                    "branch_id": branch_id,
                    "level": level,
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
                    branch_id = -1
                    if len(self.branches) > 0:
                        widget_x = self.x_offset + self.x_screen
                        widget_y = self.get_area_height() - self.y_screen   
                        center_attached, branch_idx, nearest_point = attach_stroke_to_nearest_point(center, [branch["stroke"] for branch in self.branches], limit = {"xmin": widget_x, "xmax": widget_x + self.width, "ymin": widget_y - self.height, "ymax": widget_y})

                        dx = center_attached[0][0] - center[0][0]
                        dy = center_attached[0][1] - center[0][1]
                        left  = [(x + dx, y + dy) for x, y in left]
                        right = [(x + dx, y + dy) for x, y in right]
                        center = center_attached
                        branch_id = self.branches[branch_idx]["branch_id"]

                    new_leaf = {
                        "outline1": left,
                        "outline2": right,
                        "inner": center,
                        "curvature_type": [(p.x, p.y) for p in bpy.context.scene.leaf_curvature_type_canvas_settings.stroke],
                        "branch_id": branch_id,
                    }
                    self.leaves.append(new_leaf)
                    self.add_leaf_to_scene(new_leaf)
                    
        self.is_drawing = False
        self.current_stroke = []

    def draw(self):
        if not self._is_visible:
            return 
        
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
            last_branch = self.branches[-1]

            # Check if there are leaves attached to this branch
            attached_leaves = [leaf for leaf in self.leaves if leaf["branch_id"] == last_branch["branch_id"]]
            if attached_leaves:
                return

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
            if len(self.leaves) > 0:
                bpy.context.window_manager.popup_menu(
                        GC_OT_existing_leaves_popup.draw,
                        title=GC_OT_existing_leaves_popup.bl_label,
                        icon='INFO'
                    )
                return
            
            self.branches.clear()
            bpy.context.scene.branch_collection.branches.clear()
            self.undo_branches_stack.clear()
        
        elif active_tool == "LEAF" and (self.leaves or self.current_leaf):
            self.leaves.clear()
            bpy.context.scene.leaf_collection.leaves.clear()
            self.undo_leaves_stack.clear()

            self.current_leaf.clear()
            self.current_leaf_tips.clear()
            self.undo_current_leaf_stack.clear()
        
        self.context.area.tag_redraw()

    def add_gp_points_to_stroke(self, gp_stroke, stroke):
        for x, y in stroke:
            point = gp_stroke.add()
            point.x = x - (self.x_screen + (self.width/2)) + self.x
            point.y = y - self.y_screen + self.y

    def add_branch_to_scene(self, branch):
        scene_branch = bpy.context.scene.branch_collection.branches.add()

        # stroke
        self.add_gp_points_to_stroke(scene_branch.stroke, branch["stroke"])

        # start and end positions
        start_x, start_y = branch["stroke"][0]
        end_x, end_y   = branch["stroke"][-1]
        scene_branch.start_position.point = (start_x - (self.x_screen + (self.width/2)) + self.x, start_y - self.y_screen + self.y)
        scene_branch.end_position.point   = (end_x - (self.x_screen + (self.width/2)) + self.x, end_y - self.y_screen + self.y)

        scene_branch.brush_size = branch["brush_size"]
        scene_branch.branch_type = branch["branch_type"]
        scene_branch.branch_id = branch["branch_id"]
        scene_branch.parent_id = branch["parent_id"]
        scene_branch.level = branch["level"]

        # If optional branch shape exists
        if len(branch["branch_shape_left"]) > 0:
            for point in branch["branch_shape_left"]:
                p = scene_branch.branch_shape_left_stroke.add()
                p.x = point[0]
                p.y = point[1]

            for point in branch["branch_shape_right"]:
                p = scene_branch.branch_shape_right_stroke.add()
                p.x = point[0]
                p.y = point[1]

    def remove_branch_from_scene(self):
        branches = bpy.context.scene.branch_collection.branches
        if len(branches) > 0:
            branches.remove(len(branches) - 1)
            
    def add_leaf_to_scene(self, leaf):
        scene_leaf = bpy.context.scene.leaf_collection.leaves.add()

        self.add_gp_points_to_stroke(scene_leaf.outline1, leaf["outline1"])
        self.add_gp_points_to_stroke(scene_leaf.outline2, leaf["outline2"])
        self.add_gp_points_to_stroke(scene_leaf.inner, leaf["inner"])


        for x, y in leaf["curvature_type"]:
            point = scene_leaf.curvature_type.add()
            point.x = x
            point.y = y

        scene_leaf.branch_id = leaf["branch_id"]

    def remove_leaf_from_scene(self):
        leaves = bpy.context.scene.leaf_collection.leaves
        if len(leaves) > 0:
            leaves.remove(len(leaves) - 1)
            