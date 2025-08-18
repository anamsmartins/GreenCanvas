import bpy
import os

from .ui.bl_ui_draw_op import *
from .ui.canvas.bl_ui_branch_panel_canvas import * 
from .ui.panels.bl_ui_static_panel import *
from .ui.components.bl_ui_button import *

from .properties import GC_PG_Stroke

from .bl_panels_op import is_branch_panel_active

PANEL_BOUNDS = {"x": 20, "y": 230, "width": 160, "height": 65}

class GC_PG_branch_shape_canvas_settings(bpy.types.PropertyGroup):
    strokes: bpy.props.CollectionProperty(type=GC_PG_Stroke)
    x_norm_factor: bpy.props.FloatProperty(
        name="X Normalize Factor",
        default=0.0
    )
    y_norm_factor: bpy.props.FloatProperty(
        name="Y Normalize Factor",
        default=0.0
    )

class DP_OT_draw_branch_shape_canvas_operator(BL_UI_OT_draw_operator):
    bl_idname = "view3d.dp_ot_draw_branch_shape_canvas_operator"
    bl_label = "Blender UI branch shape canvas operator"
    bl_description = "Canvas for the branch shape operator" 
    bl_options = {'REGISTER'}

    def on_invoke(self, context, event):
        self.region_type = "UI"
            
        self.panel = BL_UI_Static_Panel(PANEL_BOUNDS["x"], PANEL_BOUNDS["y"], PANEL_BOUNDS["width"], PANEL_BOUNDS["height"])
        self.panel.region_type = self.region_type
        self.panel.is_widget_active = is_branch_panel_active
        self.panel.bg_color = (0, 0, 0, 0)
        self.panel.outline_color = (0.576, 0.576, 0.576, 1)
        self.panel.outline_size = 3.0

        self.branch_panel_canvas = BL_UI_Branch_Panel_Canvas(0, 0, PANEL_BOUNDS["width"], PANEL_BOUNDS["height"])
        self.branch_panel_canvas.region_type = self.region_type
        self.branch_panel_canvas.is_widget_active = is_branch_panel_active
        self.branch_panel_canvas.brush_color = (0.576, 0.576, 0.576, 1)

        button_size = 17 if bpy.app.version[0] < 4 else 20
        self.clear_branch_panel_canvas_button = BL_UI_Button(PANEL_BOUNDS["width"] - button_size - 7 , PANEL_BOUNDS["height"] - button_size - 8, button_size, button_size)
        self.clear_branch_panel_canvas_button.region_type = self.region_type
        self.clear_branch_panel_canvas_button.is_widget_active = is_branch_panel_active
        self.clear_branch_panel_canvas_button.bg_color = (0, 0, 0, 0)
        self.clear_branch_panel_canvas_button.hover_bg_color = (0, 0, 0, 0)
        self.clear_branch_panel_canvas_button.select_bg_color = (0, 0, 0, 0)
        addon_dir = os.path.dirname(__file__)
        addon_root = os.path.dirname(addon_dir) if "modules" in addon_dir else addon_dir
        icon_path = os.path.join(addon_root, "icons", "clear.png")
        self.clear_branch_panel_canvas_button.set_image(icon_path)
        self.clear_branch_panel_canvas_button.set_image_size((button_size,button_size))
        self.clear_branch_panel_canvas_button.set_image_position((1,1))
        self.clear_branch_panel_canvas_button.text = ""
        self.clear_branch_panel_canvas_button.set_mouse_down(self.branch_panel_canvas.clear)

        # Add new widgets here
        widgets_panel = [self.branch_panel_canvas, self.clear_branch_panel_canvas_button]
        widgets =       [self.panel]

        widgets += widgets_panel

        self.init_widgets(context, widgets)

        self.panel.add_widgets(widgets_panel)

class GC_OT_incomplete_branch_shape_popup(bpy.types.Operator):
    bl_idname = "gc.incomplete_branch_shape"
    bl_label = "Incomplete Branch Shape"
    bl_description = "You've started a branch shape, but it's incomplete. Complete it with a second stroke or remove it."

    def draw(self, context):
        layout = self.layout
        layout.label(text="You've started a branch shape, but it's incomplete. Complete it with a second stroke or remove it.")

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
        
def register():
    bpy.utils.register_class(DP_OT_draw_branch_shape_canvas_operator)
    bpy.utils.register_class(GC_PG_branch_shape_canvas_settings)
    bpy.utils.register_class(GC_OT_incomplete_branch_shape_popup)
    bpy.types.Scene.branch_shape_canvas_settings = bpy.props.PointerProperty(type=GC_PG_branch_shape_canvas_settings)

def unregister():  
    del bpy.types.Scene.branch_shape_canvas_settings
    bpy.utils.unregister_class(DP_OT_draw_branch_shape_canvas_operator)
    bpy.utils.unregister_class(GC_PG_branch_shape_canvas_settings)
    bpy.utils.unregister_class(GC_OT_incomplete_branch_shape_popup)
