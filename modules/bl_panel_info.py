import bpy

class GC_PT_info_panel(bpy.types.Panel):
    bl_idname = "GC_PT_info_panel"
    bl_label = "Information"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "GreenCanvas"

    def draw(self, context):
        layout = self.layout
        layout.scale_y = 1.4

        row = layout.row()
        row.operator("view3d.gc_ot_instructions_info", text="Help", icon="INFO")
        row.operator("view3d.gc_ot_instructions_video", text="Video", icon="FILE_MOVIE")

class GC_OT_show_instructions_info_operator(bpy.types.Operator):
    bl_idname = "view3d.gc_ot_instructions_info"
    bl_label = "Show Steps"
    bl_description = "Shows a panel with the steps to model the plant"
    bl_options = {'REGISTER'}

    def execute(self, context):
        bpy.ops.view3d.dp_ot_instructions_info_operator('INVOKE_DEFAULT')

        return {'FINISHED'}
    
class GC_OT_show_instructions_video_operator(bpy.types.Operator):
    bl_idname = "view3d.gc_ot_instructions_video"
    bl_label = "Show Video"
    bl_description = "Shows a panel with a link for the video on how to model the plant"
    bl_options = {'REGISTER'}

    def execute(self, context):
        bpy.ops.view3d.dp_ot_instructions_video_operator('INVOKE_DEFAULT')

        return {'FINISHED'}

classes = (
    GC_PT_info_panel, 
    GC_OT_show_instructions_info_operator,
    GC_OT_show_instructions_video_operator,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    

def unregister():    
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except RuntimeError:
            pass