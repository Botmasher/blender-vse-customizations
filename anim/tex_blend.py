import bpy

## Blend Gradient Texture
##
## Blender Python script by Joshua R (GitHub user Botmasher)
##
## set colors and options to create a gradient material

# extend list methods
class Grab(list):
    def first(self):
        return self[0]
    def mid(self):
        return self[int(len(self)*0.5)]
    def last(self):
        return self[len(self)-1]

# base name for blends
blend_name = 'gradient'

def create_blend(obj=bpy.context.scene.objects.active, colors=Grab([]), only_active=False):
    """Create and assign gradient material-texture to object"""

    if not obj or not obj.data: return

    # create and slot in blend material-texture
    material = bpy.data.materials.new(name=blend_name)
    print(material.name)
    obj.data.materials.append(material)
    texture = bpy.data.textures.new(name=blend_name, type='BLEND')
    material.texture_slots.add()

    # TODO exception on material or texture stack overflow
    texture_slot = None
    for i in range(len(material.texture_slots)):
        if not material.texture_slots[i].texture:
            material.texture_slots.create(i)
            material.texture_slots[i].texture = texture
            texture_slot = material.texture_slots[i]
            break

    # configure blend
    if len(colors) >= 2 and texture_slot:
        material.diffuse_color = colors.first()
        material.diffuse_intensity = 1.0
        material.specular_intensity = 0.0
        material.use_transparent_shadows = True
        texture_slot.use_map_alpha = True
        texture_slot.texture_coords = 'GENERATED'
        texture_slot.use_map_color_diffuse = True
        texture_slot.color = colors.last()

    # TODO deactivate all but blend
    if only_active:
        slots = [slot for slot in obj.material_slots if slot.material == material]
        if len(slots) < 1: return

    return

# test call
colors = Grab([(1,1,1), (0,0,0)])
create_blend(colors=colors)

# TODO create new blended plane

# TODO update existing texture to blend
