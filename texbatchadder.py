import bpy
from bpy.props import *
from bpy_extras.io_utils import ImportHelper 	# helps with file browser

# reference active object
active_material = bpy.context.scene.objects.active.active_material

# store image path and array of image texture names
imgs_dir = '../'
tex_names = ['0.png', '1.png', '2.png']

# button click in ative material's property
# open file browser
 	# let user select as many images (only images) as desired
 	# on left side panel, user selects from import options:
 	# 	(1) Should I use alpha? 		Default: True if like png.
 	# 	(2) Should I use transparency? 	Default: True if like png.
 	# 	(3) Should I set preview alpha? Default: True if like png.
 	# 	(4) Should I set to clipped? 	Default: True.

## /!\ TODO: file browsing
# def store_output (paths):
# 	img_paths = paths
# 	return None
# class TexFilesLoader (bpy.types.Operator, ImportHelper):
#     bl_idname = "material.loadtex_files"
#     bl_label = "Browse and load image files as textures"
#     #? path = bpy.props.StringProperty(subtype="FILE_PATH")
#     def execute (self, context):
#     	fpath = self.properties.filepath
#         store_output(self.path)
#         return {'FINISHED'}
#     def invoke (self, context, event):
#         context.window_manager.fileselect_add(self)
#         return {'RUNNING_MODAL'}


empty_tex_slots = []
# store indexes for this material's open texture slots
for i in range (0, len (active_material.texture_slots-1) ):
	if active_material.texture_slots[i] == None:
        # add all open textures slots to list
		empty_tex_slots.append(i)
	else:
        # deactivate all used texture slots for this material
		active_material.use_textures[i] = False

# create textures
for i in range(0,len(tex_names-1)):
    # slot the new texture into the next open slot
    this_empty_slot = active_material.texture_slots[empty_tex_slots[i]]
    active_material.active_texture_index = this_empty_slot
    
    # create the new texture in this slot
    bpy.ops.texture.new()
    
    # build each tex path but use filename without extension for texname
    this_tex_path = imgs_dir+tex_names[i]
    active_material.active_texture.name = strip_img_extension(tex_names[i])

def strip_img_extension (path):
    # take an image filepath string
    # output the string without the file extension
    img_extensions = ['.png','.jpg','.jpeg','.gif','.tif','.bmp']
    if path[-4:] in img_extensions:
        path = path[:-4]
    elif path[-5:] in img_extensions:
        path = path[:-5]
    else:
        pass
    return path

# apply parameters 1-4 above to each texture created
def apply_mattex_params ():
    active_material.use_transparency = True
    active_material.transparency_method = 'Z_TRANSPARENCY'
    active_material.active_texture.type = 'IMAGE'
    active_material.active_texture.use_map_alpha = True
    active_material.alpha = 0.0
    active_material.active_texture.use_preview_alpha = True
    active_material.active_texture.extension = 'CLIP'
    return {'FINISHED'}
    
apply_mattex_params()

# activate the first texture for this material
active_material.use_textures[0] = True


# # test property for user to adjust in panel
# bpy.types.Scene.img_texs_test = EnumProperty(
#     items = [('zero', '0', 'some test text'),],
#     name = 'Image Textures Test',
#     description = 'A test property for image textures batcher'
#     )

# class ImgTexturesPanel (bpy.types.Panel):
# 	# Blender UI label, name, placement
#     bl_label = 'Batch add textures to this material'
#     bl_idname = 'material.panel_name'
#     bl_space_type = 'PROPERTIES'
#     bl_region_type = 'UI'
#     # build the panel
#     def draw (self, context):
#     	# property selection
#         self.layout.row().prop(bpy.context.scene,'img_texs_test', expand=True)
#         # button
#         self.layout.operator('material.operator_name', text="User Button Text")

# class ImgTexturesOperator (bpy.types.Operator):
#     bl_label = 'Batch Text Adder Operation'
#     bl_idname = 'material.operator_name'
#     bl_description = 'Add multiple images as textures for this material'
#     def execute (self, context):
#         # function to run on button press
#         return{'FINISHED'}
    
# def register():
#     bpy.utils.register_class(ImgTexturesPanel)
#     bpy.utils.register_class(ImgTexturesOperator)

# def unregister():
#     bpy.utils.unregister_class(ImgTexturesPanel)
#     bpy.utils.unregister_class(ImgTexturesOperator)

# if __name__ == '__main__':
#     register()
#     #unregister()