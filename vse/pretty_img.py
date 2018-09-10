#!/usr/bin/env python
import bpy
from bpy.props import *
from bpy_extras.io_utils import ImportHelper

## Pretty Image Loader
## sequencer image loading tool by Botmasher (Joshua R)
##
## This small Blender Python tool loads prettier images with transparency and original image
## dimensions instead of default settings and wonkily stretched/squashed dimensions
## 

def load_scale_img (name, path, scale=1.0, channel=1, frame_start=bpy.context.scene.frame_current, length=10, alpha=True):
    # open a browser window and let user pick the path

    bpy.context.scene.sequence_editor_create()
    # create sequence editor

    strip = bpy.context.scene.sequence_editor.sequences.new_image(name=name, filepath=path, channel=channel, frame_start=frame_start)

    # TODO set channel strip wisely - currently importing many causes interlaced stacking of transform and image strips

    for s in bpy.context.scene.sequence_editor.sequences_all: s.select = False
    strip.select = True
    
    bpy.ops.sequencer.effect_strip_add(type='TRANSFORM')
    transform_strip = bpy.context.scene.sequence_editor.active_strip
    transform_strip.use_uniform_scale = False
    
    # hidden bg render to get updated img res data (otherwise orig w and h are 0)
    # https://blenderartists.org/forum/archive/index.php/t-339084.html
    bpy.ops.render.opengl(sequencer=True)

    # gather image data
    img = strip.elements[0]
    img_res = {'w': img.orig_width, 'h': img.orig_height}
    #directory = strip.directory
    filename = img.filename
    
    print("%s: %s" % (filename, "{0} x {1}".format(img_res['w'], img_res['h'])))

    # resize image
    # figure out how to resize just using input dimensions, the stretch applied, transform scale
    render_res = {'w': bpy.context.scene.render.resolution_x, 'h': bpy.context.scene.render.resolution_y}
    img_render_ratio = {'w': img_res['w'] / render_res['w'], 'h': img_res['h'] / render_res['h']}
    print("Image vs screen res ratio - w: {0:.0f}%, h: {1:.0f}%".format(img_render_ratio['w'] * 100, img_render_ratio['h'] * 100))

    scaled_img_h = 1080     # 1.0 scale y == 100% render_res.h
    scaled_img_w = 1920     # stretched value
    scaled_img_w_target = img_res['w'] / img_res['h'] * 1080      # final value we're after
    img_rescale_y = scaled_img_w_target / scaled_img_w  # what is that as a percentage of stretch?

    transform_strip.use_uniform_scale = False
    transform_strip.scale_start_y = scale                   # w
    transform_strip.scale_start_x = img_rescale_y * scale   # h

    # set strip opacity
    if alpha:
        transform_strip.blend_type = 'ALPHA_OVER'
        transform_strip.blend_alpha = 1.0
        strip.blend_type = 'ALPHA_OVER'
        strip.blend_alpha = 0.0

    # set strip length
    strip.frame_final_duration = length

    return strip

# UI menu properties
PrettyImageProperties = {
    'alpha': BoolProperty(name="Transparency", description="Use alpha blend on image transform", default=True),
    'scale': FloatProperty(name="Scale", description="Transform scale to apply to fitted image", default=1.0),
    'length': IntProperty(name="Strip length", description="Frame duration of imported images", default=10)
}

class PrettyImagePanel (bpy.types.Panel):
    # Blender UI label, name, placement
    bl_label = "Pretty Image Loader"
    bl_idname = 'strip.pretty_image_loader'
    bl_space_type = 'SEQUENCE_EDITOR'
    bl_region_type = 'UI'
    def draw (self, context):

        # TODO do not show if inspecting a single strip
        sequencer = bpy.context.scene.sequence_editor
        #if sequencer.active_strip: return

        row = self.layout.row()
        row.operator("strip.add_pretty", text="Add Pretty Image")
        
class PrettyImageOperator (bpy.types.Operator):
    # Blender UI label, id and description
    bl_label = "Pretty Image Operator"
    bl_idname = 'strip.add_pretty'
    bl_description = "Add a new image with alpha, transform strip and proper dimensions."
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
    # image loading/formatting
    set_alpha = PrettyImageProperties['alpha']
    img_scale = PrettyImageProperties['scale']
    length = PrettyImageProperties['length']
    
    def store_files (self, files):
        img_filenames = []
        for f in files:
            img_filenames.append (f.name)
        return img_filenames

    def execute (self, ctx):
        print("\n\nRestarting PRETTY IMG LOADER...")
        img_filenames = self.store_files(self.files)
        img_path = self.directory
        for filename in img_filenames:
            load_scale_img(filename, "{0}{1}".format(img_path, filename), scale=self.img_scale, length=self.length, alpha=self.set_alpha)
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
