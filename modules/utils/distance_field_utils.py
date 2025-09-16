import numpy as np
from scipy.ndimage import distance_transform_edt

from .constraints.angle_utils import angle_between

def world_to_grid(x, y, x_range, y_range, grid_size=128):
    x_span = x_range[1] - x_range[0]
    y_span = y_range[1] - y_range[0]
    gx = int(((x - x_range[0]) / x_span) * (grid_size - 1))
    gy = int(((y - y_range[0]) / y_span) * (grid_size - 1))
    return gx, gy

def compute_new_2d_distance_field_pos(branch, parent, hull_3d, x_range, y_range, occupancy, realistic=False, grid_size=128):
    bx, by, bz = branch.stroke[0].x, branch.stroke[0].y, branch.stroke[0].z
    tx, ty, tz = branch.stroke[-1].x, branch.stroke[-1].y, branch.stroke[-1].z
    branch_base = np.array([bx, by, bz])
    old_tip_vec = np.array([tx, ty, tz])
    old_length = np.linalg.norm(branch_base - old_tip_vec)

    # Compute distance field
    dist_field = distance_transform_edt(occupancy == 0)

    # Create grid of world coordinates
    gx = np.arange(grid_size)
    gy = np.arange(grid_size)
    gx_grid, gy_grid = np.meshgrid(gx, gy)

    wx_grid = (gx_grid / (grid_size - 1)) * (x_range[1] - x_range[0]) + x_range[0]
    wy_grid = (gy_grid / (grid_size - 1)) * (y_range[1] - y_range[0]) + y_range[0]
    wz_grid = np.full_like(wx_grid, tz)

    # Stack into candidate points
    candidates = np.stack([wx_grid.ravel(), wy_grid.ravel(), wz_grid.ravel()], axis=-1)

    # Mask 1: inside hull
    norms = np.linalg.norm(hull_3d.equations[:, :-1], axis=1, keepdims=True)
    eq_normed = hull_3d.equations[:, :-1] / norms
    d_normed = hull_3d.equations[:, -1] / norms.squeeze()
    mask_hull = np.all(candidates @ eq_normed.T + d_normed <= 1e-1, axis=1)

    # Mask 2: length constraint
    new_lengths = np.linalg.norm(candidates - branch_base, axis=1)
    mask_length = new_lengths <= old_length

    # Combine masks
    mask = mask_hull & mask_length

    # Mask 3: angle constraint (optional)
    if realistic and parent is not None:
        parent_base = np.array([parent.stroke[0].x, parent.stroke[0].y, parent.stroke[0].z])
        parent_tip = np.array([parent.stroke[-1].x, parent.stroke[-1].y, parent.stroke[-1].z])
        parent_vec = [parent_base, parent_tip]
        # Compute angles for all candidates
        candidate_vecs = np.stack([np.tile(branch_base, (candidates.shape[0], 1)), candidates], axis=1)
        angles = np.array([angle_between(cv, parent_vec) for cv in candidate_vecs])
        mask &= angles <= branch.limit_angle

    # Apply mask to distance field
    masked_dist = np.full(candidates.shape[0], -np.inf)
    masked_dist[mask] = dist_field.ravel()[mask]

    # If no valid candidates, fallback to old tip
    if np.all(masked_dist == -np.inf):
        gx_fallback, gy_fallback = world_to_grid(tx, ty, x_range, y_range, grid_size)
        occupancy[gy_fallback, gx_fallback] = 1
        return tx, ty, tz

    # Pick best candidate
    best_idx = np.argmax(masked_dist)
    best_point = candidates[best_idx]
    gx_best, gy_best = gx_grid.ravel()[best_idx], gy_grid.ravel()[best_idx]

    # Update occupancy
    occupancy[int(gy_best), int(gx_best)] = 1

    return tuple(best_point)