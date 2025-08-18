import math

def catmull_rom_spline(P0, P1, P2, P3, nPoints=20):
    """Generates points between P1 and P2 using Catmull–Rom Spline (pure Python)"""
    alpha = 0.5

    def tj(ti, Pi, Pj):
        dx = Pj[0] - Pi[0]
        dy = Pj[1] - Pi[1]
        dist = math.sqrt(dx*dx + dy*dy)
        return (dist ** alpha) + ti

    t0 = 0.0
    t1 = tj(t0, P0, P1)
    t2 = tj(t1, P1, P2)
    t3 = tj(t2, P2, P3)

    # Avoid zero-length intervals by adding a tiny epsilon
    eps = 1e-6
    if abs(t1 - t0) < eps or abs(t2 - t1) < eps or abs(t3 - t2) < eps:
        # Just return a straight line between P1 and P2
        return [P1, P2]

    points = []
    for step in range(nPoints):
        ti = t1 + (step / (nPoints - 1)) * (t2 - t1)

        A1x = (t1 - ti)/(t1 - t0)*P0[0] + (ti - t0)/(t1 - t0)*P1[0]
        A1y = (t1 - ti)/(t1 - t0)*P0[1] + (ti - t0)/(t1 - t0)*P1[1]

        A2x = (t2 - ti)/(t2 - t1)*P1[0] + (ti - t1)/(t2 - t1)*P2[0]
        A2y = (t2 - ti)/(t2 - t1)*P1[1] + (ti - t1)/(t2 - t1)*P2[1]

        A3x = (t3 - ti)/(t3 - t2)*P2[0] + (ti - t2)/(t3 - t2)*P3[0]
        A3y = (t3 - ti)/(t3 - t2)*P2[1] + (ti - t2)/(t3 - t2)*P3[1]

        B1x = (t2 - ti)/(t2 - t0)*A1x + (ti - t0)/(t2 - t0)*A2x
        B1y = (t2 - ti)/(t2 - t0)*A1y + (ti - t0)/(t2 - t0)*A2y

        B2x = (t3 - ti)/(t3 - t1)*A2x + (ti - t1)/(t3 - t1)*A3x
        B2y = (t3 - ti)/(t3 - t1)*A2y + (ti - t1)/(t3 - t1)*A3y

        Cx = (t2 - ti)/(t2 - t1)*B1x + (ti - t1)/(t2 - t1)*B2x
        Cy = (t2 - ti)/(t2 - t1)*B1y + (ti - t1)/(t2 - t1)*B2y

        points.append((Cx, Cy))
    return points

def smooth_polyline(points, smooth_fn, smooth_steps=8):
    """Smooth a list of points using a 4-point spline function."""
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
    
    tx, ty = target_point
    
    input_is_points = len(strokes[0]) == 2

    if input_is_points:
        points = strokes[0]
        for px, py in points:
            dist_sq = (tx - px) ** 2 + (ty - py) ** 2 
            if dist_sq < min_dist:
                min_dist = dist_sq
                nearest_point = (px, py)

    else:
        for stroke in strokes:
            # Check each segment of the stroke
            for i in range(len(stroke) - 1):
                (x1, y1), (x2, y2) = stroke[i], stroke[i + 1]
                dist, closest_pt = point_to_segment_closest_distance(tx, ty, x1, y1, x2, y2)
                if dist < min_dist:
                    min_dist = dist
                    nearest_point = closest_pt
    
    return nearest_point

def stroke_horizontal_center(stroke):
    return sum(x for x, y in stroke) / len(stroke)