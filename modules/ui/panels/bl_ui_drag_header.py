from ..bl_ui_widget import *

class BL_UI_Drag_Header(BL_UI_Widget):
    
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)

        self.widgets = []

    def add_widget(self, widget):
        self.widgets.append(widget)
        
    def add_widgets(self, widgets):
        self.widgets = widgets
        self.layout_widgets()
        
    def layout_widgets(self):
        for widget in self.widgets:
            widget.update(self.x_screen + widget.x, self.y_screen + widget.y)   
    
    def update(self, x, y):
        super().update(x, y)
        self.layout_widgets()
    
    def child_widget_focused(self, x, y):
        for widget in self.widgets:
            if widget.is_in_rect(x, y):
                return True       
        return False