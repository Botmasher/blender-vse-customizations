#!/usr/bin/env python
import bpy
from bpy.props import *
from bpy_extras.io_utils import ImportHelper

## Pretty Image Loader
## a small Blender Python image loading tool by Botmasher (Joshua R)
##
## This small Blender Python tool loads images with your choice of a transform strip, transparency
## and original image dimensions instead of default settings and wonkily stretched/squashed dimensions
## 

def load_scale_img (name, path, scale=1.0, channel=1, frame_start=bpy.context.scene.frame_current):
    # open a browser window and let user pick the path
    strip = bpy.context.scene.sequence_editor.sequences.new_image(name=name, filepath=path, channel=channel, frame_start=frame_start)
    
    for s in bpy.context.scene.sequence_editor.sequences_all: s.select = False
    strip.select = True
    
    bpy.ops.sequencer.effect_strip_add(type='TRANSFORM')
    transform_strip = bpy.context.scene.sequence_editor.active_strip
    transform_strip.use_uniform_scale = False
    
    # hidden bg render to get updated img res data (otherwise orig w and h are 0)
    # https://blenderartists.org/forum/archive/index.php/t-339084.html
    bpy.ops.render.opengl(sequencer=True)

    # gather image data
    image = strip.elements[0]
    width = image.orig_width
    height = image.orig_height
    directory = strip.directory
    filename = image.filename
    
    print(str(width) + "x" + str(height))

    # TODO figure stretch into calc
    # - get render resolution
    # - compare image w/h to render w or h (probably h? eventually bool prop for user to pick)
    # - if image h is sized up to res h, what would the orig width be relative to that height?
    #   - Blender's not straightforwardly calculating height width ratio as resized?
    # - maybe instead set crop, then size up/down to that height or width?
    #   - in that case just figure the % diff btwn res h vs orig h and just use that factor for w as well

    # resize image

    #ratio = width / height
    #transform_strip.scale_start_x = scale
    #transform_strip.scale_start_y = scale
    
    strip.use_translation = True
    rew_w = bpy.context.scene.render.resolution_x
    res_h = bpy.context.scene.render.resolution_y
    h_ratio = res_h / height
    transform_strip.use_uniform_scale = True
    transform_strip.scale_start_x = scale * h_ratio

    ## TODO center to screen/res

    return strip

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
        bpy.context.scene.sequence_editor_create()  # verify vse is valid in scene
        load_scale_img ("MY-ASDF-PATH.png")
        return {'FINISHED'}
    # import settings
    filepath = StringProperty (name='File Path')
    files = CollectionProperty(name='File Names', type=bpy.types.OperatorFileListElement)
    directory = StringProperty(maxlen=1024, subtype='DIR_PATH',options={'HIDDEN'})
    filter_image = BoolProperty(default=True, options={'HIDDEN'})
    filter_folder = BoolProperty(default=True, options={'HIDDEN'})
    #filter_glob = StringProperty(default="", options={'HIDDEN'})
    # img alpha setting to pass to batch texturizer
    use_transparency = BoolProperty (default=True, name="Use transparency")
    replace_current = BoolProperty (default=False, name="Replace current textures")
    update_existing = BoolProperty (options={'HIDDEN'})

    def store_files (self, files):
        img_filenames = []
        for f in files:
            img_filenames.append (f.name)
        return img_filenames

    def execute (self, ctx):
        print("\n\nRestarting PRETTY IMG LOADER...")
        img_filenames = self.store_files(self.files)
        img_path = self.directory
        print(img_path)
        print(img_filenames)
        for filename in img_filenames:
            load_scale_img(filename, "%s%s" % (img_path, filename))
        return {'FINISHED'}

    def invoke (self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

  
def register():
    bpy.utils.register_class(PrettyImagePanel)
    bpy.utils.register_class(PrettyImageOperator)

def unregister():
    bpy.utils.unregister_class(PrettyImagePanel)
    bpy.utils.unregister_class(PrettyImageOperator)

if __name__ == '__main__':
    register()
    #unregister()