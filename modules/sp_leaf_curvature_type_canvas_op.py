import bpy
import os

from .ui.bl_ui_draw_op import *
from .ui.canvas.bl_ui_leaf_panel_canvas import * 
from .ui.panels.bl_ui_static_panel import *
from .ui.components.bl_ui_button import *

from .properties import GC_PG_Stroke

from .bl_panels_op import is_branch_panel_inactive

PANEL_BOUNDS = {"x": 20, "y": 160, "width": 160, "height": 65}

class GC_PG_leaf_curvature_type_canvas_settings(bpy.types.PropertyGroup):
    stroke: bpy.props.PointerProperty(type=GC_PG_Stroke)
    x_norm_factor: bpy.props.FloatProperty(
        name="X Normalize Factor",
        default=0.0
    )
    y_norm_factor: bpy.props.FloatProperty(
        name="Y Normalize Factor",
        default=0.0
    )

class DP_OT_draw_leaf_curvature_type_canvas_operator(BL_UI_OT_draw_operator):
    bl_idname = "view3d.dp_ot_draw_leaf_curvature_type_canvas_operator"
    bl_label = "Blender UI leaf curvature type canvas operator"
    bl_description = "Canvas for the leaf curvature type operator" 
    bl_options = {'REGISTER'}
    
    def on_invoke(self, context, event):
        self.region_type = "UI"
            
        self.panel = BL_UI_Static_Panel(PANEL_BOUNDS["x"], PANEL_BOUNDS["y"], PANEL_BOUNDS["width"], PANEL_BOUNDS["height"])
        self.panel.region_type = self.region_type
        self.panel.is_widget_active = is_branch_panel_inactive
        self.panel.bg_color = (0, 0, 0, 0)
        self.panel.outline_color = (0.576, 0.576, 0.576, 1)
        self.panel.outline_size = 3.0

        self.leaf_panel_canvas = BL_UI_Leaf_Panel_Canvas(0, 0, PANEL_BOUNDS["width"], PANEL_BOUNDS["height"])
        self.leaf_panel_canvas.region_type = self.region_type
        self.leaf_panel_canvas.is_widget_active = is_branch_panel_inactive
        self.leaf_panel_canvas.brush_color = (0.576, 0.576, 0.576, 1)

        button_size = 17 if bpy.app.version[0] < 4 else 20
        self.clear_leaf_panel_canvas_button = BL_UI_Button(PANEL_BOUNDS["width"] - button_size - 7, PANEL_BOUNDS["height"] - button_size - 8, button_size, button_size)
        self.clear_leaf_panel_canvas_button.region_type = self.region_type
        self.clear_leaf_panel_canvas_button.is_widget_active = is_branch_panel_inactive
        self.clear_leaf_panel_canvas_button.bg_color = (0, 0, 0, 0)
        self.clear_leaf_panel_canvas_button.hover_bg_color = (0, 0, 0, 0)
        self.clear_leaf_panel_canvas_button.select_bg_color = (0, 0, 0, 0)
        addon_dir = os.path.dirname(__file__)
        addon_root = os.path.dirname(addon_dir) if "modules" in addon_dir else addon_dir
        icon_path = os.path.join(addon_root, "icons", "clear.png")
        self.clear_leaf_panel_canvas_button.set_image(icon_path)
        self.clear_leaf_panel_canvas_button.set_image_size((button_size,button_size))
        self.clear_leaf_panel_canvas_button.set_image_position((1,1))
        self.clear_leaf_panel_canvas_button.text = ""
        self.clear_leaf_panel_canvas_button.set_mouse_down(self.leaf_panel_canvas.clear)

        # Add new widgets here
        widgets_panel = [self.leaf_panel_canvas, self.clear_leaf_panel_canvas_button]
        widgets =       [self.panel]

        widgets += widgets_panel

        self.init_widgets(context, widgets)

        self.panel.add_widgets(widgets_panel)

class GC_OT_no_leaf_curvature_type_popup(bpy.types.Operator):
    bl_idname = "gc.no_leaf_curvature_type_popup"
    bl_label = "Missing Leaf Curvature Type"
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
    bl_label = "Missing Branches"
    bl_description = "You need to draw at least one branch before drawing leaves."

    def draw(self, context):
        layout = self.layout
        layout.label(text="You need to draw at least one branch before drawing leaves.")

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
        
def register():
    bpy.utils.register_class(DP_OT_draw_leaf_curvature_type_canvas_operator)
    bpy.utils.register_class(GC_OT_no_leaf_curvature_type_popup)
    bpy.utils.register_class(GC_OT_no_branches_popup)
    bpy.utils.register_class(GC_PG_leaf_curvature_type_canvas_settings)
    bpy.types.Scene.leaf_curvature_type_canvas_settings = bpy.props.PointerProperty(type=GC_PG_leaf_curvature_type_canvas_settings)

def unregister():  
    del bpy.types.Scene.leaf_curvature_type_canvas_settings
    bpy.utils.unregister_class(DP_OT_draw_leaf_curvature_type_canvas_operator)
    bpy.utils.unregister_class(GC_OT_no_leaf_curvature_type_popup)
    bpy.utils.unregister_class(GC_OT_no_branches_popup)
    bpy.utils.unregister_class(GC_PG_leaf_curvature_type_canvas_settings)
