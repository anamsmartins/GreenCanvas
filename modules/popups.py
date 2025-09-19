import bpy

class GC_OT_existing_leaves_popup(bpy.types.Operator):
    bl_idname = "gc.existing_leaves_popup"
    bl_label = "Existing leaves"
    bl_description = "You can only clear all branches once no leaves exist."

    def draw(self, context):
        layout = self.layout
        layout.label(text="You can only clear all branches once no leaves exist.")

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
    
class GC_OT_no_leaf_curvature_type_popup(bpy.types.Operator):
    bl_idname = "gc.no_leaf_curvature_type_popup"
    bl_label = "Missing leaf curvature type"
    bl_description = "You need to draw a leaf curvature type before drawing leaves."

    def draw(self, context):
        layout = self.layout
        layout.label(text="You need to draw a leaf curvature type before drawing leaves.")

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
    
class GC_OT_no_branches_popup(bpy.types.Operator):
    bl_idname = "gc.no_branches_popup"
    bl_label = "Missing branches"
    bl_description = "You need to draw at least one branch before drawing leaves."

    def draw(self, context):
        layout = self.layout
        layout.label(text="You need to draw at least one branch before drawing leaves.")

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
    
class GC_OT_incomplete_branch_shape_popup(bpy.types.Operator):
    bl_idname = "gc.incomplete_branch_shape_popup"
    bl_label = "Incomplete branch shape"
    bl_description = "You've started a branch shape, but it's incomplete. Complete it with a second stroke or remove it."

    def draw(self, context):
        layout = self.layout
        layout.label(text="You've started a branch shape, but it's incomplete. Complete it with a second stroke or remove it.")

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

class GC_OT_no_object_selected_popup(bpy.types.Operator):
    bl_idname = "gc.no_object_selected_popup"
    bl_label = "No object selected"
    bl_description = "For this operation you need to select an object first."

    def draw(self, context):
        layout = self.layout
        layout.label(text="For this operation you need to select an object first.")

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
    
class GC_OT_no_branch_selected_popup(bpy.types.Operator):
    bl_idname = "gc.no_branch_selected_popup"
    bl_label = "No branch selected"
    bl_description = "For this operation you need to select a branch first."

    def draw(self, context):
        layout = self.layout
        layout.label(text="For this operation you need to select a branch first.")

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

class GC_OT_selected_branch_needs_leaves_popup(bpy.types.Operator):
    bl_idname = "gc.selected_branch_needs_leaves_popup"
    bl_label = "Seletec branch needs leaves"
    bl_description = "For this operation the selected branch needs at least one leaf."

    def draw(self, context):
        layout = self.layout
        layout.label(text="For this operation the selected branch needs at least one leaf.")

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


classes = (
    GC_OT_existing_leaves_popup,
    GC_OT_no_leaf_curvature_type_popup,
    GC_OT_no_branches_popup,
    GC_OT_incomplete_branch_shape_popup,
    GC_OT_no_object_selected_popup,
    GC_OT_no_branch_selected_popup,
    GC_OT_selected_branch_needs_leaves_popup,
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