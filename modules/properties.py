import bpy

# --- Strokes ---

class GC_PG_X_Y_Point(bpy.types.PropertyGroup):
    point: bpy.props.FloatVectorProperty(size=2)

class GC_PG_Stroke(bpy.types.PropertyGroup):
    points: bpy.props.CollectionProperty(type=GC_PG_X_Y_Point)

# --- Branches ---

# A single branch
class GC_PG_Branch(bpy.types.PropertyGroup):
    stroke: bpy.props.CollectionProperty(type=GC_PG_X_Y_Point)
    start_position: bpy.props.PointerProperty(type=GC_PG_X_Y_Point)
    end_position: bpy.props.PointerProperty(type=GC_PG_X_Y_Point)
    brush_size: bpy.props.IntProperty(name="Brush Size", default=3, min=1, max=5)
    # Optional
    branch_shape: bpy.props.CollectionProperty(type=GC_PG_Stroke)

# Collection of branches
class GC_PG_BranchCollection(bpy.types.PropertyGroup):
    branches: bpy.props.CollectionProperty(type=GC_PG_Branch)

# --- Leaves ---

# A single leaf
class GC_PG_Leaf(bpy.types.PropertyGroup):
    outline1: bpy.props.CollectionProperty(type=GC_PG_X_Y_Point)
    outline2: bpy.props.CollectionProperty(type=GC_PG_X_Y_Point)
    inner: bpy.props.CollectionProperty(type=GC_PG_X_Y_Point)
    curvature_type: bpy.props.CollectionProperty(type=GC_PG_X_Y_Point)

# Collection of leaves
class GC_PG_LeafCollection(bpy.types.PropertyGroup):
    leaves: bpy.props.CollectionProperty(type=GC_PG_Leaf)

# --- Register & Unregister ---

classes = [GC_PG_X_Y_Point, GC_PG_Stroke, GC_PG_Branch, GC_PG_BranchCollection, GC_PG_Leaf, GC_PG_LeafCollection ]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.branch_collection = bpy.props.PointerProperty(type=GC_PG_BranchCollection)
    bpy.types.Scene.leaf_collection = bpy.props.PointerProperty(type=GC_PG_LeafCollection)


def unregister():
    del bpy.types.Scene.branch_collection
    del bpy.types.Scene.leaf_collection
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)