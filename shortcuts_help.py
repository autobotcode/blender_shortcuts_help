bl_info = {
    "name": "Shortcuts Help",
    "description": "Displays a list of shortcuts in a popup, categorized by Blender's areas. Shortcuts are OS-specific.",
    "author": "John Gilbey",
    "version": (1, 0),
    "blender": (3, 6, 1),
    "location": "View3D > Toolbar > Shortcuts Display",
    "warning": "",
    "category": "3D View",
    "support": "COMMUNITY",
    "wiki_url": "https://github.com/autobotcode/blender_shortcuts_help",
    "tracker_url": "https://github.com/autobotcode/blender_shortcuts_help"
}

import bpy
from bpy.props import StringProperty, CollectionProperty, BoolProperty
import os

class ShortcutCategory(bpy.types.PropertyGroup):
    expanded: BoolProperty(name="Expanded", default=False)

class ShortcutsPopup(bpy.types.Operator):
    bl_idname = "wm.shortcuts_popup"
    bl_label = "Shortcuts"
    
    filter: StringProperty(default="")
    expanded_categories: CollectionProperty(type=ShortcutCategory)

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop(self, "filter", text="", icon='VIEWZOOM')

        keyconfigs_to_check = [bpy.context.window_manager.keyconfigs.default, bpy.context.window_manager.keyconfigs.user]
        filter_lower = self.filter.lower()
        shortcut_dict = {}

        is_mac = os.name == 'posix'
        WINDOWS_KEYS = ["HOME", "END", "INSERT", "DEL", "PAGE_UP", "PAGE_DOWN", "BACK_SPACE", "LEFT_ALT", "RIGHT_ALT"]
        MAC_KEYS = ["FN"]
        
        for keyconfig in keyconfigs_to_check:
            for keymap in keyconfig.keymaps:
                for item in keymap.keymap_items:
                    if item.map_type != 'KEYBOARD':
                        continue
                    if os.name == 'posix' and item.type in WINDOWS_KEYS:
                        continue
                    elif os.name != 'posix' and item.type in MAC_KEYS:
                        continue
                    
                    key_str = ""
                    if item.oskey:
                        key_str += "Cmd+" if is_mac else "Ctrl+"
                    if item.shift:
                        key_str += "Shift+"
                    if item.ctrl:
                        key_str += "Ctrl+" if not is_mac else "Cmd+"
                    if item.alt:
                        key_str += "Alt+" if not is_mac else "Opt+"
                    key_str += f"{item.type}"

                    if filter_lower in item.name.lower() or filter_lower in key_str.lower():
                        key = (keymap.name, item.name)
                        if key not in shortcut_dict:
                            shortcut_dict[key] = []
                        if key_str not in shortcut_dict[key]:
                            shortcut_dict[key].append(key_str)


        categories = sorted({keymap_name for keymap_name, _ in shortcut_dict.keys()})
        for category in categories:
            if category not in [cat.name for cat in self.expanded_categories]:
                new_cat = self.expanded_categories.add()
                new_cat.name = category

        for cat in self.expanded_categories:
            if cat.name in categories:
                box = layout.box()
                col = box.column(align=True)
                icon = 'TRIA_DOWN' if cat.expanded else 'TRIA_RIGHT'
                col.prop(cat, "expanded", text=cat.name, emboss=False, icon=icon)
                if cat.expanded:
                    for (keymap_name, item_name), keys in sorted(shortcut_dict.items()):
                        if keymap_name == cat.name:
                            key_string = ", ".join(keys)
                            col.label(text=f"      • {item_name} ({key_string})")


    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=600)

bpy.utils.register_class(ShortcutCategory)

def add_shortcuts_button(self, context):
    self.layout.operator("wm.shortcuts_popup", text="Shortcuts", icon='QUESTION')

def register():
    bpy.utils.register_class(ShortcutsPopup)
    bpy.types.TOPBAR_MT_help.append(add_shortcuts_button)
    
    wm = bpy.context.window_manager
    if os.name == 'posix':
        keymap = wm.keyconfigs.addon.keymaps.new(name="Window", space_type='EMPTY', region_type='WINDOW')
        keymap_item = keymap.keymap_items.new('wm.shortcuts_popup', 'K', 'PRESS', shift=True, oskey=True)
    else:
        keymap = wm.keyconfigs.addon.keymaps.new(name="Window", space_type='EMPTY', region_type='WINDOW')
        keymap_item = keymap.keymap_items.new('wm.shortcuts_popup', 'K', 'PRESS', shift=True, ctrl=True)

def unregister():
    bpy.utils.unregister_class(ShortcutsPopup)
    bpy.types.TOPBAR_MT_help.remove(add_shortcuts_button)

    wm = bpy.context.window_manager
    if os.name == 'posix':
        keymap = wm.keyconfigs.addon.keymaps["Window"]
        for kmi in keymap.keymap_items:
            if kmi.idname == 'wm.shortcuts_popup':
                keymap.keymap_items.remove(kmi)
    else:
        keymap = wm.keyconfigs.addon.keymaps["Window"]
        for kmi in keymap.keymap_items:
            if kmi.idname == 'wm.shortcuts_popup':
                keymap.keymap_items.remove(kmi)

if __name__ == "__main__":
    register()
