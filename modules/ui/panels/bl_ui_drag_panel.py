from ..bl_ui_widget import BL_UI_Widget
from .bl_ui_drag_header import BL_UI_Drag_Header
from ..components.bl_ui_image import BL_UI_Image

class BL_UI_Drag_Panel(BL_UI_Widget):
    
    def __init__(self, x, y, width, height):
        super().__init__(x,y, width, height)
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        self.is_drag = False
        self.widgets = []
        self.has_drag_header = False

    def set_location(self, x, y):
        super().set_location(x,y)
        self.layout_widgets()
    
    def set_hide_panel(self, hide_panel_func):
        self.hide_panel_func = hide_panel_func

    def add_widget(self, widget):
        self.widgets.append(widget)
        
    def add_widgets(self, widgets):
        self.widgets = widgets
        self.layout_widgets()
        
    def layout_widgets(self):
        for widget in self.widgets:
            widget.update(self.x_screen + widget.x, self.y_screen + widget.y)   
    
    def update(self, x, y):
        super().update(x - self.drag_offset_x, y + self.drag_offset_y)
    
    def child_widget_focused(self, x, y):
        for widget in self.widgets:
            if widget.is_in_rect(x, y):
                # if drag header then set drag
                if isinstance(widget, BL_UI_Drag_Header):
                    if not widget.child_widget_focused(x, y):
                        height = self.get_area_height()
                        self.is_drag = True
                        self.drag_offset_x = x - self.x_screen
                        self.drag_offset_y = y - (height - self.y_screen)
                elif isinstance(widget, BL_UI_Image):
                    return False
                return True       
        return False
    
    def mouse_down(self, x, y):
        if self.child_widget_focused(x, y):
            return False
        
        if self.is_in_rect(x,y):
            # only set drag if it doesn't contain a drag header
            if not self.has_drag_header:
                height = self.get_area_height()
                self.is_drag = True
                self.drag_offset_x = x - self.x_screen
                self.drag_offset_y = y - (height - self.y_screen)
                
            return True
        try:
            self.hide_panel_func()
        except:
            return False

    def mouse_move(self, x, y):
        if self.is_drag:
            area_height = self.get_area_height()
            area_width = self.get_area_width()

            new_x = x - self.drag_offset_x
            new_y = (self.get_area_height() - y) + self.drag_offset_y

            new_x = max(0, min(new_x, area_width - self.width))
            new_y = max(0, min(new_y, area_height - self.height))

            self.update(new_x + self.drag_offset_x, new_y - self.drag_offset_y)
            self.layout_widgets()

    def mouse_up(self, x, y):
        self.is_drag = False
        self.drag_offset_x = 0
        self.drag_offset_y = 0