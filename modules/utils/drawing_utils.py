import math

import bpy
import gpu
from gpu_extras.batch import batch_for_shader

from .stroke_utils import find_nearest_point, smooth_polyline, catmull_rom_spline

def build_2d_polyline_with_brush_size(points, brush_size, cap_segments=8):
    verts = []
    indices = []
    half_thick = brush_size / 2.0

    def add_cap(center, start_angle, end_angle):
        base_idx = len(verts)
        verts.append(center)
        for i in range(cap_segments + 1):
            angle = start_angle + (end_angle - start_angle) * (i / cap_segments)
            verts.append((
                center[0] + math.cos(angle) * half_thick,
                center[1] + math.sin(angle) * half_thick
            ))
        for i in range(cap_segments):
            indices.append((base_idx, base_idx + i + 1, base_idx + i + 2))

    for i in range(len(points) - 1):
        x1, y1 = points[i]
        x2, y2 = points[i + 1]

        dx = x2 - x1
        dy = y2 - y1
        length = math.hypot(dx, dy)
        if length == 0:
            continue
        dx /= length
        dy /= length

        px = -dy * half_thick
        py = dx * half_thick

        v0 = (x1 + px, y1 + py)
        v1 = (x1 - px, y1 - py)
        v2 = (x2 - px, y2 - py)
        v3 = (x2 + px, y2 + py)

        base_index = len(verts)
        verts.extend([v0, v1, v2, v3])
        indices.extend([
            (base_index, base_index + 1, base_index + 2),
            (base_index, base_index + 2, base_index + 3)
        ])

        if i == 0:
            add_cap((x1, y1), math.atan2(py, px), math.atan2(-py, -px))
        if i == len(points) - 2:
            add_cap((x2, y2), math.atan2(-py, -px), math.atan2(py, px))

    return verts, indices

def attach_stroke_to_nearest_point(new_stroke, strokes, limit=None):
    if limit is None:
        limit = {"xmin": None, "xmax": None, "ymin": None, "ymax": None}

    # Check both ends of the stroke
    start_point = new_stroke[0]
    end_point = new_stroke[-1]

    # Find nearest stroke for both tips
    point_a, idx_a = find_nearest_point(start_point, strokes)
    point_b, idx_b = find_nearest_point(end_point, strokes)

    # Compute distances
    dist_a = math.hypot(start_point[0] - point_a[0], start_point[1] - point_a[1])
    dist_b = math.hypot(end_point[0] - point_b[0], end_point[1] - point_b[1])

    # Choose the closer tip
    if dist_a <= dist_b:
        attach_point = start_point
        nearest_point = point_a
        parent_idx = idx_a
    else:
        attach_point = end_point
        nearest_point = point_b
        parent_idx = idx_b
        # Reverse the stroke so the attached tip is first
        new_stroke.reverse()

    # Compute movement offset
    dx = nearest_point[0] - attach_point[0]
    dy = nearest_point[1] - attach_point[1]

    adjusted_stroke = [
        (px + dx, py + dy)
        for px, py in new_stroke
        if (limit["xmin"] is None or px + dx >= limit["xmin"])
        and (limit["xmax"] is None or px + dx <= limit["xmax"])
        and (limit["ymin"] is None or py + dy >= limit["ymin"])
        and (limit["ymax"] is None or py + dy <= limit["ymax"])
    ]

    return adjusted_stroke, parent_idx, nearest_point
    

def stretch_stroke_to_tips(stroke, target_tip_a, target_tip_b):
    if not stroke or len(stroke) < 2:
        raise ValueError("Stroke must have at least two points")

    # Determine if reversing is needed
    dist_normal = math.hypot(stroke[0][0] - target_tip_a[0], stroke[0][1] - target_tip_a[1])
    dist_reversed = math.hypot(stroke[-1][0] - target_tip_a[0], stroke[-1][1] - target_tip_a[1])

    if dist_reversed < dist_normal:
        stroke = list(reversed(stroke))

    # Replace first and last points
    new_stroke = [target_tip_a] + stroke[1:-1] + [target_tip_b]

    return new_stroke

def draw_stroke(points, color, brush_size, brush_size_bias=2, smooth_steps=8):
    if len(points) < 2:
        return

    smoothed = smooth_polyline(points, catmull_rom_spline, smooth_steps)
    verts, indices = build_2d_polyline_with_brush_size(smoothed, brush_size + brush_size_bias)

    shader = gpu.shader.from_builtin('UNIFORM_COLOR' if bpy.app.version[0] >= 4 else '2D_UNIFORM_COLOR')
    batch = batch_for_shader(shader, 'TRIS', {"pos": verts}, indices=indices)

    shader.bind()
    shader.uniform_float("color", color)
    batch.draw(shader)

    

