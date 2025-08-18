import bpy

from .ui.bl_ui_draw_op import *
from .ui.panels.bl_ui_drag_panel import *
from .ui.panels.bl_ui_drag_header import *
from .ui.canvas.bl_ui_main_canvas import *

PANEL_BOUNDS = {"x": 0, "y": 0, "width": 700, "height": 700}
HEADER_BOUNDS = {"x": 0, "y": 0, "width": PANEL_BOUNDS["width"], "height": 30}
CANVAS_BOUNDS = {"x": 0, "y": HEADER_BOUNDS["height"], "width": PANEL_BOUNDS["width"], "height": PANEL_BOUNDS["width"] - HEADER_BOUNDS["height"]}

main_canvas = None

class DP_OT_draw_main_canvas_operator(BL_UI_OT_draw_operator):
    bl_idname = "view3d.dp_ot_draw_main_canvas_operator"
    bl_label = "Blender UI main canvas operator"
    bl_description = "Main drawing canvas operator, where the user draws the plant sketch (branches & leaves)" 
    bl_options = {'REGISTER'}

    def on_invoke(self, context, event):

        self.panel = BL_UI_Drag_Panel(PANEL_BOUNDS["x"], PANEL_BOUNDS["y"], PANEL_BOUNDS["width"], PANEL_BOUNDS["height"])
        self.panel.bg_color = (0.921, 0.984, 0.933, 0.2)
        self.panel.has_drag_header = True

        self.header = BL_UI_Drag_Header(HEADER_BOUNDS["x"], HEADER_BOUNDS["y"], HEADER_BOUNDS["width"], HEADER_BOUNDS["height"])
        self.header.bg_color = (0.264, 0.264, 0.264, 1)

        self.canvas = BL_UI_Main_Canvas(CANVAS_BOUNDS["x"], CANVAS_BOUNDS["y"], CANVAS_BOUNDS["width"], CANVAS_BOUNDS["height"])
        
        global main_canvas 
        main_canvas = self.canvas

        widgets_panel = [self.header, self.canvas]
        widgets =       [self.panel]

        widgets += widgets_panel

        self.init_widgets(context, widgets)

        self.panel.add_widgets(widgets_panel)

        self.panel.set_location((context.area.width / 2) - (PANEL_BOUNDS["width"] / 2), 
                                (context.area.height / 2) - (PANEL_BOUNDS["height"] / 2))

class GC_OT_main_canvas_undo(bpy.types.Operator):
    bl_idname = "view3d.gc_ot_main_canvas_undo"
    bl_label = "Undo Main Canvas Stroke"
    bl_description = "Undo last stroke of the active tool in the main canvas"

    def execute(self, context):
        global main_canvas
        if main_canvas:
            main_canvas.undo()

        return {'FINISHED'}
    
class GC_OT_main_canvas_clear(bpy.types.Operator):
    bl_idname = "view3d.gc_ot_main_canvas_clear"
    bl_label = "Clear all strokes of the active tool"
    bl_description = "Clear all strokes of the active tool in the main canvas"

    def execute(self, context):
        global main_canvas
        if main_canvas:
            main_canvas.clear()

        return {'FINISHED'}
    
    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)
        
        
def register():
    bpy.utils.register_class(DP_OT_draw_main_canvas_operator)
    bpy.utils.register_class(GC_OT_main_canvas_undo)
    bpy.utils.register_class(GC_OT_main_canvas_clear)

def unregister():  
    bpy.utils.unregister_class(DP_OT_draw_main_canvas_operator)
    bpy.utils.unregister_class(GC_OT_main_canvas_undo)
    bpy.utils.unregister_class(GC_OT_main_canvas_clear)
