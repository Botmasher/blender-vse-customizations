import bpy

## Blend Gradient Texture
##
## Blender Python script by Joshua R (GitHub user Botmasher)
##
## set colors and options to create a gradient material

# NOTE
# - create material on active object
# - create texture (check if slots empty or if one exists)
# - set to blend

blend_name = 'gradient'

def create_blend(obj=bpy.context.scene.objects.active, only_active=False):
    """Create and assign gradient material-texture to object"""
    if not obj or not obj.data or not obj.data.materials: return
    # create and slot in blend material-texture
    material = bpy.data.materials.new(name=blend_name)
    obj.data.materials.append(material)
    texture = bpy.data.textures.new(name=blend_name, type='BLEND')
    material.texture_slots.add()
    material.texture_slots.create(len(material.texture_slots)-1)
    material.texture_slots[len(material.texture_slots)-1] = texture

    # TODO deactivate all but blend
    if only_active:
        slots = [slot for slot in obj.material_slots if slot.material == material]
        if len(slots) < 1: return
    return

# TODO create new blended plane

# TODO update existing texture to blend
