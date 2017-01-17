import bpy
from bpy.props import *
from bpy_extras.io_utils import ImportHelper 	# helps with file browser

# button click in ative material's property
# open file browser
 	# let user select as many images (only images) as desired
 	# on left side panel, user selects from import options:
 	# 	(1) Should I use alpha? 		Default: True if like png.
 	# 	(2) Should I use transparency? 	Default: True if like png.
 	# 	(3) Should I set preview alpha? Default: True if like png.
 	# 	(4) Should I set to clipped? 	Default: True.
output = []
def store_output (path):
	output = path
	return None

class TexFilesLoader (bpy.types.Operator, ImportHelper):
    bl_idname = "material.loadtex_files"
    bl_label = "Browse and load image files as textures"
    #? path = bpy.props.StringProperty(subtype="FILE_PATH")
    def execute (self, context):
    	fpath = self.properties.filepath
        store_output(self.path)
        return {'FINISHED'}
    def invoke (self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

# store array of image names
tex_names = []
# create as many textures as there are image names in array
	# 	each tex name is the name of img before file extension dot
new_tex = bpy.ops.texture.new() # better way to create new tex?
new_tex.name = 'texname'        # error - how to ref created tex?

# apply parameters 1-4 above to each texture created
new_tex.type = 'IMAGE' # syntax?
new_tex.use_map_alpha = True
bpy.context.scene.objects.active.active_material.use_transparency = True
bpy.context.scene.objects.active.active_material.transparency_method = 'Z_TRANSPARENCY'
bpy.context.scene.objects.active.active_material.alpha = 0.0
new_tex.use_preview_alpha = True
new_tex.extension = 'CLIP'

# add created textures to this material

# deactivate all textures for this material
for tex in bpy.context.scene.objects.active.active_material.texture_slots:
    if bpy.context.scene.objects.active.active_material.texture_slots[i] != None:
        bpy.context.scene.objects.active.active_material.use_textures[i] = False
# activate the first texture for this material
bpy.context.scene.objects.active.active_material.use_textures[0] = True
# rename the material to match the first texture name, minus any final hyphens, final numbers, or final hyphen+numbers
bpy.context.scene.objects.active.active_material.texture_slots[n].name = tex_names[n]


# # test property for user to adjust in panel
# bpy.types.Scene.img_texs_test = EnumProperty(
#     items = [('zero', '0', 'some test text'),
#              ('one', '1', 'some test text')],
#     name = 'Image Textures Test',
#     description = 'A test property for image textures batcher'
#     )

# class ImgTexturesPanel (bpy.types.Panel):
# 	# Blender UI label, name, placement
#     bl_label = 'Batch add textures to this material'
#     bl_idname = 'material.panel_name'
#     bl_space_type = 'SEQUENCE_EDITOR'
#     bl_region_type = 'UI' # change to 
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