
import math
import bpy
import numpy as np

from shapely.geometry import MultiPoint, Polygon
from scipy.spatial import ConvexHull


def convex_hull_2d(points_xy):
    hull_poly = MultiPoint(points_xy).convex_hull 

    if hull_poly.is_empty:
        raise ValueError("2D hull is empty. Check your input points.")
    
    if not isinstance(hull_poly, Polygon):
        hull_poly = hull_poly.buffer(0.1)

    return hull_poly

def interpolate_hull_x(polygon: Polygon, y):
    min_x = float('inf')
    max_x = float('-inf')

    coords = list(polygon.exterior.coords)

    for i in range(len(coords)-1):
        (x0, y0), (x1, y1) = coords[i], coords[i+1]

        if y0 == y1:
            if y == y0:
                min_x = min(min_x, x0, x1)
                max_x = max(max_x, x0, x1)
        elif (y0 <= y <= y1) or (y1 <= y <= y0):
            t = (y - y0)/(y1 - y0)
            x = x0 + t*(x1 - x0)
            min_x = min(min_x, x)
            max_x = max(max_x, x)

    if min_x == float('inf') or max_x == float('-inf'):
        return None, None
    
    return min_x, max_x

def convex_hull_3d(points_2d, hull_poly, n_layers=32, samples_per_circle=136):
    # Define Y Layers for Sweeping (split vertical range into n layers)
    y_layers = np.linspace(min(p[1] for p in points_2d), max(p[1] for p in points_2d), n_layers)

    # For each layer
    cloud = []

    for y in y_layers:
        x_min, x_max = interpolate_hull_x(hull_poly, y)
        if x_min is None:
            continue

        radius = (x_max - x_min)/2
        x_center = (x_max + x_min)/2
        
        radius *= math.sqrt(2)

        # Sample points around the circle in X-Z plane
        angles = np.linspace(0, 2*np.pi, samples_per_circle, endpoint=False)
        for angle in angles:
            adjusted_x = x_center + radius * np.cos(angle)
            adjusted_y = radius * np.sin(angle)   # horizontal depth
            adjusted_z = y 
            cloud.append((adjusted_x, adjusted_y, adjusted_z))

    points_3d = np.array(cloud)
    hull_3d = ConvexHull(points_3d)

    return points_3d, hull_3d

def export_convex_hull_to_blender(points_3d, hull_3d, name="ConvexHullObject"):
    verts = [tuple(v) for v in points_3d]
    
    # ConvexHull simplices are triangles, suitable for faces
    faces = [tuple(triangle) for triangle in hull_3d.simplices]

    # Create mesh and object
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()

    obj = bpy.data.objects.new(name, mesh)

    # Link object to scene
    scene = bpy.context.scene
    scene.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    
    return obj