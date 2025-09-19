import bpy
import os

from .ui.bl_ui_draw_op import *
from .ui.canvas.bl_ui_leaf_panel_canvas import * 
from .ui.panels.bl_ui_static_panel import *
from .ui.components.bl_ui_button import *

from .bl_panel_active_tool import is_branch_panel_inactive

PANEL_BOUNDS = {"x": 20, "y": 172, "width": 160, "height": 65}

def clear_widgets_locals():
    return bpy.context.scene.built_plant

class DP_OT_draw_leaf_curvature_type_canvas_operator(BL_UI_OT_draw_operator):
    bl_idname = "view3d.dp_ot_draw_leaf_curvature_type_canvas_operator"
    bl_label = "Blender UI leaf curvature type canvas operator"
    bl_description = "Canvas for the leaf curvature type operator" 
    bl_options = {'REGISTER'}
    
    def on_invoke(self, context, event):
        self.region_type = "UI"
        self.is_operator_active = is_branch_panel_inactive
        self.clear_widgets_locals = clear_widgets_locals
            
        self.panel = BL_UI_Static_Panel(PANEL_BOUNDS["x"], PANEL_BOUNDS["y"], PANEL_BOUNDS["width"], PANEL_BOUNDS["height"])
        self.panel.region_type = self.region_type
        self.panel.bg_color = (0, 0, 0, 0)
        self.panel.outline_color = (0.576, 0.576, 0.576, 1)
        self.panel.outline_size = 3.0

        self.leaf_panel_canvas = BL_UI_Leaf_Panel_Canvas(0, 0, PANEL_BOUNDS["width"], PANEL_BOUNDS["height"])
        self.leaf_panel_canvas.region_type = self.region_type
        self.leaf_panel_canvas.brush_color = (0.576, 0.576, 0.576, 1)

        button_size = 17 if bpy.app.version[0] < 4 else 20
        self.clear_leaf_panel_canvas_button = BL_UI_Button(PANEL_BOUNDS["width"] - button_size - 7, PANEL_BOUNDS["height"] - button_size - 8, button_size, button_size)
        self.clear_leaf_panel_canvas_button.region_type = self.region_type
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
        
classes = (
    DP_OT_draw_leaf_curvature_type_canvas_operator,
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