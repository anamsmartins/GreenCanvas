import numpy as np
import random

from .shape_ratio_utils import shape_ratio

def compute_offset_child(parent_stroke, child_start):
    offset = 0.0
    for i in range(len(parent_stroke) - 1):
        p1 = np.array(parent_stroke[i])
        p2 = np.array(parent_stroke[i+1])
        seg_len = np.linalg.norm(p2 - p1)

        v = p2 - p1
        w = np.array(child_start) - p1
        t = np.dot(w, v) / np.dot(v, v)  # parametric position along segment

        if 0 <= t <= 1:
            offset += t * seg_len
            break
        else:
            offset += seg_len

    return offset

def length_child_max(branch_level):
    length_map = {
        0: (1.0, 0.0),
        1: (0.4, 0.05),
        2: (1.0, 0.05),
    }
    n_length, n_length_v = length_map.get(branch_level, (0.2, 0.0))
    
    return random.uniform((n_length - n_length_v), (n_length + n_length_v))

def length_base(scale):
    return 0.3 * scale

def compute_branch_length(child, parent, trunk_length, scale):
    len_child_max = length_child_max(child.level)

    if parent is None:
        return len_child_max * scale

    child_offset = compute_offset_child([(p.x, p.y, p.z) for p in parent.stroke], [(p.x, p.y, p.z) for p in child.stroke][0])

    if child.branch_type == "MAIN":
        len_base = length_base(scale)
        ratio = (trunk_length - child_offset) / (trunk_length - len_base)
        child_length = trunk_length * len_child_max * shape_ratio(ratio)
    else:
        child_length = len_child_max * (parent.length - (0.6 * child_offset))
        child_length *= 1.2

    return child_length, child_offset