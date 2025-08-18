from ..bl_ui_widget import BL_UI_Widget

class BL_UI_Static_Panel(BL_UI_Widget):
    
    def __init__(self, x, y, width, height):
        super().__init__(x,y, width, height)
        
        self.widgets = []

    def set_location(self, x, y):
        super().set_location(x,y)
        self.layout_widgets()

    def add_widget(self, widget):
        self.widgets.append(widget)
        
    def add_widgets(self, widgets):
        self.widgets = widgets
        self.layout_widgets()
        
    def layout_widgets(self):
        for widget in self.widgets:
            if widget.region_type == "UI":
                widget.update_to_ui_scale()
            widget.update(self.x_screen + widget.x, self.y_screen + widget.y)   

    def child_widget_focused(self, x, y):
        for widget in self.widgets:
            if widget.is_in_rect(x, y):
                return True       
        return False
    
    def mouse_down(self, x, y):
        if self.child_widget_focused(x, y):
            return False
        
        if self.is_in_rect(x,y):
            return True
        
        return False

    def mouse_move(self, x, y):
        pass

    def mouse_up(self, x, y):
        pass