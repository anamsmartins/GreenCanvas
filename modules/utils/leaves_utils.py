import numpy as np
import random

from .stroke_utils import point_at_offset
from .constraints.length_utils import compute_offset_child

def format_leaf_coords_to_blender(leaves, scale_factor, y_min):
    for leaf in leaves:
        for stroke in [leaf.inner, leaf.outline1, leaf.outline2]:
            for pt in stroke:
                old_y = pt.y
                pt.x *= scale_factor
                pt.y = 0
                pt.z = old_y * scale_factor - y_min * scale_factor
        
        leaf.id_data.update_tag()

def compute_leaves_offset(leaves, branches, variations, rescale_to_child_length):
    for leaf in leaves:
        if leaf.branch_id < 0:
            continue 
        branch = next((b for b in branches if b.branch_id == leaf.branch_id), None)
        if branch is None:
            continue
        
        # Compute initial offset along branch stroke
        leaf_offset_variation = random.uniform(- 0.2, 0.2) if variations else 0
        offset = compute_offset_child([(p.x, p.y, p.z) for p in branch.stroke], (leaf.inner[0].x, leaf.inner[0].y, leaf.inner[0].z))
        offset_var = offset + leaf_offset_variation
        leaf.branch_offset = offset_var / branch.length if branch.length > 0 else 0.0
        leaf.id_data.update_tag()

        update_leaf(leaf, branch, rescale_to_child_length=rescale_to_child_length)


def update_leaf(leaf, branch, rescale_to_child_length=False):
    min_scale = 0.1
    max_scale = 1
        
    # Find the new attachment point on the (possibly rescaled) branch by offset
    parent_pts = [(p.x, p.y, p.z) for p in branch.stroke]
    attach_point = np.array(point_at_offset(parent_pts, (leaf.branch_offset * branch.length) - 0.2))

    base = np.array([leaf.inner[0].x, leaf.inner[0].y, leaf.inner[0].z])
    
    scale = 1
    if rescale_to_child_length:
        t =  1 - max(0.0, min(1.0, leaf.branch_offset))
        scale = min_scale + t / (max_scale - min_scale)


    # Move leaf geometry collections
    for stroke in [leaf.inner, leaf.outline1, leaf.outline2]:
        for p in stroke:
            v = np.array([p.x, p.y, p.z]) - base
            v = scale * v
            v = v + attach_point
            p.x, p.y, p.z = float(v[0]), float(v[1]), float(v[2])
    
    leaf.id_data.update_tag()

def update_leaves_of_branch(leaves, branch, rescale_to_child_length=False):    
    for leaf in leaves:
        if branch is None or leaf.branch_id != branch.branch_id:
            continue 
          
        update_leaf(leaf, branch, rescale_to_child_length=rescale_to_child_length)