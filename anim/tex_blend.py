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

def get_mattex(obj):
    """Get an object's active material and texture slot"""
    if obj is None: return
    try:
        material = obj.active_material
        texture_slot = material.texture_slots[material.active_texture_index]
    except:
        return (None, None)
    return (material, texture_slot)

def configure_blend(material, texture_slot, colors, blend_type):
    """Adjust material and texture settings for gradient"""
    material.diffuse_color = colors.first()
    material.diffuse_intensity = 1.0
    material.specular_intensity = 0.0
    material.use_transparent_shadows = True
    texture_slot.use_map_alpha = True
    texture_slot.use_map_color_diffuse = True
    texture_slot.color = colors.last()
    texture_slot.texture_coords = 'ORCO'
    texture_slot.texture.progression = blend_type
    return (material, texture_slot)

def create_blend(obj=bpy.context.scene.objects.active, colors=Grab([]), blend_type='EASING', only_active=False):
    """Create and assign gradient material-texture to object"""
    if not obj or not obj.data: return

    # create and slot in blend material-texture
    material = bpy.data.materials.new(name=gradient_name)
    print(material.name)
    obj.data.materials.append(material)
    texture = bpy.data.textures.new(name=gradient_name, type='BLEND')
    material.texture_slots.add()

    # add blend texture
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

    if len(colors) >= 2 and texture_slot:
        configure_blend(material, texture_slot, colors)

    # deactivate all but blend
    if only_active:
        for slot in material.texture_slots:
            if slot: slot.use = False
        texture_slot.use = True
    return

def update_blend(obj=bpy.context.scene.objects.active, colors=Grab([])):
    """Update existing texture and material to blend gradient"""
    if not obj or not colors: return
    material, texture_slot = get_mattex(obj)
    if material and texture_slot:
        configure_blend(material, texture_slot, colors)
    return

def create_blend_plane(colors, blend_type, shape='PLANE'):
    """Create a new object with a mesh and a blend gradient"""
    mesh_info = bmesh.new()
    points = {
        'PLANE': ((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (1.0, 1.0, 0.0), (0.0, 1.0, 0.0)),
        'CUBE': ((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (1.0, 1.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0), (1.0, 0.0, 0.0), (0.0, 1.0, 1.0), (1.0, 1.0, 1.0))
    }
    for point in points[shape]:
        mesh_info.verts.new(point)
    mesh_info.faces.new(mesh_info.verts)
    mesh_info.normal_update()
    mesh = bpy.data.meshes.new(gradient_name)
    mesh_info.to_mesh(mesh)
    obj = bpy.data.objects.new(gradient_name, mesh)
    bpy.context.scene.objects.link(obj)
    bpy.context.scene.update()
    create_blend(obj=obj, colors=colors, blend_type=blend_type)
    return obj

# test calls
colors = Grab([(1,1,1), (0,0,0)])
#create_blend(colors=colors)
create_blend_plane(colors)
