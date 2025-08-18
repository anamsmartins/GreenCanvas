import bpy

from bpy.types import Operator

class BL_UI_OT_draw_operator(Operator):
    bl_idname = "view3d.bl_ui_ot_draw_operator"
    bl_label = "bl ui widgets operator"
    bl_description = "Operator for bl ui widgets" 
    bl_options = {'REGISTER'}
    	
    @property
    def region_type(self):
        return self._region_type

    @region_type.setter
    def region_type(self, value):
        if value in ["WINDOW", "UI"]:
            self._region_type  = value

    def init_widgets(self, context, widgets):
        self.widgets = widgets
        for widget in self.widgets:
            widget.init(context)

    def on_invoke(self, context, event):
        pass

    def on_finish(self, context):
        self._finished = True

    def invoke(self, context, event):
        self.draw_handle = None
        self.draw_event  = None
        self._finished = False
        self._region_type = "WINDOW"
                
        self.widgets = []

        self.on_invoke(context, event)

        args = (self, context)
        self.register_handlers(args, context)
                   
        context.window_manager.modal_handler_add(self)

        return {"RUNNING_MODAL"}
    
    def register_handlers(self, args, context):
        self.draw_handle = bpy.types.SpaceView3D.draw_handler_add(self.draw_callback_px, args, self._region_type, "POST_PIXEL")
        self.draw_event = context.window_manager.event_timer_add(0.1, window=context.window)
        
    def unregister_handlers(self, context):
        
        context.window_manager.event_timer_remove(self.draw_event)
        
        bpy.types.SpaceView3D.draw_handler_remove(self.draw_handle, self.region_type)
        
        self.draw_handle = None
        self.draw_event  = None
        
    def handle_widget_events(self, event):
        result = False
        for widget in self.widgets:
            if widget.handle_event(event):
                result = True
        return result
          
    def modal(self, context, event):

        if self._finished:
            self.finish()
            return {'FINISHED'}

        if context.area:
            context.area.tag_redraw()
        
        if self.handle_widget_events(event):
            return {'RUNNING_MODAL'}   
                    
        return {"PASS_THROUGH"}
                                
    def finish(self):
        self.unregister_handlers(bpy.context)
        self.on_finish(bpy.context)
		
	# Draw handler to paint onto the screen
    def draw_callback_px(self, op, context):
        for widget in self.widgets:
            widget.draw()