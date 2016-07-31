import bpy
from bpy.props import *

def load_image (file):
    #if this is an image strip
    # use the same path
    # else
    # open a browser window and let user pick the path
    bpy.context.sequencer.image_strip_add()
    print (file)
    return file

class PrettyImagePanel (bpy.types.Panel):
    # Blender UI label, name, placement
    bl_label = 'Pretty Image Loader'
    bl_idname = 'strip.pretty_image_loader'
    bl_space_type = 'SEQUENCE_EDITOR'
    bl_region_type = 'UI'
    def draw (self, context):
        row = self.layout.row()
        row.operator("strip.add_pretty", text='Add Pretty Image')
        
class PrettyImageOperator (bpy.types.Operator):
    # Blender UI label, id and description
    bl_label = "Pretty Image Loader"
    bl_idname = "strip.add_pretty"
    bl_description = 'Add a new image with alpha, transform strip and proper dimensions.'
    def execute (self, context):
        load_image("ASDF IS A PATH, right?!?")
        return {'FINISHED'}
    
def register():
    bpy.utils.register_class(PrettyImagePanel)

def unregister():
    bpy.utils.unregister_class(PrettyImagePanel)

if __name__ == '__main__':
    register()
    #unregister()