import bpy

## Blender API experimentation for 2.80

# data for scene and view
scene = bpy.context.scene
layer = bpy.context.view_layer
data = bpy.data

# get the active object
active_object = layer.objects.active

# get all selected objects
selected_objects = [object for object in layer.objects.selected]

# deselect all objects
for object in layer.objects:
    object.select_get() and layer.select_set(False)

# select the active object
active_object.select_set(True)

# delete the active object
nested_collection = scene.collection.children[0]    # key ['Collection']
nested_collection.objects.unlink(active_object)

# create a primitive
mesh_size = 3.0
bpy.ops.mesh.primitive_cube_add(size=mesh_size)
mesh_object = layer.objects.active

# create and link an object
new_mesh = data.meshes.new("empty")
new_object = data.objects.new("Twobject", new_mesh)
scene.collection.objects.link(new_object)

# create materials on the object
material_a = bpy.data.materials.new("color-A")
material_b = bpy.data.materials.new("color-B")
new_object.active_material = material_a
new_object.data.materials.append(material_b)

# TODO: toggle between multiple materials/textures
