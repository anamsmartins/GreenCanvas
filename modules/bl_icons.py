import bpy.utils.previews
import os

preview_collections = {}

def load_icons():
    pcoll = bpy.utils.previews.new()
    
    icons_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "icons")

    pcoll.load("branch-active-icon", os.path.join(icons_dir, "branch-active.png"), 'IMAGE')
    pcoll.load("branch-inactive-icon", os.path.join(icons_dir, "branch-inactive.png"), 'IMAGE')
    pcoll.load("leaf-active-icon", os.path.join(icons_dir, "leaf-active.png"), 'IMAGE')
    pcoll.load("leaf-inactive-icon", os.path.join(icons_dir, "leaf-inactive.png"), 'IMAGE')
    pcoll.load("undo-icon", os.path.join(icons_dir, "undo.png"), 'IMAGE')
    pcoll.load("clear-icon", os.path.join(icons_dir, "clear.png"), 'IMAGE')

    preview_collections["main"] = pcoll

    return pcoll

def unload_icons():
    for pcoll in preview_collections.values():
        bpy.utils.previews.remove(pcoll)
    preview_collections.clear()
