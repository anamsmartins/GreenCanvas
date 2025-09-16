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

# REMOVE WHEN DEPLOY
import site
site.addsitedir("/home/uwuntu/.local/lib/python3.10/site-packages")

import logging
import os
import bpy
from bpy.props import *

from .modules.bl_icons import load_icons, unload_icons
from .modules.properties import register as properties_register, unregister as properties_unregister
from .modules.bl_panel_active_tool import register as bl_panel_active_tool_register, unregister as bl_panel_active_tool_unregister
from .modules.bl_panel_properties import register as bl_panel_properties_register, unregister as bl_panel_properties_unregister
from .modules.bl_panel_actions import register as bl_panel_actions_register, unregister as bl_panel_actions_unregister
from .modules.bl_panel_info import register as bl_panel_info_register, unregister as bl_panel_info_unregister
from .modules.dp_main_canvas_op import register as dp_main_canvas_op_register, unregister as dp_main_canvas_op_unregister
from .modules.sp_branch_slider_op import register as sp_branch_slider_op_register, unregister as sp_branch_slider_op_unregister
from .modules.sp_branch_shape_canvas_op import register as sp_branch_shape_canvas_op_register, unregister as sp_branch_shape_canvas_op_unregister
from .modules.sp_leaf_curvature_type_canvas_op import register as sp_leaf_curvature_type_canvas_op_register, unregister as sp_leaf_curvature_type_canvas_op_unregister
from .modules.build_plant_op import register as build_plant_op_register, unregister as build_plant_op_unregister
from .modules.sp_lod_slider_op import register as sp_lod_slider_op_register, unregister as sp_lod_slider_op_unregister
from .modules.popups import register as popup_register, unregister as popup_unregister
from .modules.dp_instructions_info_op import register as dp_instructions_info_op_register, unregister as dp_instructions_info_op_unregister
from .modules.dp_instructions_video_op import register as dp_instructions_video_op_register, unregister as dp_instructions_video_op_unregister
from .modules.propagate_leaves import register as propagate_leaves_register, unregister as propagate_leaves_unregister
from .modules.dp_building_plant_op import register as dp_building_plant_op_register, unregister as dp_building_plant_op_unregister

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

    # Popups
    popup_register()
    
    # UI
    dp_main_canvas_op_register()
    dp_building_plant_op_register()
    
    sp_branch_slider_op_register()
    sp_branch_shape_canvas_op_register()
    sp_leaf_curvature_type_canvas_op_register()
    bl_panel_active_tool_register()

    sp_lod_slider_op_register()
    propagate_leaves_register()
    bl_panel_properties_register()
    
    build_plant_op_register()
    bl_panel_actions_register()

    dp_instructions_info_op_register()
    dp_instructions_video_op_register()
    bl_panel_info_register()


def unregister():

    # Icons
    del bpy.types.Scene.preview_collections
    unload_icons()

    # Properties
    properties_unregister()
    
    # Popups
    popup_unregister()

    # UI
    dp_main_canvas_op_unregister()
    dp_building_plant_op_unregister()
    
    sp_branch_slider_op_unregister()
    sp_branch_shape_canvas_op_unregister()
    sp_leaf_curvature_type_canvas_op_unregister()
    bl_panel_active_tool_unregister()

    sp_lod_slider_op_unregister()
    propagate_leaves_unregister()
    bl_panel_properties_unregister()
    
    build_plant_op_unregister()
    bl_panel_actions_unregister()

    dp_instructions_info_op_unregister()
    dp_instructions_video_op_unregister()
    bl_panel_info_unregister()

# if __name__ == "__main__":
#     register()

# REMOVE WHEN DEPLOY
register()