bl_info = {
    "name": "GreenCanvas",
    "author": "",
    "version": (1, 0),
    "location": "View3D > Tool > GreenCanvas",
    "description": "GreenCanvas description",
    "warning": "",
    "wiki_url": "",
    "category": "GreenCanvas",
}

import logging
import os
import bpy
from bpy.props import *

from .modules.bl_icons import load_icons, unload_icons
from .modules.properties import register as properties_register, unregister as properties_unregister
from .modules.bl_panels_op import register as bl_panels_register, unregister as bl_panels_unregister
from .modules.dp_main_canvas_op import register as dp_main_canvas_op_register, unregister as dp_main_canvas_op_unregister
from .modules.sp_branch_slider_op import register as sp_branch_slider_op_register, unregister as sp_branch_slider_op_unregister
from .modules.sp_branch_shape_canvas_op import register as sp_branch_shape_canvas_op_register, unregister as sp_branch_shape_canvas_op_unregister
from .modules.sp_leaf_curvature_type_canvas_op import register as sp_leaf_curvature_type_canvas_op_register, unregister as sp_leaf_curvature_type_canvas_op_unregister

preview_collections = {} # Icons 

# Logging setup
def setup_logging():
    log_file = os.path.join(os.path.dirname(__file__), "log.txt")
    logging.basicConfig(
        filename=log_file,
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logging.getLogger().setLevel(logging.DEBUG)
    logging.info("Logging initialized") # print("cat") == logging.info("Cat")
    bpy.app.debug_wm  = True

def register():
    #setup_logging()

    # Icons
    preview_collections["main"] = load_icons()
    bpy.types.Scene.preview_collections = preview_collections

    # Properties
    properties_register()
    
    # UI
    bl_panels_register()
    dp_main_canvas_op_register()
    sp_branch_slider_op_register()
    sp_branch_shape_canvas_op_register()
    sp_leaf_curvature_type_canvas_op_register()


def unregister():

    # Icons
    del bpy.types.Scene.preview_collections
    unload_icons()

    # Properties
    properties_unregister()
    
    # UI
    bl_panels_unregister()
    dp_main_canvas_op_unregister()
    sp_branch_slider_op_unregister()
    sp_branch_shape_canvas_op_unregister()
    sp_leaf_curvature_type_canvas_op_unregister()

# if __name__ == "__main__":
#     register()

# REMOVE WHEN DEPLOY
register()