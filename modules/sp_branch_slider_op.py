import bpy

from .ui.components.bl_ui_slider import * 
from .ui.bl_ui_draw_op import *
from .ui.panels.bl_ui_static_panel import *

from .bl_panel_active_tool import is_branch_panel_active

if bpy.app.version[0] < 4:
    PANEL_BOUNDS = {"x": 15, "y": 155, "width": 170, "height": 50}
else:
    PANEL_BOUNDS = {"x": 15, "y": 110, "width": 170, "height": 50}

SLIDER_BOUNDS = {"x": 5, "y": 20, "width": PANEL_BOUNDS["width"] - 10, "height": PANEL_BOUNDS["height"] - 20}

def clear_widgets_locals():
    return bpy.context.scene.built_plant

class DP_OT_draw_branch_slider_operator(BL_UI_OT_draw_operator):
    bl_idname = "view3d.dp_ot_draw_branch_slider_operator"
    bl_label = "Blender UI branch slider operator"
    bl_description = "Custom slider operator" 
    bl_options = {'REGISTER'}

    def on_invoke(self, context, event):
        self.region_type = "UI"
        self.is_operator_active = is_branch_panel_active
        self.clear_widgets_locals = clear_widgets_locals
            
        self.panel = BL_UI_Static_Panel(PANEL_BOUNDS["x"], PANEL_BOUNDS["y"], PANEL_BOUNDS["width"], PANEL_BOUNDS["height"])
        self.panel.region_type = self.region_type
        self.panel.bg_color = (0, 0, 0, 0)

        self.slider = BL_UI_Slider(SLIDER_BOUNDS["x"], SLIDER_BOUNDS["y"], SLIDER_BOUNDS["width"], SLIDER_BOUNDS["height"])
        self.slider.color= (0.69, 0.937, 0.69, 0.8)
        self.slider.hover_color = (0.69, 0.937, 0.69, 1.0)
        self.slider.min = 1
        self.slider.max = 5
        self.slider.set_value(4)
        self.slider.decimals = 0
        self.slider.show_min_max = False
        self.slider.set_value_change(self.on_slider_value_change)

        self.slider.region_type = self.region_type

        # Add new widgets here
        widgets_panel = [self.slider]
        widgets =       [self.panel]

        widgets += widgets_panel

        self.init_widgets(context, widgets)

        self.panel.add_widgets(widgets_panel)

    def on_slider_value_change(self, slider, value):
        bpy.context.scene.branch_slider_settings.brush_size = int(value)
        
classes = (
    DP_OT_draw_branch_slider_operator,
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

