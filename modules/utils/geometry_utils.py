import bpy
import bmesh
from mathutils import Vector, Matrix
import math
import mathutils

from .branches_utils import get_branch_mesh_name

def build_plant_mesh(branches):
    # -- Create plant object
    plant_obj = bpy.data.objects.new("Plant", None)
    bpy.context.collection.objects.link(plant_obj)

    # -- Create branches object
    branches_obj = bpy.data.objects.new("Branches", None)
    bpy.context.collection.objects.link(branches_obj)
    branches_obj.parent = plant_obj

    # -- Create a mapping from index to mesh object
    branch_obj_map = {}
    branch_type_counter = {}
    branch_type_prefix = {}
    leaf_per_branch_counter = {}
    
    # -- For each branch, create its mesh and set up parenting
    for i, branch in enumerate(branches):
        branch_parent_id = branch.parent_id
        branch_parent = next((b for b in branches if b.branch_id == branch_parent_id), None)

        # Find parent
        if branch_parent_id == None or branch_parent_id < 1:
            branch_obj_parent = branches_obj
            parent_prefix = ""
        else:
            branch_obj_parent = branch_obj_map.get(branch_parent_id)
            parent_prefix = branch_type_prefix.get(branch_parent_id, "")

        # Setup name and prefix
        name, prefix = get_branch_mesh_name(branch, branch_obj_parent, parent_prefix, branch_type_counter)

        if bpy.context.scene.ignore_brush_size and branch_parent is not None:
            # compute radius of parent at this offset
            parent_base = branch_parent.brush_size
            parent_tip = 0.1 * branch_parent.brush_size
            t = branch.offset / branch_parent.length
            parent_radius_at_offset = (1 - t) * parent_base + t * parent_tip

            # Compute new brush size of branch
            branch.brush_size = min(branch.brush_size, parent_radius_at_offset * 0.9)
            branch.id_data.update_tag()

        # Project branch mesh
        branch_obj = project_branch(branch,  name=name)
        branch_obj.parent = branch_obj_parent
        origin_offset = Vector((branch.stroke[0].x, branch.stroke[0].y, branch.stroke[0].z))
        set_origin_to_point(branch_obj, origin_offset)
        branch_obj.modifiers.new(name="Decimate", type='DECIMATE')

        branch_type_prefix[branch.branch_id] = prefix
        branch_obj_map[branch.branch_id] = branch_obj
    
    # -- Create each leaf mesh and set up parenting
    for leaf in bpy.context.scene.leaf_collection.leaves:
        branch = next((b for b in branches if b.branch_id == leaf.branch_id), None)
        if branch is None:
            continue

        branch_id = leaf.branch_id
        leaf_per_branch_counter[branch_id] = leaf_per_branch_counter.get(branch_id, 0) + 1
        parent_prefix = branch_type_prefix.get(branch_id, "")

        leaf_obj = project_leaf(leaf, name=f"{parent_prefix} Leaf {leaf_per_branch_counter[branch_id]}")
        leaf_obj.parent = branch_obj_map.get(branch_id)
        leaf_obj.modifiers.new(name="Decimate", type='DECIMATE')

        leaf_origin = Vector((leaf.inner[0].x, leaf.inner[0].y, leaf.inner[0].z))
        set_origin_to_point(leaf_obj, leaf_origin)

        # Rotate leaf according to branch direction (to not be facing the camera)
        branch_tip = branch.stroke[-1]
        branch_base = branch.stroke[0]
        branch_vector = Vector((branch_tip.x - branch_base.x,
                        branch_tip.y - branch_base.y,
                        branch_tip.z - branch_base.z)).normalized()
        branch_vector_xy = Vector((branch_vector.x, branch_vector.y, 0)).normalized()
        perp_vector = Vector((-branch_vector_xy.y, branch_vector_xy.x, 0))
        z_axis = Vector((0, 0, 1))
        y_axis = perp_vector
        x_axis = z_axis.cross(y_axis).normalized()
        y_axis = x_axis.cross(z_axis).normalized()  # ensure orthogonal
        z_mat = Matrix((x_axis, y_axis, z_axis)).transposed().to_4x4()


        tilt_mat = Matrix.Rotation(math.radians(-75), 4, 'X')  # smaller tilt
        leaf_obj.matrix_world = Matrix.Translation(leaf_origin) @ z_mat @ tilt_mat
    

def project_branch(branch, name="Branch"):
    branch_stroke = [(p.x, p.y, p.z) for p in branch.stroke]
    brush_size = branch.brush_size

    curve_data = bpy.data.curves.new(f"{name} mesh", type='CURVE')
    curve_data.dimensions = '3D'
    spline = curve_data.splines.new('BEZIER')
    spline.bezier_points.add(len(branch_stroke) - 1)

    for i, (x, y, z) in enumerate(branch_stroke):
        bp = spline.bezier_points[i]
        bp.co = (x , y, z)
        bp.handle_left_type = 'AUTO'
        bp.handle_right_type = 'AUTO'

    bshape_left_stroke = branch.branch_shape_left_stroke
    bshape_right_stroke = branch.branch_shape_right_stroke

    if len(bshape_left_stroke) == 0:
        curve_obj = bpy.data.objects.new(f"{name}", curve_data)
        bpy.context.collection.objects.link(curve_obj)

        # Original curve with bevel
        curve_data.bevel_depth = brush_size * 0.05
        taper_object = get_default_branch_tip()
        curve_data.taper_object = taper_object

        bpy.context.view_layer.objects.active = curve_obj
        curve_obj.select_set(True)

        bpy.ops.object.convert(target='MESH')
        bpy.data.objects.remove(taper_object, do_unlink=True)
       
        mesh = curve_obj.data
        bm = bmesh.new()
        bm.from_mesh(mesh)
        bmesh.ops.holes_fill(bm, edges=[e for e in bm.edges if e.is_boundary], sides=0)
        bm.to_mesh(mesh)
        bm.free()

        curve_obj.select_set(False)

        return curve_obj
    
    # Else: model with branch shape strokes
    curve_obj = bpy.data.objects.new(f"{name} curve", curve_data)
    bpy.context.collection.objects.link(curve_obj)

    # Resample points
    n = int(((len(spline.bezier_points) - 1) * curve_data.resolution_u) / 2)
    bshape_stroke1 = resample_points(to_vectors(bshape_left_stroke), n)
    bshape_stroke2 = resample_points(to_vectors(bshape_right_stroke), n)

    # Create new mesh
    mesh = bpy.data.meshes.new(f"{name} mesh")
    bshape_obj = bpy.data.objects.new(f"{name}", mesh)
    bpy.context.collection.objects.link(bshape_obj)
    bm = bmesh.new()

    # Generate cross-section circles between rails
    circle_verts = 12
    radii = []
    for i in range(n):
        p1, p2 = bshape_stroke1[i], bshape_stroke2[i]
        radius = abs(p2.x - p1.x) / 2 
        radii.append(radius)

    min_radius = min(min(radii), 0.02)
    max_radius = max(radii)
    max_thickness = brush_size * 0.05

    rings = []
    for i in range(n):
        t = i / (n - 1)  # goes 0..1 along mesh length (local Z)
        p1, p2 = bshape_stroke1[i], bshape_stroke2[i]
        radius = ((radii[i] - min_radius) / (max_radius - min_radius)) * max_thickness
        
        ring = []
        for j in range(circle_verts):
            angle = 2 * math.pi * j / circle_verts
            x = math.cos(angle) * radius
            y = math.sin(angle) * radius
            v = bm.verts.new((x, y, t))
            ring.append(v)
        rings.append(ring)

    # Connect rings with faces
    for i in range(len(rings)-1):
        ring1, ring2 = rings[i], rings[i+1]
        for j in range(circle_verts):
            v1, v2 = ring1[j], ring1[(j+1)%circle_verts]
            v3, v4 = ring2[(j+1)%circle_verts], ring2[j]
            bm.faces.new([v1, v2, v3, v4])

    # Add tip vertex in local space (Z=1)
    tip_offset = 0.1  
    tip_vert = bm.verts.new((0, 0, 1.0 + tip_offset))

    last_ring = rings[-1]
    for j in range(circle_verts):
        v1 = last_ring[j]
        v2 = last_ring[(j+1) % circle_verts]
        bm.faces.new([v1, v2, tip_vert])

    # Add cap at bottom
    bm.faces.new(rings[0])

    bm.to_mesh(mesh)
    if hasattr(mesh, "update"):
        mesh.update()
    bm.free()

    # Smooth surface
    for poly in mesh.polygons:
        poly.use_smooth = True

    # Deform along curve
    deform = bshape_obj.modifiers.new("CurveDeform", 'CURVE')
    deform.object = curve_obj
    deform.deform_axis = 'POS_Z'

    bpy.ops.object.select_all(action='DESELECT')
    bshape_obj.select_set(True)   
    bpy.context.view_layer.objects.active = bshape_obj

    # Stretch from 0-1 to the curve length and 
    mesh_length = max(v.co.z for v in mesh.vertices) - min(v.co.z for v in mesh.vertices)
    curve_length = sum(
        (Vector((branch.stroke[i+1].x, branch.stroke[i+1].y, branch.stroke[i+1].z)) -
        Vector((branch.stroke[i].x, branch.stroke[i].y, branch.stroke[i].z))).length
        for i in range(len(branch.stroke) - 1)
    )
    bpy.ops.transform.resize(
        value=(1, 1, curve_length / mesh_length), 
        orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), 
        constraint_axis=(False, False, True), 
    )

    # Apply curve modifier
    bpy.ops.object.modifier_apply(modifier=deform.name)

    bshape_obj.select_set(False)   
    bpy.ops.object.select_all(action='DESELECT')

    # Position at the curve location
    start = branch.stroke[0]
    bshape_obj.location = Vector((start.x, start.y, start.z))

    # Remove curve object
    bpy.data.objects.remove(curve_obj, do_unlink=True)

    return bshape_obj

def get_default_branch_tip(name="BranchTaperCurve"):
    points=[(0, 1), (1, 0)]
    curve_data = bpy.data.curves.new(name, type='CURVE')
    curve_data.dimensions = '2D'
    polyline = curve_data.splines.new('POLY')
    polyline.points.add(len(points) - 1)
    for i, (x, y) in enumerate(points):
        polyline.points[i].co = (x, y, 0, 1)
    obj = bpy.data.objects.new(name, curve_data)
    bpy.context.collection.objects.link(obj)
    return obj

def project_leaf(leaf, name="Leaf"):
    outline1 = to_vectors(leaf.outline1)
    outline2 = to_vectors(leaf.outline2)
    inner = to_vectors(leaf.inner)
    curvature_type = to_vectors(leaf.curvature_type)

    n = max(len(outline1), len(outline2))
    outline1 = resample_points(outline1, n)
    outline2 = resample_points(outline2, n)
    inner = resample_points(inner, n)
    depths = compute_leaf_curvature_depth(curvature_type, n)

    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    bm = bmesh.new()

    # Create vertices by interpolating between outline1 and outline2
    rows = 10
    grid = []
    for i in range(n):
        v_left = outline1[i]
        v_right = outline2[i]
        v_mid = inner[i]
        depth = max(depths[i], 0.01)

        for j in range(rows):
            t = j / (rows - 1)

            base = v_left.lerp(v_right, t)

            bias = 0.2 if depth > 0 else 0
            v = base.lerp(v_mid, bias)

            # slitghtly lower the midrib and border points
            if (j==0 or j == int(rows/2) or j==rows-1):
                v.y += 0.05

            v = Vector((v.x, v.y - depth, v.z))
            v = bm.verts.new(v)

            grid.append(v)

    bm.verts.ensure_lookup_table()
    
    # Create faces between grid points
    for i in range(n-1):
        for j in range(rows-1):
            v1 = grid[i*rows + j]
            v2 = grid[i*rows + j+1]
            v3 = grid[(i+1)*rows + j+1]
            v4 = grid[(i+1)*rows + j]
            bm.faces.new((v1, v2, v3, v4))

    bm.to_mesh(mesh)
    bm.free()

    # Smooth the mesh
    obj.modifiers.new("Subdivision", type='SUBSURF')
    obj.modifiers["Subdivision"].levels = 2

    # Set shading to smooth
    for poly in mesh.polygons:
        poly.use_smooth = True

    return obj

def compute_leaf_curvature_depth(curvature_type, n, canvas_size=(160, 65)):
    width, height = canvas_size

    # Normalize curvature stroke into [0,1]
    normed = [Vector((pt.x / width, pt.y / height, 0)) for pt in curvature_type]

    resampled = resample_points(normed, n)
    mapped = [(pt.y * height * 0.012) for pt in resampled]

    return mapped

def set_origin_to_point(obj, base_point: mathutils.Vector):
    # Get base point in object local coordinates
    local_base = obj.matrix_world.inverted() @ base_point

    # Shift mesh data so that base point is at local (0,0,0)
    obj.data.transform(mathutils.Matrix.Translation(-local_base))

    # Compute new world matrix: put origin at base_point_world
    new_world = mathutils.Matrix.Translation(base_point) @ obj.matrix_world

    if obj.parent:
        # Update parent inverse so the parent–child relationship is preserved
        obj.matrix_parent_inverse = obj.parent.matrix_world.inverted() @ new_world

    obj.matrix_world = new_world

def to_vectors(points):
    return [Vector((pt.x, pt.y, pt.z)) for pt in points]

def resample_points(points, target_count):
    if len(points) == 0:
        return []
    if len(points) == 1:
        return points * target_count

    # compute cumulative distances
    dists = [0.0]
    for i in range(1, len(points)):
        d = (points[i] - points[i-1]).length
        dists.append(dists[-1] + d)

    total_length = dists[-1]
    step = total_length / (target_count - 1)

    resampled = []
    j = 0
    for k in range(target_count):
        t = k * step
        while j < len(dists)-1 and dists[j+1] < t:
            j += 1
        # interpolate between points[j] and points[j+1]
        if j == len(points)-1:
            resampled.append(points[-1])
        else:
            if j == len(points)-1 or dists[j+1] == dists[j]:
                p = points[j]
            else:
                f = (t - dists[j]) / (dists[j+1] - dists[j])
                p = points[j].lerp(points[j+1], f)
            resampled.append(p)
    return resampled
