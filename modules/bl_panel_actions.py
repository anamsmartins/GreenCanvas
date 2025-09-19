import bpy

from .bl_panel_active_tool import set_branch_panel_active
from .dp_main_canvas_op import register as dp_main_canvas_op_register
from .sp_branch_slider_op import register as sp_branch_slider_op_register
from .sp_branch_shape_canvas_op import register as sp_branch_shape_canvas_op_register
from .sp_leaf_curvature_type_canvas_op import register as sp_leaf_curvature_type_canvas_op_register

class GC_PT_actions_panel(bpy.types.Panel):
    bl_idname = "GC_PT_actions_panel"
    bl_label = "Actions"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "GreenCanvas"

    def draw(self, context):
        layout = self.layout
        layout.scale_y = 1.4

        started_drawing = bpy.context.scene.started_drawing
        built_plant = bpy.context.scene.built_plant
        
        if not started_drawing:
            row = layout.row()
            row.operator("view3d.gc_ot_start_drawing_operator", text="Start Drawing", icon="GREASEPENCIL")
        elif not built_plant:
            # Canvas Actions
            row = layout.row()
            row.label(text="Canvas:")

            row = layout.row()
            hide_show_icon = "HIDE_OFF" if bpy.context.scene.main_canvas_visible else "HIDE_ON"
            row.operator("view3d.gc_ot_main_canvas_hide_show", text="Hide / Show Canvas", icon=hide_show_icon)

            layout.separator()

            # Plant Generation Actions
            row = layout.row()
            row.label(text="Plant Generation:")

            # Brush size checkbox
            row = layout.row(align=True)
            row.prop(context.scene, "ignore_brush_size", text="Vary brush size naturally")

            # Build button
            row = layout.row(align=True)
            row.prop(context.scene, "model_type_selector", text="")
            row.separator(factor=0.5) 
            row.operator("mesh.gc_ot_build_plant", text="Build Plant").is_variation = False
            if len(bpy.context.scene.branch_collection.branches) > 0:
                row.enabled = True
            else:
                row.enabled = False
        else: 
            row = layout.row()
            row.operator("view3d.gc_ot_start_drawing_additional_operator", text="New Plant / Drawing", icon="GREASEPENCIL")

class GC_OT_start_drawing_operator(bpy.types.Operator):
    bl_idname = "view3d.gc_ot_start_drawing_operator"
    bl_label = "Start Drawing"
    bl_description = "Starts the drawing process"
    bl_options = {'REGISTER'}

    def execute(self, context):
        bpy.context.scene.panel_settings.active_tool = "BRANCH"
        bpy.context.scene.started_drawing = True
        bpy.context.scene.main_canvas_visible = True
        bpy.context.scene.built_plant = False
        set_branch_panel_active(True)

        bpy.ops.view3d.dp_ot_draw_main_canvas_operator('INVOKE_DEFAULT') # open main drawing canvas
        bpy.ops.view3d.dp_ot_draw_branch_slider_operator('INVOKE_DEFAULT') # open branch slider
        bpy.ops.view3d.dp_ot_draw_branch_shape_canvas_operator('INVOKE_DEFAULT') # open branch shape canvas
        bpy.ops.view3d.dp_ot_draw_leaf_curvature_type_canvas_operator('INVOKE_DEFAULT') # open leaf curvature type canvas
        bpy.ops.view3d.dp_ot_draw_lod_slider_operator("INVOKE_DEFAULT") # open lod slider

        return {'FINISHED'}

class GC_OT_start_drawing_additional_operator(bpy.types.Operator):
    bl_idname = "view3d.gc_ot_start_drawing_additional_operator"
    bl_label = "Start Drawing Again"
    bl_description = "Starts the drawing process again"
    bl_options = {'REGISTER'}

    def execute(self, context):
        bpy.context.scene.panel_settings.active_tool = "BRANCH"
        bpy.context.scene.built_plant = False
        bpy.context.scene.main_canvas_visible = True
        set_branch_panel_active(True)
        self.clear_previous_plant_variables()

        return {'FINISHED'}     
    
        
    def clear_previous_plant_variables(self):
        bpy.context.scene.branch_collection.branches.clear()
        bpy.context.scene.leaf_collection.leaves.clear()
        
        bpy.context.scene.branch_shape_canvas_settings.left_stroke.clear()
        bpy.context.scene.branch_shape_canvas_settings.right_stroke.clear()
        
        bpy.context.scene.leaf_curvature_type_canvas_settings.stroke.clear()
        
        bpy.context.scene.branch_slider_settings.brush_size = 4

classes = (
    GC_PT_actions_panel, 
    GC_OT_start_drawing_operator,
    GC_OT_start_drawing_additional_operator,
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


    