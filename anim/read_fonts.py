import bpy

## Read all fonts for text (font) objects in Blender scene

def read_font(obj):
    if obj.type != 'FONT' or not obj.data.font:
        return
    return obj.data.font

def print_font_name(font):
    font and print(font.name)
    return font

def objects_fonts(objs=bpy.context.scene.objects, selected_only=False):
    """Find fonts for a list of objects"""
    fonts = []
    for obj in objs:
        if selected_only and not obj.select:
            continue
        if obj.type == 'FONT':
            font = read_font(obj)
            font and fonts.append(font)
    return fonts

def scene_fonts(scene=bpy.context.scene):
    if not scene: return
    fonts = objects_fonts(scene.objects, selected_only=False)
    return fonts

fonts = scene_fonts()
fonts and [print_font_name(f) for f in fonts]
