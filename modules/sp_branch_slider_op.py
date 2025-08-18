import bpy

from .ui.components.bl_ui_slider import * 
from .ui.bl_ui_draw_op import *
from .ui.panels.bl_ui_static_panel import *

from .bl_panels_op import is_branch_panel_active

PANEL_BOUNDS = {"x": 15, "y": 145, "width": 170, "height": 50}
SLIDER_BOUNDS = {"x": 5, "y": 20, "width": PANEL_BOUNDS["width"] - 10, "height": PANEL_BOUNDS["height"] - 20}

class GC_PG_branch_slider_settings(bpy.types.PropertyGroup):
    brush_size: bpy.props.IntProperty(
        name="Branch slider brush size value",
        default=3,
        min=1,
        max=5,
    )

class DP_OT_draw_branch_slider_operator(BL_UI_OT_draw_operator):
    bl_idname = "view3d.dp_ot_draw_branch_slider_operator"
    bl_label = "Blender UI branch slider operator"
    bl_description = "Custom slider operator" 
    bl_options = {'REGISTER'}

    def on_invoke(self, context, event):
        self.region_type = "UI"
            
        self.panel = BL_UI_Static_Panel(PANEL_BOUNDS["x"], PANEL_BOUNDS["y"], PANEL_BOUNDS["width"], PANEL_BOUNDS["height"])
        self.panel.region_type = self.region_type
        self.panel.bg_color = (0, 0, 0, 0)
        self.panel.is_widget_active = is_branch_panel_active

        self.slider = BL_UI_Slider(SLIDER_BOUNDS["x"], SLIDER_BOUNDS["y"], SLIDER_BOUNDS["width"], SLIDER_BOUNDS["height"])
        self.slider.color= (0.69, 0.937, 0.69, 0.8)
        self.slider.hover_color = (0.69, 0.937, 0.69, 1.0)
        self.slider.min = 1
        self.slider.max = 5
        self.slider.set_value(3)
        self.slider.decimals = 0
        self.slider.show_min_max = False
        self.slider.set_value_change(self.on_slider_value_change)

        self.slider.region_type = self.region_type
        self.slider.is_widget_active = is_branch_panel_active

        # Add new widgets here
        widgets_panel = [self.slider]
        widgets =       [self.panel]

        widgets += widgets_panel

        self.init_widgets(context, widgets)

        self.panel.add_widgets(widgets_panel)

    def on_slider_value_change(self, slider, value):
        bpy.context.scene.branch_slider_settings.brush_size = int(value)
        
def register():
    bpy.utils.register_class(DP_OT_draw_branch_slider_operator)
    bpy.utils.register_class(GC_PG_branch_slider_settings)
    bpy.types.Scene.branch_slider_settings = bpy.props.PointerProperty(type=GC_PG_branch_slider_settings)

def unregister():  
    del bpy.types.Scene.branch_slider_settings
    bpy.utils.unregister_class(DP_OT_draw_branch_slider_operator)
    bpy.utils.unregister_class(GC_PG_branch_slider_settings)
