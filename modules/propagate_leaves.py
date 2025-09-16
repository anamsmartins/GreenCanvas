import bpy
import random
from mathutils import Matrix
import bmesh
import math

from .popups import GC_OT_no_branch_selected_popup, GC_OT_selected_branch_needs_leaves_popup
from .utils.constraints.number_leaves_utils import compute_number_of_leaves

def find_edge_chain(obj):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()

    # Find endpoints (open branch will have two, spiral or straight)
    endpoints = [v for v in bm.verts if len(v.link_edges) == 1]
    if not endpoints:
        start = bm.verts[0]
    else:
        start = endpoints[0]

    chain = [start]
    visited = {start}
    current = start

    while True:
        nexts = [e.other_vert(current) for e in current.link_edges if e.other_vert(current) not in visited]
        if not nexts:
            break
        current = nexts[0]
        chain.append(current)
        visited.add(current)
    
    coords_chain = [v.co for v in chain]
    bm.free()
    
    return coords_chain

def point_at_offset(chain_world, offset):
    acc = 0
    for i in range(len(chain_world) - 1):
        segment = chain_world[i + 1] - chain_world[i]
        seg_len = segment.length
        if acc + seg_len > offset:
            local_offset = offset - acc
            ratio = local_offset / seg_len
            return chain_world[i] + segment * ratio
        acc += seg_len
    return chain_world[-1]

def positions_on_branch(branch_chain_world, branch_length, number_leaves, mode="random", start_offset=0):
    positions = []

    if mode == "even":
        # Compute offsets
        offsets_space = branch_length / (number_leaves - 1)
        positions_offsets = []
        current_pos_offset = start_offset
        while current_pos_offset <= branch_length + start_offset:
            positions_offsets.append(current_pos_offset)
            current_pos_offset += offsets_space
        
        for n in range(number_leaves - 1):
            # Get offset
            offset = positions_offsets[n]

            # Find which segment contains the target offset
            new_pos = point_at_offset(branch_chain_world, offset)
            positions.append(new_pos)

    elif mode == "random":
        min_offset = start_offset
        max_offset = branch_length + start_offset

        for _ in range(number_leaves):
            # Get random offset
            offset = random.uniform(min_offset, max_offset)

            # Find which segment contains the target offset
            new_pos = point_at_offset(branch_chain_world, offset)
            positions.append(new_pos)

    return positions

def get_branch_length(chain_world):
    total_length = sum((chain_world[i+1] - chain_world[i]).length for i in range(len(chain_world)-1))
    return total_length

def get_offset_along_branch(branch_chain_world, position, branch_length):

    # Find closest segment and t along chain
    min_dist = float('inf')
    closest_seg_idx = 0
    closest_t = 0.0
    for i in range(len(branch_chain_world)-1):
        a, b = branch_chain_world[i], branch_chain_world[i+1]
        ab = b - a
        ab_len2 = ab.length_squared
        if ab_len2 == 0:
            continue
        t = (position - a).dot(ab) / ab_len2
        t = max(0.0, min(1.0, t))
        proj = a.lerp(b, t)
        dist = (position - proj).length
        if dist < min_dist:
            min_dist = dist
            closest_seg_idx = i
            closest_t = t

    # Accumulate arc-length along the chain up to projected point
    total_length = 0.0
    for j in range(closest_seg_idx):
        total_length += (branch_chain_world[j+1] - branch_chain_world[j]).length
    a, b = branch_chain_world[closest_seg_idx], branch_chain_world[closest_seg_idx+1]
    total_length += (b - a).length * closest_t

    # Normalize to 0 — 1
    return (total_length / branch_length)

class GC_OT_propagate_leaves_operator(bpy.types.Operator):
    bl_idname = "mesh.gc_ot_propagate_leaves"
    bl_label = "Propagate leaves"
    bl_description = "Propagate leaves along the selected branch"

    def execute(self, context):
        branch_obj = bpy.context.active_object
        if branch_obj is None or branch_obj.type != 'MESH':
            bpy.context.window_manager.popup_menu(
                GC_OT_no_branch_selected_popup.draw,
                    title=GC_OT_no_branch_selected_popup.bl_label,
                    icon='INFO'
            )
            return {'CANCELLED'}

        # Get existing leaves on the branch
        leaves_objs = [c for c in branch_obj.children if "Leaf" in c.name]
        if not leaves_objs:
            bpy.context.window_manager.popup_menu(
                GC_OT_selected_branch_needs_leaves_popup.draw,
                    title=GC_OT_selected_branch_needs_leaves_popup.bl_label,
                    icon='INFO'
            )
            return {'CANCELLED'}

        # Compute number and positions of the new leaves
        realistic = bpy.context.scene.propagate_leaves_selector == "REAL"

        branch_chain = find_edge_chain(branch_obj)
        branch_chain_world = [branch_obj.matrix_world @ v for v in branch_chain]
        branch_length = get_branch_length(branch_chain_world)
        branch_start_offset = 0.2 * branch_length
        branch_end_offset = 0.05 * branch_length
        branch_length -= branch_start_offset - branch_end_offset
        
        if realistic:
            parent_obj = branch_obj.parent
            
            # If parent and collection
            if parent_obj.data is None:
                parent_length = branch_length
                branch_offset = 0
            else:
                parent_chain = find_edge_chain(branch_obj)
                parent_chain_world = [parent_obj.matrix_world @ v for v in parent_chain]
                parent_length = get_branch_length(parent_chain_world)

                branch_pos_world = branch_obj.matrix_world.translation
                branch_offset = get_offset_along_branch(parent_chain_world, branch_pos_world, parent_length)

            num_new_leaves = compute_number_of_leaves(branch_offset, parent_length)
            new_leaves_positions = positions_on_branch(branch_chain_world, branch_length, num_new_leaves, "even", start_offset=branch_start_offset)
        else:
            num_new_leaves = random.randint(8, 16)
            new_leaves_positions = positions_on_branch(branch_chain_world, branch_length, num_new_leaves, "random", start_offset=branch_start_offset)

        for idx, new_leaf_pos in enumerate(new_leaves_positions):
            # Random mesh from existing leaves on the branch
            leaf_obj = random.choice(leaves_objs)
            leaf_pos_world = leaf_obj.matrix_world.translation
            leaf_offset = get_offset_along_branch(branch_chain_world, leaf_pos_world, branch_length)
            leaf_scale_factor = leaf_offset

            # Copy mesh and data from selected leaf
            new_leaf = leaf_obj.copy()
            new_leaf.data = leaf_obj.data.copy()
            bpy.context.collection.objects.link(new_leaf)
            new_leaf.parent = branch_obj
            original_matrix = leaf_obj.matrix_world.copy()

            # Compute leaf scaling if realistic
            if realistic:
                new_leaf_offset = get_offset_along_branch(branch_chain_world, new_leaf_pos, branch_length)
                new_leaf_scale = 1 - min(new_leaf_offset, 1.0)
                new_leaf_scale = 0.2 + 0.6 * new_leaf_scale  # range 0.8 — 0.2
                scale_matrix = Matrix.Scale(new_leaf_scale + leaf_scale_factor, 4)
            else:
                scale_matrix = Matrix.Identity(4)

            # Place leaves on both sides
            if idx % 2 == 0:
                up_angle = 0  # no flip
            else:
                up_angle = math.pi # flip over
            flip_mat = Matrix.Rotation(up_angle, 4, 'Y')  # or 'X' as per your branch/leaf orientation

            # Add a little tilt to the leaves
            tilt_angle = math.radians(random.randint(-25, 25))
            tilt_mat = Matrix.Rotation(tilt_angle, 4, 'X')  # or 'X' as per your branch/leaf orientation

            # Compose transformation: flip, tilt and scale
            new_leaf.matrix_world = (
                Matrix.Translation(new_leaf_pos) 
                @ original_matrix.to_3x3().to_4x4()
                @ flip_mat 
                @ tilt_mat
                @ scale_matrix
            )
            
            new_leaf.matrix_world.translation = new_leaf_pos

        return {'FINISHED'}

classes = (
    GC_OT_propagate_leaves_operator,
)

def register():
    for cls in classes:
        if not hasattr(bpy.types, cls.__name__):
            bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        if hasattr(bpy.types, cls.__name__):
            bpy.utils.unregister_class(cls)
   
    
        