import math
import numpy as np

from mathutils import Vector

def catmull_rom_spline(P0, P1, P2, P3, nPoints=20):
    """Generates points between P1 and P2 using Catmull–Rom Spline (NumPy optimized)."""
    alpha = 0.5
    P0, P1, P2, P3 = map(np.array, (P0, P1, P2, P3))

    def tj(ti, Pi, Pj):
        return ((np.linalg.norm(Pj - Pi))**alpha) + ti

    t0 = 0.0
    t1 = tj(t0, P0, P1)
    t2 = tj(t1, P1, P2)
    t3 = tj(t2, P2, P3)

    eps = 1e-6
    if abs(t1 - t0) < eps or abs(t2 - t1) < eps or abs(t3 - t2) < eps:
        # Return a straight line
        return [tuple(P1), tuple(P2)]

    # Parameter values
    t = np.linspace(t1, t2, nPoints)

    # Compute A1, A2, A3
    A1 = (t1 - t)[:, None]/(t1 - t0)*P0 + (t - t0)[:, None]/(t1 - t0)*P1
    A2 = (t2 - t)[:, None]/(t2 - t1)*P1 + (t - t1)[:, None]/(t2 - t1)*P2
    A3 = (t3 - t)[:, None]/(t3 - t2)*P2 + (t - t2)[:, None]/(t3 - t2)*P3

    # Compute B1, B2
    B1 = (t2 - t)[:, None]/(t2 - t0)*A1 + (t - t0)[:, None]/(t2 - t0)*A2
    B2 = (t3 - t)[:, None]/(t3 - t1)*A2 + (t - t1)[:, None]/(t3 - t1)*A3

    # Compute C (final points)
    C = (t2 - t)[:, None]/(t2 - t1)*B1 + (t - t1)[:, None]/(t2 - t1)*B2

    # Return as a list of tuples
    return [tuple(pt) for pt in C]

def smooth_polyline(points, smooth_fn, smooth_steps=8):
    if len(points) < 4:
        return points

    smoothed = [points[0]]
    for i in range(len(points) - 3):
        p0, p1, p2, p3 = points[i:i+4]
        curve_points = smooth_fn(p0, p1, p2, p3, nPoints=smooth_steps)
        smoothed.extend(curve_points[1:])
    
    if smoothed[-1] != points[-1]:
        smoothed.append(points[-1])
    
    return smoothed

def point_to_segment_closest_distance(px, py, x1, y1, x2, y2):
    # Vector from A to P
    APx = px - x1
    APy = py - y1

    # Vector from A to B
    ABx = x2 - x1
    ABy = y2 - y1

    # Project AP onto AB, computing parameterized position t
    AB_len_sq = ABx**2 + ABy**2
    if AB_len_sq == 0:  # Segment is a point
        return math.hypot(APx, APy), (x1, y1)
    t = max(0, min(1, (APx * ABx + APy * ABy) / AB_len_sq))

    # Closest point on the segment
    closest_x = x1 + t * ABx
    closest_y = y1 + t * ABy

    # Distance from P to closest point
    dist = math.hypot(px - closest_x, py - closest_y)
    return dist, (closest_x, closest_y)

def find_nearest_point(target_point, strokes):
    min_dist = float('inf')
    nearest_point = None
    nearest_idx = -1
    
    tx, ty = target_point
    
    input_is_points = len(strokes[0]) == 2

    if input_is_points:
        points = strokes[0]
        for px, py in points:
            dist_sq = (tx - px) ** 2 + (ty - py) ** 2 
            if dist_sq < min_dist:
                min_dist = dist_sq
                nearest_point = (px, py)
        nearest_idx = 0

    else:
        for s_idx, stroke in enumerate(strokes):
            # Check each segment of the stroke
            for i in range(len(stroke) - 1):
                (x1, y1), (x2, y2) = stroke[i], stroke[i + 1]
                dist, closest_pt = point_to_segment_closest_distance(tx, ty, x1, y1, x2, y2)
                if dist < min_dist:
                    min_dist = dist
                    nearest_point = closest_pt
                    nearest_idx = s_idx

    return nearest_point, nearest_idx

def stroke_horizontal_center(stroke):
    return sum(x for x, y in stroke) / len(stroke)

def compute_stroke_length(stroke):
    return sum((Vector((stroke[i+1].x, stroke[i+1].y, stroke[i+1].z)) -
                Vector((stroke[i].x, stroke[i].y, stroke[i].z))).length for i in range(len(stroke)-1))

def point_at_offset(stroke, offset):
    accumulated = 0.0
    for i in range(len(stroke) - 1):
        p1 = np.array(stroke[i])
        p2 = np.array(stroke[i + 1])
        seg = p2 - p1
        seg_len = np.linalg.norm(seg)

        if accumulated + seg_len >= offset:
            t = (offset - accumulated) / seg_len
            return (p1 + t * seg).tolist()

        accumulated += seg_len
    return stroke[-1]