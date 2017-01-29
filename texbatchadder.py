import bpy
from bpy.props import *
from bpy_extras.io_utils import ImportHelper 	# helps with file browser

# store image path and array of image texture filenames
img_dir = '//'
img_filenames = ['0.png', '1.png', '2.png']

# button click in ative material's property
# open file browser
    # let user select as many images (only images) as desired
    # on left side panel, user selects from import options:
    #   (1) Should I use alpha?         Default: True if like png.
    #   (2) Should I use transparency?  Default: True if like png.
    #   (3) Should I set preview alpha? Default: True if like png.
    #   (4) Should I set to clipped?    Default: True.

## /!\ TODO: file browsing
# def store_output (paths):
#   img_paths = paths
#   return None
# class TexFilesLoader (bpy.types.Operator, ImportHelper):
#     bl_idname = "material.loadtex_files"
#     bl_label = "Browse and load image files as textures"
#     #? path = bpy.props.StringProperty(subtype="FILE_PATH")
#     def execute (self, context):
#       fpath = self.properties.filepath
#         store_output(self.path)
#         return {'FINISHED'}
#     def invoke (self, context, event):
#         context.window_manager.fileselect_add(self)
#         return {'RUNNING_MODAL'}

class ImgTexturizer:

    def __init__ (self, texture_names, directory):
        # reference active material and user paths
        self.material = bpy.context.scene.objects.active.active_material
        self.texture_names = texture_names
        self.dir = directory

    def setup (self):
        # counter for tracking current img index (equal to number of tex slots filled)
        img_counter = 0
        # add images in material's open texture slots
        for i in range (0, len (self.material.texture_slots)-1 ):
            if self.material.texture_slots[i] == None:
                # create tex in this slot using the next img
                self.create_texture(i, img_counter)
                img_counter += 1
                # settings for created tex - assumes it's the active tex
                self.apply_mattex_params()
                self.material.use_textures[i] = False
            else:
                # deactivate all used texture slots for this material
                self.material.use_textures[i] = False
        # activate the first texture for this material
        self.material.use_textures[0] = True

        # return uncreated imgs if not all images got turned into texs
        return self.check_if_created_all(img_counter)

    def check_if_created_all (self, count_created):
        # verify that all images were loaded into textures
        count_total = len(self.texture.names)
        if count_created >= count_total:
            return {'FINISHED'}
        # return the sublist of uncreated images
        return self.texture_names[count_created:]

    def create_texture (self, empty_slot, img_i):
        # set new location to the next open slot
        self.material.active_texture_index = empty_slot
        # create the new texture in this slot
        created_tex_name = strip_img_extension(self.texture_names[img_i])
        created_tex = bpy.data.textures.new (created_tex_name,'IMAGE')
        # update texture slot to hold this texture
        self.material.texture_slots.add()
        self.material.texture_slots[empty_slot].texture = created_tex
        # load and use imge file
        tex_path = self.dir + self.texture_names[img_i]
        self.load_image(tex_path, empty_slot)

    def build_path (self, filename):
        return (self.dir + filename)
    
    def load_image (self, filename, slot):
        path = self.build_path(filename)
        # load image to into blend db
        bpy.data.images.load(path)
        # use loaded image as this texture's image
        self.material.active_texture.image = bpy.data.images[bpy.data.images.find(filename)]

    # take an image filename string
    # output the string without the file extension
    def strip_img_extension (self, filename):
        img_extensions = ['.png','.jpg','.jpeg','.gif','.tif','.bmp']
        if filename[-4:] in img_extensions:
            return filename[:-4]
        elif path[-5:] in img_extensions:
            return filename[:-5]
        else:
            return filename

    # apply parameters 1-4 above to each texture created
    def apply_mattex_params (self):
        self.material.use_transparency = True
        self.material.transparency_method = 'Z_TRANSPARENCY'
        self.material.active_texture.type = 'IMAGE'
        self.material.active_texture.use_map_alpha = True
        self.material.alpha = 0.0
        self.material.active_texture.use_preview_alpha = True
        self.material.active_texture.extension = 'CLIP'

# reference active object and names when instantiating
imgTexs = ImgTexturizer (img_filenames, img_dir)
imgTexs.setup()

# # test property for user to adjust in panel
# bpy.types.Scene.img_texs_test = EnumProperty(
#     items = [('zero', '0', 'some test text'),],
#     name = 'Image Textures Test',
#     description = 'A test property for image textures batcher'
#     )

# class ImgTexturesPanel (bpy.types.Panel):
#   # Blender UI label, name, placement
#     bl_label = 'Batch add textures to this material'
#     bl_idname = 'material.panel_name'
#     bl_space_type = 'PROPERTIES'
#     bl_region_type = 'UI'
#     # build the panel
#     def draw (self, context):
#       # property selection
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