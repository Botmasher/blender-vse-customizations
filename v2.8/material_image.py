import bpy

# Use material nodes to display an image with transparency
# script by Joshua (GitHub user Botmasher)

# add plane
# TODO: create fresh new plane and add vertex data
# img_plane = bpy.data.objects.new(
#     "Img Plane",
#     bpy.data.meshes.new("Img Plane")
# )
# bpy.context.scene.collection.objects.link(img_plane)
# bpy.context.view_layer.objects.active = img_plane
bpy.ops.mesh.primitive_plane_add()
img_plane = bpy.context.view_layer.objects.active
img_plane.name = "Img Plane"

# add material to plane
img_material = bpy.data.materials.new("img_mat")
img_plane.active_material = img_material
# TODO: add image texture data (the image)
#bpy.data.images.new(name="test img")

# set material image texture
img_texture = bpy.data.textures.new("img_tex", 'IMAGE')
img_material.use_nodes = True
img_material.node_tree.nodes[1].type = 'MIX_SHADER'
img_material.node_tree.nodes[1].inputs[0] = img_texture
node = img_material.node_tree.nodes[1]
node.label = 'custom_nodetree_img_node'

# TODO: grab node and adjust shaders, then material settings
# - tried ways to get at it through material and node_tree
# - update to Diffuse shader, Transparent shader 
# - then update to alpha Blend and Shadow modes
