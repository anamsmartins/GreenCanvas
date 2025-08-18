import bpy
import time

# --- Property Groups ---
branch_panel_active = False

def set_branch_panel_active(value):
    global branch_panel_active
    branch_panel_active = value

def is_branch_panel_active():
    global branch_panel_active
    return branch_panel_active and is_tool_panel_active()

def is_branch_panel_inactive():
    global branch_panel_active
    return not branch_panel_active and is_tool_panel_active()

def is_tool_panel_active():
    global draw_active
    return draw_active

class GC_PG_panel_settings(bpy.types.PropertyGroup):
    active_tool: bpy.props.EnumProperty(
        name="Active Tool",
        items=[('BRANCH', "Branch", "Switch to Branch Tool"), # (identifier, name, description)
               ('LEAF', "Leaf", "Switch to Leaf Tool"),
               ('START', "Start Drawing", "Setup menus and canvas to start drawing")],
        default="START",
    )

# --- Functions ---

def get_active_tool_icon(pcoll_icons, tool, current_active_tool):
    active_icon = f"{tool.lower()}-active-icon"
    inactive_icon = f"{tool.lower()}-inactive-icon"
    return pcoll_icons[active_icon].icon_id if current_active_tool == tool.upper() else pcoll_icons[inactive_icon].icon_id

def draw_tool_header(layout, pcoll_icons, active_tool):
    # -- Branch/Leaf buttons -- 
    split = layout.split(factor=0.5)

    col_left = split.column()
    row_left = col_left.row(align=True)
    row_left.scale_x = 1.1
    row_left.scale_y = 1.1
    
    branch_icon_id = get_active_tool_icon(pcoll_icons, 'branch', active_tool)
    leaf_icon_id = get_active_tool_icon(pcoll_icons, 'leaf', active_tool)
    
    row_left.operator("view3d.gc_ot_set_active_tool_branch_operator", icon_value=branch_icon_id, text="", emboss=False)
    row_left.operator("view3d.gc_ot_set_active_tool_leaf_operator", icon_value=leaf_icon_id, text="", emboss=False)

    # -- Undo/Clear buttons -- 

    col_right = split.column()
    row_right = col_right.row(align=True)
    row_right.alignment = 'RIGHT'
    row_right.scale_x = 1.1
    row_right.scale_y = 1.1

    row_right.operator("view3d.gc_ot_main_canvas_undo", icon_value=pcoll_icons["undo-icon"].icon_id, text="", emboss=False)
    row_right.operator("view3d.gc_ot_main_canvas_clear", icon_value=pcoll_icons["clear-icon"].icon_id, text="", emboss=False)


def draw_tool_START(layout, pcoll_icons):
    layout.operator("view3d.gc_ot_start_drawing_operator", text="Start Drawing")

def draw_tool_BRANCH(layout, pcoll_icons):

    row = layout.row()
    row.label(text= f"Brush Size:")

    # BL_UI_Slider
    layout.separator()
    layout.separator()
    layout.separator()

    row = layout.row()
    row.label(text= "Branch Shape:")

    # Branch Shape Canvas
    layout.separator()
    layout.separator()
    layout.separator()
    layout.separator()
    layout.separator()
    layout.separator()
    layout.separator()


def draw_tool_LEAF(layout, pcoll_icons):

    layout.label(text= "Curvature Type:")

    # Leaf Curvature Type Canvas
    layout.separator()
    layout.separator()
    layout.separator()
    layout.separator()
    layout.separator()
    layout.separator()
    layout.separator()



# --- Operators ---

class GC_OT_start_drawing_operator(bpy.types.Operator):
    bl_idname = "view3d.gc_ot_start_drawing_operator"
    bl_label = "Start Drawing"
    bl_description = "Starts the drawing process"

    def execute(self, context):
        context.scene.panel_settings.active_tool = "BRANCH"
        set_branch_panel_active(True)
        bpy.ops.view3d.dp_ot_draw_main_canvas_operator('INVOKE_DEFAULT') # open main drawing canvas
        bpy.ops.view3d.dp_ot_draw_branch_slider_operator('INVOKE_DEFAULT') # open branch slider
        bpy.ops.view3d.dp_ot_draw_branch_shape_canvas_operator('INVOKE_DEFAULT') # open branch shape canvas
        bpy.ops.view3d.dp_ot_draw_leaf_curvature_type_canvas_operator('INVOKE_DEFAULT') # open leaf curvature type canvas

        return {'FINISHED'}

class GC_OT_set_active_tool_branch_operator(bpy.types.Operator):
    bl_idname = "view3d.gc_ot_set_active_tool_branch_operator"
    bl_label = "Set Branch Active Tool"
    bl_description = "Sets the Branch as the active tool"

    def execute(self, context):
        context.scene.panel_settings.active_tool = "BRANCH"
        set_branch_panel_active(True)
        return {'FINISHED'}
    
class GC_OT_set_active_tool_leaf_operator(bpy.types.Operator):
    bl_idname = "view3d.gc_ot_set_active_tool_leaf_operator"
    bl_label = "Set Leaf Active Tool"
    bl_description = "Sets the Leaf as the active tool"

    def execute(self, context):
        context.scene.panel_settings.active_tool = "LEAF"
        set_branch_panel_active(False)
        return {'FINISHED'}

# --- Panels ---

last_draw_time = 0
draw_active = False

def check_active_tool_panel_status():
    global last_draw_time, draw_active

    now = time.time()
    # If draw was active but hasn't been called for >1 second
    if draw_active and (now - last_draw_time) > 0.15:
        draw_active = False

    return 0.1

class GC_PT_active_tool_panel(bpy.types.Panel):
    bl_idname = "GC_PT_active_tool_panel"
    bl_label = "Active Tool Panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "GreenCanvas"

    def draw(self, context):
        global last_draw_time, draw_active
        last_draw_time = time.time()
        draw_active = True

        layout = self.layout
        layout.scale_y = 1.4

        settings = context.scene.panel_settings
        active_tool = settings.active_tool
        pcoll_icons = context.scene.preview_collections["main"]

        if (active_tool != "START"):
            draw_tool_header(layout, pcoll_icons, active_tool)

        draw_func = globals().get(f'draw_tool_{active_tool}')
        draw_func(layout, pcoll_icons)

        
class GC_PT_actions_panel(bpy.types.Panel):
    bl_idname = "GC_PT_actions_panel"
    bl_label = "Actions Panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "GreenCanvas"

    def draw(self, context):
        settings = context.scene.panel_settings
        active_tool = settings.active_tool

        layout = self.layout
        layout.scale_y = 1.4
        
        if (active_tool != "START"):
            row = layout.row()
            row.operator("mesh.primitive_uv_sphere_add", text="Build Plant")

class GC_PT_info_panel(bpy.types.Panel):
    bl_idname = "GC_PT_info_panel"
    bl_label = "Information Panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "GreenCanvas"

    def draw(self, context):
        layout = self.layout
        layout.scale_y = 1.4

        row = layout.row()
        row.operator("mesh.primitive_uv_sphere_add", text="i")
        row.operator("mesh.primitive_uv_sphere_add", text="video")

# --- Register & Unregister ---

classes = (
    GC_PG_panel_settings, 
    GC_PT_active_tool_panel, 
    GC_PT_actions_panel, 
    GC_PT_info_panel, 
    GC_OT_set_active_tool_branch_operator,
    GC_OT_set_active_tool_leaf_operator,
    GC_OT_start_drawing_operator,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.panel_settings = bpy.props.PointerProperty(type=GC_PG_panel_settings)
    bpy.app.timers.register(check_active_tool_panel_status, persistent=True)
    

def unregister():    
    del bpy.types.Scene.panel_settings
    bpy.app.timers.unregister(check_active_tool_panel_status)
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
