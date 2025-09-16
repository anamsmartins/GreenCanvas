import numpy as np
import mathutils
import random

from .stroke_utils import point_at_offset, compute_stroke_length
from .constraints.angle_utils import compute_limit_angle
from .constraints.length_utils import compute_offset_child, compute_branch_length

def format_branch_coords_to_blender(branches, scale_factor):
    y_min = min(pt.y for b in branches for pt in b.stroke)
    for branch in branches:
        for pt in branch.stroke:
            old_y = pt.y
            pt.x *= scale_factor
            pt.y = 0
            pt.z = old_y * scale_factor - y_min * scale_factor

            if pt.z < 0:
                print(f"Warning: Branch {branch.branch_id} point z < 0 after formatting: {pt.z}")
                
        format_branch_shape(branch, scale_factor)

        branch.id_data.update_tag()

    return y_min

def format_branch_shape(branch, scale_factor):
    branch_shape_left_stroke = branch.branch_shape_left_stroke
    branch_shape_right_stroke = branch.branch_shape_right_stroke

    if len(branch_shape_left_stroke) == 0:
        return

    for pt in branch_shape_left_stroke:
        pt.x *= scale_factor
        pt.y *= scale_factor

    
    for pt in branch_shape_right_stroke:
        pt.x *= scale_factor
        pt.y *= scale_factor

    branch.id_data.update_tag()
    

def get_branch_mesh_name(branch, parent, parent_prefix, branch_type_counter):
    branch_type = branch.branch_type.lower()

    # Count per (parent, type)
    key = (parent, branch_type)
    branch_type_counter[key] = branch_type_counter.get(key, 0) + 1
    num = branch_type_counter[key]

    if branch_type == "trunk":
        return "Trunk", ""

    if branch_type == "main" and parent.name == "Branches":
        name = f"Main {num}"
        prefix = f"M{num}"
        return name, prefix

    # Child branch
    name = f"{parent_prefix} Child {num}"
    prefix = f"{parent_prefix} C{num}"
    return name, prefix


def compute_children_by_parent_id(branches):
    # Prepopulate every branch index with an empty list
    children_map = {branch.parent_id: [] for branch in branches}

    # Fill in child indices
    for branch in branches:
        parent_id = branch.parent_id
        
        if parent_id < 0:
            continue
        
        # Append this branch index as a child of its parent
        children_map[parent_id].append(branch.branch_id)

    return children_map

def update_branch_stroke(branch, new_tip):
    stroke = branch.stroke
    base = np.array([stroke[0].x, stroke[0].y, stroke[0].z])
    old_tip = np.array([stroke[-1].x, stroke[-1].y, stroke[-1].z])
    new_tip = np.array(new_tip)

    old_vec = old_tip - base
    new_vec = new_tip - base

    # Scaling factor
    old_len = np.linalg.norm(old_vec)
    scale = np.linalg.norm(new_vec) / old_len if old_len > 1e-6 else 1.0

    # Rotation matrix (align old_vec → new_vec)
    if old_len > 1e-6 and np.linalg.norm(new_vec) > 1e-6:
        v1 = old_vec / old_len
        v2 = new_vec / np.linalg.norm(new_vec)
        axis = np.cross(v1, v2)
        angle = np.arccos(np.clip(np.dot(v1, v2), -1.0, 1.0))
        rot = mathutils.Matrix.Rotation(angle, 3, mathutils.Vector(axis)) if np.linalg.norm(axis) > 1e-6 else mathutils.Matrix.Identity(3)
    else:
        rot = mathutils.Matrix.Identity(3)

    # Apply transform to each point
    for p in stroke:
        v = np.array([p.x, p.y, p.z]) - base
        v = scale * np.array(rot @ mathutils.Vector(v))
        p.x, p.y, p.z = v + base

    branch.id_data.update_tag()

def update_child_branches_strokes(branches, parent, rescale_to_child_length=False):
    children_map = compute_children_by_parent_id(branches)

    child_ids = children_map.get(parent.branch_id, [])
    child_indexes = [i for i, branch in enumerate(branches) if branch.branch_id in child_ids]
        
    if not child_indexes:
        return

    for cidx in child_indexes:
        child = branches[cidx]
        offset = child.offset
        parent_pts = [(p.x, p.y, p.z) for p in parent.stroke]
        attach_point = np.array(point_at_offset(parent_pts, offset))

        # Child current base/tip and direction
        base = np.array([child.stroke[0].x, child.stroke[0].y, child.stroke[0].z])
        tip  = np.array([child.stroke[-1].x, child.stroke[-1].y, child.stroke[-1].z])
        old_dir = tip - base
        old_len = np.linalg.norm(old_dir)

        # Optional scaling to target length
        scale = 1.0
        if rescale_to_child_length and hasattr(child, "length") and old_len > 1e-9:
            scale = float(child.length) / old_len

        for p in child.stroke:
            v = np.array([p.x, p.y, p.z]) - base
            v = scale * v
            v = v + attach_point
            p.x, p.y, p.z = float(v[0]), float(v[1]), float(v[2])

        child.id_data.update_tag()
    
def compute_branches_length_angle_constraints(branches, trunk, realistic, variations):
    children_map = compute_children_by_parent_id(branches)
    removal_branches_ids = [] 

    if realistic:
        scale = compute_stroke_length(trunk.stroke)
        trunk_length = compute_branch_length(trunk, None, None, scale)
        trunk.length = trunk_length
        trunk.id_data.update_tag()
        
        for branch in branches:
            child_ids = children_map.get(branch.branch_id, [])
            child_indexes = [i for i, branch in enumerate(branches) if branch.branch_id in child_ids]
            if not child_indexes:
                continue

            limit_angle = compute_limit_angle(branch, child_indexes, branches)

            for cidx in child_indexes:
                child = branches[cidx]

                length, offset = compute_branch_length(child, branch, trunk_length, scale)
                
                if length < 0.05:
                    removal_branches_ids.append(cidx)
                else:
                    child.limit_angle = limit_angle
                    child.length = length
                    child.offset = offset
                    child.id_data.update_tag()

        # Remove non realistic branches (hierarchy level where negative length was computed)
        for i in sorted(removal_branches_ids, reverse=True):
            branches.remove(i)

        # Scale everyrhing to match new lengths
        for branch in branches:
            update_child_branches_strokes(branches, branch, rescale_to_child_length=True) 
    else:
        for branch in branches:
            branch.length = compute_stroke_length(branch.stroke)
            
            child_ids = children_map.get(branch.branch_id, [])
            child_indexes = [i for i, branch in enumerate(branches) if branch.branch_id in child_ids]

            if not child_indexes:
                continue
            
            for cidx in child_indexes:
                child = branches[cidx]

                branch_offset_variation = random.uniform(- 0.2, 0) if variations else 0
                offset = compute_offset_child([(p.x, p.y, p.z) for p in branch.stroke], [(p.x, p.y, p.z) for p in child.stroke][0])
                offset_var = offset + branch_offset_variation

                child.offset = offset_var if offset_var <= branch.length and offset_var > 0 else offset
                child.id_data.update_tag()
