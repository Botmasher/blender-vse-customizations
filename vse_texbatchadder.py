import bpy
from bpy.props import *

# button click on materials property
# open file browser
 	# let user select as many images (only images) as desired
 	# on left side panel, user selects from import options:
 	# 	(1) Should I use alpha? 		Default: True if like png.
 	# 	(2) Should I use transparency? 	Default: True if like png.
 	# 	(3) Should I set preview alpha? Default: True if like png.
 	# 	(4) Should I set to clipped? 	Default: True.
# store array of image names
# create as many textures for this material as there are image names in array
	# 	each tex name is the name of img before file extension dot
# apply parameters 1-4 above to each texture created
# deactivate all textures for this material
# activate the first texture for this material
# rename the material to match the first texture name, minus any final hyphens, final numbers, or final hyphen+numbers

# test property for user to adjust in panel
bpy.types.Scene.img_texs_test = EnumProperty(
    items = [('zero', '0', 'some test text'),
             ('one', '1', 'some test text')],
    name = 'Image Textures Test',
    description = 'A test property for image textures batcher'
    )

class ImgTexturesPanel (bpy.types.Panel):
	# Blender UI label, name, placement
    bl_label = 'Batch add textures to this material'
    bl_idname = 'material.panel_name'
    bl_space_type = 'SEQUENCE_EDITOR'
    bl_region_type = 'UI' # change to 
    # build the panel
    def draw (self, context):
    	# property selection
        self.layout.row().prop(bpy.context.scene,'img_texs_test', expand=True)
        # button
        self.layout.operator('material.operator_name', text="User Button Text")

class ImgTexturesOperator (bpy.types.Operator):
    bl_label = 'Batch Text Adder Operation'
    bl_idname = 'material.operator_name'
    bl_description = 'Add multiple images as textures for this material'
    def execute (self, context):
        # function to run on button press
        return{'FINISHED'}
    
def register():
    bpy.utils.register_class(ImgTexturesPanel)
    bpy.utils.register_class(ImgTexturesOperator)

def unregister():
    bpy.utils.unregister_class(ImgTexturesPanel)
    bpy.utils.unregister_class(ImgTexturesOperator)

if __name__ == '__main__':
    register()
    #unregister()