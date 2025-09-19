import bpy

from .ui.components.bl_ui_slider import * 
from .ui.bl_ui_draw_op import *
from .ui.panels.bl_ui_static_panel import *
from ..modules.bl_panel_properties import is_properties_panel_active
from ..modules.popups import GC_OT_no_object_selected_popup

PANEL_BOUNDS = {"x": 15, "y": 110, "width": 170, "height": 50}
SLIDER_BOUNDS = {"x": 5, "y": 20, "width": PANEL_BOUNDS["width"] - 10, "height": PANEL_BOUNDS["height"] - 20}

def clear_widgets_locals():
    return not bpy.context.scene.built_plant

class DP_OT_draw_lod_slider_operator(BL_UI_OT_draw_operator):
    bl_idname = "view3d.dp_ot_draw_lod_slider_operator"
    bl_label = "Blender UI Level of Detail slider operator"
    bl_description = "Custom slider operator" 
    bl_options = {'REGISTER'}

    def on_invoke(self, context, event):
        self.region_type = "UI"
        self.is_operator_active = is_properties_panel_active
        self.clear_widgets_locals = clear_widgets_locals
            
        self.panel = BL_UI_Static_Panel(PANEL_BOUNDS["x"], PANEL_BOUNDS["y"], PANEL_BOUNDS["width"], PANEL_BOUNDS["height"])
        self.panel.region_type = self.region_type
        self.panel.bg_color = (0, 0, 0, 0)

        self.slider = BL_UI_Slider(SLIDER_BOUNDS["x"], SLIDER_BOUNDS["y"], SLIDER_BOUNDS["width"], SLIDER_BOUNDS["height"])
        self.slider.color= (0.69, 0.937, 0.69, 0.8)
        self.slider.hover_color = (0.69, 0.937, 0.69, 1.0)
        self.slider.min = 1
        self.slider.max = 5
        self.slider.set_value(5)
        self.slider.decimals = 0
        self.slider.show_min_max = False
        self.slider.set_value_change(self.on_slider_value_change)
        self.slider.set_on_mouse_down_popup(self.on_mouse_down_popup)
        self.slider.region_type = self.region_type

        # Add new widgets here
        widgets_panel = [self.slider]
        widgets =       [self.panel]

        widgets += widgets_panel

        self.init_widgets(context, widgets)

        self.panel.add_widgets(widgets_panel)

        self.original_mesh = None


    def on_slider_value_change(self, slider, value):
        obj = bpy.context.active_object
        if obj is None or obj.type != 'MESH':
            return

        dec = obj.modifiers.get('Decimate')
        if dec is None:
            return
        
        if value == 5:
            dec.show_viewport = False 
            return

        dec.show_viewport = True
        dec.ratio = value * 0.05

    def on_mouse_down_popup(self):
        obj = bpy.context.active_object
        if obj is None or obj.type != 'MESH':        
            bpy.context.window_manager.popup_menu(
                GC_OT_no_object_selected_popup.draw,
                    title=GC_OT_no_object_selected_popup.bl_label,
                    icon='INFO'
            )
            return False

        return True

classes = (
    DP_OT_draw_lod_slider_operator,
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

