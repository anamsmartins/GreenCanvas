import bpy
import numpy as np
import random

from .utils.convex_hull_utils import convex_hull_2d, convex_hull_3d
from .utils.distance_field_utils import compute_new_2d_distance_field_pos, world_to_grid
from .utils.geometry_utils import build_plant_mesh
from .utils.branches_utils import (
    format_branch_coords_to_blender,
    compute_branches_length_angle_constraints,
    update_branch_stroke,
    update_child_branches_strokes,
)
from .utils.leaves_utils import (
    update_leaves_of_branch,
    format_leaf_coords_to_blender,
    compute_leaves_offset,
)

from .dp_main_canvas_op import unregister as dp_main_canvas_op_unregister
from .sp_branch_slider_op import unregister as sp_branch_slider_op_unregister
from .sp_branch_shape_canvas_op import unregister as sp_branch_shape_canvas_op_unregister
from .sp_leaf_curvature_type_canvas_op import unregister as sp_leaf_curvature_type_canvas_op_unregister


class GC_OT_build_plant(bpy.types.Operator):
    bl_idname = "mesh.gc_ot_build_plant"
    bl_label = "Build 3D Plant Model"
    bl_description = "Build the 3D Plant Model from the Sketch"
    bl_options = {'REGISTER'}

    is_variation: bpy.props.BoolProperty(name="Is Plant Variation", default=False)

    def execute(self, context):
        bpy.ops.view3d.dp_ot_building_plant_operator("INVOKE_DEFAULT")

        bpy.app.timers.register(lambda: self.build_plant(context), first_interval=0.1)

        return {"FINISHED"}

    def build_plant(self, context):

        branches = context.scene.branch_collection.branches
        leaves = context.scene.leaf_collection.leaves
        realistic = context.scene.model_type_selector == "REAL"
        scale_factor = 0.012
        grid_size = 128
        variations = self.is_variation

        if variations:
            scale_factor = random.uniform(0.017, 0.09)
        else:
            context.scene.built_plant = True
            y_min = format_branch_coords_to_blender(branches, scale_factor)
            if len(leaves) > 0:
                format_leaf_coords_to_blender(leaves, scale_factor, y_min)

        # Compute constraints
        trunk_branch = next((b for b in branches if b.branch_type == "TRUNK"), None)
        compute_branches_length_angle_constraints(branches, trunk_branch, realistic, variations)
        rescale_to_child_length = realistic and not variations
        compute_leaves_offset(leaves, branches, variations, rescale_to_child_length)

        # Convex hull
        xy_branches = [(pt.x, pt.z) for branch in branches for pt in branch.stroke]
        hull_poly = convex_hull_2d(xy_branches)
        points_3d, hull_3d = convex_hull_3d(xy_branches, hull_poly)
        x_range = (min(pt[0] for pt in points_3d), max(pt[0] for pt in points_3d))
        y_range = (min(pt[1] for pt in points_3d), max(pt[1] for pt in points_3d))

        # Occupancy grid
        occupancy = np.zeros((grid_size, grid_size), dtype=np.uint8)
        x_random, y_random = self.sample_near_center(x_range, y_range)
        new_tip = (x_random, y_random, trunk_branch.stroke[-1].z)
        update_branch_stroke(trunk_branch, new_tip)
        update_child_branches_strokes(branches, trunk_branch)
        update_leaves_of_branch(leaves, trunk_branch)
        gx, gy = world_to_grid(x_random, y_random, x_range, y_range, grid_size=grid_size)
        occupancy[gy, gx] = 1

        # Distance field
        for branch in branches:
            if branch.branch_type == "TRUNK":
                continue
            parent = next((b for b in branches if b.branch_id == branch.parent_id), None)
            new_tip = compute_new_2d_distance_field_pos(
                branch, parent, hull_3d, x_range, y_range, occupancy, realistic, grid_size=grid_size
            )
            update_branch_stroke(branch, new_tip)
            update_child_branches_strokes(branches, branch)
            update_leaves_of_branch(leaves, branch)

        # Build plant mesh
        build_plant_mesh(branches)

        if not variations:
            bpy.context.scene.main_canvas_visible = False

        # Hide building plant panel
        for op in getattr(bpy.context.scene, "draw_operators", []):
            try:
                if op.bl_idname == "VIEW3D_OT_dp_ot_building_plant_operator":
                    op._finished = True
            except ReferenceError:
                pass

        return None

    def sample_near_center(self, x_range, y_range, fraction=0.05):
        x_center = (x_range[0] + x_range[1]) / 2
        y_center = (y_range[0] + y_range[1]) / 2
        x_half_width = (x_range[1] - x_range[0]) * fraction / 2
        y_half_height = (y_range[1] - y_range[0]) * fraction / 2
        x_random = np.random.uniform(x_center - x_half_width, x_center + x_half_width)
        y_random = np.random.uniform(y_center - y_half_height, y_center + y_half_height)
        return x_random, y_random

def get_view3d_context():
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == "VIEW_3D":
                for region in area.regions:
                    if region.type == 'WINDOW':
                        override = {
                            "window": window,
                            "screen": window.screen,
                            "area": area,
                            "region": region,
                            "scene": bpy.context.scene,
                        }
                        return override
    return None

classes = (GC_OT_build_plant,)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
