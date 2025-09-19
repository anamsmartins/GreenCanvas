import bpy
import time

# --- Property Groups ---

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

    layout.separator()


def draw_tool_START(layout):
    layout.operator("view3d.gc_ot_start_drawing_operator", text="Start Drawing", icon="GREASEPENCIL")

def draw_tool_BRANCH(layout):

    row = layout.row()
    row.label(text= f"Brush Size:", icon="BRUSHES_ALL")

    # BL_UI_Slider
    layout.separator()
    layout.separator()
    layout.separator()

    row = layout.row()
    row.label(text= "Branch Shape:", icon="SHARPCURVE")

    # Branch Shape Canvas
    layout.separator()
    layout.separator()
    layout.separator()
    layout.separator()
    layout.separator()
    layout.separator()
    layout.separator()


def draw_tool_LEAF(layout):

    layout.label(text= "Curvature Type:", icon="FORCE_HARMONIC")

    # Leaf Curvature Type Canvas
    layout.separator()
    layout.separator()
    layout.separator()
    layout.separator()
    layout.separator()
    layout.separator()
    layout.separator()


# --- Operators ---

class GC_OT_set_active_tool_branch_operator(bpy.types.Operator):
    bl_idname = "view3d.gc_ot_set_active_tool_branch_operator"
    bl_label = "Set Branch Active Tool"
    bl_description = "Sets the Branch as the active tool"
    bl_options = {'REGISTER'}

    def execute(self, context):
        context.scene.panel_settings.active_tool = "BRANCH"
        set_branch_panel_active(True)
        return {'FINISHED'}
    
class GC_OT_set_active_tool_leaf_operator(bpy.types.Operator):
    bl_idname = "view3d.gc_ot_set_active_tool_leaf_operator"
    bl_label = "Set Leaf Active Tool"
    bl_description = "Sets the Leaf as the active tool"
    bl_options = {'REGISTER'}

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
    bl_label = "Active Tool"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "GreenCanvas"

    @classmethod
    def poll(cls, context):
        return bpy.context.scene.started_drawing and not bpy.context.scene.built_plant

    def draw(self, context):
        started_drawing = bpy.context.scene.started_drawing
        built_plant = bpy.context.scene.built_plant

        if (not started_drawing) or (built_plant):
            return

        global last_draw_time, draw_active
        last_draw_time = time.time()
        draw_active = True

        layout = self.layout
        layout.scale_y = 1.4

        settings = context.scene.panel_settings
        active_tool = settings.active_tool
        pcoll_icons = context.scene.preview_collections["main"]

        draw_tool_header(layout, pcoll_icons, active_tool)

        draw_func = globals().get(f'draw_tool_{active_tool}')
        draw_func(layout)

# --- Register & Unregister ---

classes = (
    GC_PT_active_tool_panel, 
    GC_OT_set_active_tool_branch_operator,
    GC_OT_set_active_tool_leaf_operator,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    try:
        bpy.app.timers.register(check_active_tool_panel_status, persistent=True)
    except ValueError:
        pass

def unregister():    
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except RuntimeError:
            pass

    try:
        bpy.app.timers.unregister(check_active_tool_panel_status)
    except ValueError:
        pass
