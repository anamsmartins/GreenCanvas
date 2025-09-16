import bpy
import os

from .ui.bl_ui_draw_op import *
from .ui.panels.bl_ui_drag_panel import *
from .ui.components.bl_ui_image import *

PANEL_BOUNDS = {"x": 0, "y": 0, "width": 400, "height": 250}

class DP_OT_instructions_video_operator(BL_UI_OT_draw_operator):
    bl_idname = "view3d.dp_ot_instructions_video_operator"
    bl_label = "Blender UI instructions video panel operator"
    bl_description = "Blender UI instructions video panel operator" 
    bl_options = {'REGISTER'}

    def on_invoke(self, context, event):

        self.panel = BL_UI_Drag_Panel(PANEL_BOUNDS["x"], PANEL_BOUNDS["y"], PANEL_BOUNDS["width"], PANEL_BOUNDS["height"])
        self.panel.bg_color = (0.264, 0.264, 0.264, 0.9)
        self.panel.has_drag_header = False
        self.panel.set_hide_panel(self.on_hide_panel)

        self.image = BL_UI_Image(0, 0, PANEL_BOUNDS["width"], PANEL_BOUNDS["height"])
        addon_dir = os.path.dirname(__file__)
        addon_root = os.path.dirname(addon_dir) if "modules" in addon_dir else addon_dir
        image_path = os.path.join(addon_root, "images", "gc_instructions_video.png")
        self.image.set_image(image_path)

        widgets_panel = [self.image]
        widgets =       [self.panel]

        widgets += widgets_panel

        self.init_widgets(context, widgets)

        self.panel.add_widgets(widgets_panel)

        self.panel.set_location((context.area.width / 2) - (PANEL_BOUNDS["width"] / 2), 
                                (context.area.height / 2) - (PANEL_BOUNDS["height"] / 2))
    
    def on_hide_panel(self):
        self.finish()

classes = (
    DP_OT_instructions_video_operator,
)
        
def register():
    for cls in classes:
        if not hasattr(bpy.types, cls.__name__):
            bpy.utils.register_class(cls)

def unregister():  
    for cls in reversed(classes):
        if hasattr(bpy.types, cls.__name__):
            bpy.utils.unregister_class(cls)
