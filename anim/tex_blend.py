import bpy, bmesh

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
gradient_name = 'gradient'

def create_blend(obj=bpy.context.scene.objects.active, colors=Grab([]), only_active=False):
    """Create and assign gradient material-texture to object"""

    if not obj or not obj.data: return

    # create and slot in blend material-texture
    material = bpy.data.materials.new(name=gradient_name)
    print(material.name)
    obj.data.materials.append(material)
    texture = bpy.data.textures.new(name=gradient_name, type='BLEND')
    material.texture_slots.add()

    #
    texture_slot = None
    for i in range(len(material.texture_slots)):
        if not material.texture_slots[i].texture:
            material.texture_slots.create(i)
            material.texture_slots[i].texture = texture
            texture_slot = material.texture_slots[i]
            break
        elif i == len(material.texture_slots):
            print("Failed to add gradient to {0} - texture slots full".format(obj))
            raise
        continue

    # configure blend
    if len(colors) >= 2 and texture_slot:
        material.diffuse_color = colors.first()
        material.diffuse_intensity = 1.0
        material.specular_intensity = 0.0
        material.use_transparent_shadows = True
        texture_slot.use_map_alpha = True
        texture_slot.use_map_color_diffuse = True
        texture_slot.color = colors.last()
        texture_slot.texture_coords = 'ORCO'

    # TODO deactivate all but blend
    if only_active:
        slots = [slot for slot in obj.material_slots if slot.material == material]
        if len(slots) < 1: return

    return

# create new gradient object
def create_blend_plane(colors):
    mesh_info = bmesh.new()
    points = ((0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0))
    for x,y in points:
        mesh_info.verts.new((x, y, 0.0))
    mesh_info.faces.new(mesh_info.verts)
    mesh_info.normal_update()
    mesh = bpy.data.meshes.new(gradient_name)
    mesh_info.to_mesh(mesh)
    obj = bpy.data.objects.new(gradient_name, mesh)
    bpy.context.scene.objects.link(obj)
    bpy.context.scene.update()
    create_blend(obj=obj, colors=colors)
    return obj

# test calls
colors = Grab([(1,1,1), (0,0,0)])
#create_blend(colors=colors)
create_blend_plane(colors)

# TODO update existing texture to blend
