import bpy

# --- Strokes ---

class GC_PG_Point(bpy.types.PropertyGroup):
    x: bpy.props.FloatProperty(default=0.0)
    y: bpy.props.FloatProperty(default=0.0)
    z: bpy.props.FloatProperty(default=0.0)

class GC_PG_Stroke(bpy.types.PropertyGroup):
    points: bpy.props.CollectionProperty(type=GC_PG_Point)

# --- Branches ---

# A single branch
class GC_PG_Branch(bpy.types.PropertyGroup):
    stroke: bpy.props.CollectionProperty(type=GC_PG_Point)
    start_position: bpy.props.PointerProperty(type=GC_PG_Point)
    end_position: bpy.props.PointerProperty(type=GC_PG_Point)
    brush_size: bpy.props.FloatProperty(name="Brush Size", default=3, min=0, max=5)
    branch_type: bpy.props.EnumProperty(
        name="Branch Type",
        description="Type of branch",
        items=[
            ('TRUNK', "Trunk", "The first branch of the plant"),
            ('MAIN', "Main", "Branch connected to the trunk branch"),
            ('CHILD', "Child", "Branch connected to the main and/or other child branches")
        ],
        default='TRUNK'
    )
    branch_id: bpy.props.IntProperty(default=0)
    parent_id: bpy.props.IntProperty(default=-1)
    level: bpy.props.IntProperty(default=0)
    offset: bpy.props.FloatProperty(default=0) # offset along the parent branch
    length: bpy.props.FloatProperty(default=0)
    limit_angle: bpy.props.FloatProperty(default=0)
    # Optional
    branch_shape_left_stroke: bpy.props.CollectionProperty(type=GC_PG_Point)
    branch_shape_right_stroke: bpy.props.CollectionProperty(type=GC_PG_Point)

# Collection of branches
class GC_PG_BranchCollection(bpy.types.PropertyGroup):
    branches: bpy.props.CollectionProperty(type=GC_PG_Branch)

# --- Leaves ---

# A single leaf
class GC_PG_Leaf(bpy.types.PropertyGroup):
    outline1: bpy.props.CollectionProperty(type=GC_PG_Point)
    outline2: bpy.props.CollectionProperty(type=GC_PG_Point)
    inner: bpy.props.CollectionProperty(type=GC_PG_Point)
    curvature_type: bpy.props.CollectionProperty(type=GC_PG_Point)
    branch_id: bpy.props.IntProperty(default=-1)
    branch_offset: bpy.props.FloatProperty(default=0)

# Collection of leaves
class GC_PG_LeafCollection(bpy.types.PropertyGroup):
    leaves: bpy.props.CollectionProperty(type=GC_PG_Leaf)

# --- Panels ---

class GC_PG_panel_settings(bpy.types.PropertyGroup):
    active_tool: bpy.props.EnumProperty(
        name="Active Tool",
        items=[('BRANCH', "Branch", "Switch to Branch Tool"), # (identifier, name, description)
               ('LEAF', "Leaf", "Switch to Leaf Tool")],
        default="BRANCH",
    )

# --- Branch Shape Canvas ---

class GC_PG_branch_shape_canvas_settings(bpy.types.PropertyGroup):
    left_stroke: bpy.props.CollectionProperty(type=GC_PG_Point)
    right_stroke: bpy.props.CollectionProperty(type=GC_PG_Point)

# --- Branch Slider ---

class GC_PG_branch_slider_settings(bpy.types.PropertyGroup):
    brush_size: bpy.props.IntProperty(
        name="Branch slider brush size value",
        default=4,
        min=1,
        max=5,
    )

# --- Leaf Curvature Type Canvas ---

class GC_PG_leaf_curvature_type_canvas_settings(bpy.types.PropertyGroup):
    stroke: bpy.props.CollectionProperty(type=GC_PG_Point)

def get_model_type_items(self, context):
    return [
        ('ACC', 'Accurate', 'Build a plant model that is accurate the drawing'),
        ('REAL', 'Realistic', 'Build a realistic plant model'),
    ]

def get_propagate_leaves_items(self, context):
    return [
        ('REAL', 'Realistic', 'Propagate leaves realistically along the branch'),
        ('RANDOM', 'Random', 'Propagate leaves randomly along the branch'),

    ]

# --- Register & Unregister ---

classes = (
    GC_PG_Point,
    GC_PG_Stroke,
    GC_PG_Branch,
    GC_PG_BranchCollection,
    GC_PG_Leaf,
    GC_PG_LeafCollection,
    GC_PG_panel_settings,
    GC_PG_branch_shape_canvas_settings,
    GC_PG_branch_slider_settings,
    GC_PG_leaf_curvature_type_canvas_settings,
)
        
def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.panel_settings = bpy.props.PointerProperty(type=GC_PG_panel_settings)
    bpy.types.Scene.branch_collection = bpy.props.PointerProperty(type=GC_PG_BranchCollection)
    bpy.types.Scene.leaf_collection = bpy.props.PointerProperty(type=GC_PG_LeafCollection)
    bpy.types.Scene.branch_shape_canvas_settings = bpy.props.PointerProperty(type=GC_PG_branch_shape_canvas_settings)
    bpy.types.Scene.branch_slider_settings = bpy.props.PointerProperty(type=GC_PG_branch_slider_settings)
    bpy.types.Scene.leaf_curvature_type_canvas_settings = bpy.props.PointerProperty(type=GC_PG_leaf_curvature_type_canvas_settings)
    bpy.types.Scene.draw_operators = []
    bpy.types.Scene.started_drawing = bpy.props.BoolProperty(name="Started Drawing", default= False)
    bpy.types.Scene.main_canvas_visible = bpy.props.BoolProperty(name="Main Canvas Visible", default= False)
    bpy.types.Scene.built_plant = bpy.props.BoolProperty(name="Built Plant", default= False)

    bpy.types.Scene.model_type_selector = bpy.props.EnumProperty(
        name="Model Type",
        description="Choose an option",
        items=get_model_type_items
    )

    bpy.types.Scene.propagate_leaves_selector = bpy.props.EnumProperty(
        name="Propagate Leaves Type",
        description="Choose an option",
        items=get_propagate_leaves_items
    )

    bpy.types.Scene.ignore_brush_size = bpy.props.BoolProperty(
        name="Ignore Brush Size",
        description="If enabled, branch thickness will vary naturally instead of strictly following the brush size.",
        default=False
    )


def unregister():  
    bpy.context.scene.panel_settings.active_tool = 'BRANCH'
    bpy.context.scene.branch_collection.branches.clear()
    bpy.context.scene.leaf_collection.leaves.clear()
    bpy.context.scene.branch_shape_canvas_settings.left_stroke.clear()
    bpy.context.scene.branch_shape_canvas_settings.right_stroke.clear()
    bpy.context.scene.branch_slider_settings.brush_size = 4
    bpy.context.scene.leaf_curvature_type_canvas_settings.stroke.clear()

    for op in getattr(bpy.context.scene, "draw_operators", []):
        try:
            op.finish()
        except ReferenceError:
            pass
    bpy.context.scene.draw_operators.clear()

    bpy.context.scene.started_drawing = False
    bpy.context.scene.main_canvas_visible = False
    bpy.context.scene.built_plant = False 
    bpy.context.scene.ignore_brush_size = False

    del bpy.types.Scene.panel_settings
    del bpy.types.Scene.branch_collection
    del bpy.types.Scene.leaf_collection
    del bpy.types.Scene.branch_shape_canvas_settings
    del bpy.types.Scene.branch_slider_settings
    del bpy.types.Scene.leaf_curvature_type_canvas_settings
    del bpy.types.Scene.draw_operators
    del bpy.types.Scene.started_drawing
    del bpy.types.Scene.main_canvas_visible
    del bpy.types.Scene.built_plant

    del bpy.types.Scene.model_type_selector
    del bpy.types.Scene.propagate_leaves_selector
    del bpy.types.Scene.ignore_brush_size
    
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except RuntimeError:
            pass
