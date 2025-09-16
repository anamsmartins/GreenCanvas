import numpy as np

def compute_limit_angle(parent, child_indexes, branches):
    angles = []
    for cidx in child_indexes:
        child = branches[cidx]

        child_base = (child.stroke[0].x, child.stroke[0].y, child.stroke[0].z)
        child_tip = (child.stroke[-1].x, child.stroke[-1].y, child.stroke[-1].z)
        parent_base = (parent.stroke[0].x, parent.stroke[0].y, parent.stroke[0].z)
        parent_tip = (parent.stroke[-1].x, parent.stroke[-1].y, parent.stroke[-1].z)

        angles.append(angle_between([child_base, child_tip], [parent_base, parent_tip]))
    return max(angles) * 1.2

def angle_between(child, parent):
    child_base = child[0]
    child_tip = child[-1]

    parent_base = parent[0]
    parent_tip = parent[-1]

    child_dir_vec = np.array([child_tip[0] - child_base[0], child_tip[1] - child_base[1], child_tip[2] - child_base[2]])
    parent_dir_vec = np.array([parent_tip[0] - parent_base[0], parent_tip[1] - parent_base[1], parent_tip[2] - parent_base[2]])

    if np.linalg.norm(child_dir_vec) == 0 or np.linalg.norm(parent_dir_vec) == 0:
        return None
   
    cos_theta = np.dot(child_dir_vec, parent_dir_vec) / (np.linalg.norm(child_dir_vec) * np.linalg.norm(parent_dir_vec))
    angle_rad = np.arccos(np.clip(cos_theta, -1.0, 1.0))
    angle_deg = np.degrees(angle_rad)

    return angle_deg
