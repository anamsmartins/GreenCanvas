import bpy
import time

last_draw_time = 0
properties_draw_active = False

def is_properties_panel_active():
    global properties_draw_active
    return properties_draw_active

def check_properties_panel_status():
    global last_draw_time, properties_draw_active

    now = time.time()
    # If draw was active but hasn't been called for >1 second
    if properties_draw_active and (now - last_draw_time) > 0.15:
        properties_draw_active = False

    return 0.1

class GC_PT_properties_panel(bpy.types.Panel):
    bl_idname = "GC_PT_properties_panel"
    bl_label = "Plant Properties"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "GreenCanvas"

    @classmethod
    def poll(cls, context):
        return bpy.context.scene.built_plant

    def draw(self, context):
        global last_draw_time, properties_draw_active
        last_draw_time = time.time()
        properties_draw_active = True

        layout = self.layout
        layout.scale_y = 1.4

        row = layout.row()
        row.label(text= f"Level of Detail:", icon="MESH_ICOSPHERE")

        # BL_UI_Slider
        layout.separator()
        layout.separator()
        layout.separator()        

        row = layout.row()
        row.label(text="Propagate leaves:", icon="OUTLINER_OB_POINTCLOUD")
        row = layout.row(align=True)
        row.prop(context.scene, "propagate_leaves_selector", text="")
        row.separator(factor=0.5) 
        row.operator("mesh.gc_ot_propagate_leaves", text="Leaves")

        layout.separator()

        row = layout.row()
        row.operator("mesh.gc_ot_build_plant", text="Generate Plant Variation", icon="SHADERFX").is_variation = True

        layout.separator()


classes = (
    GC_PT_properties_panel, 
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    try:
        bpy.app.timers.register(check_properties_panel_status, persistent=True)
    except ValueError:
        pass
    

def unregister():    
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except RuntimeError:
            pass
    
    try:
        bpy.app.timers.unregister(check_properties_panel_status)
    except ValueError:
        pass