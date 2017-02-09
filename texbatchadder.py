import bpy
from bpy.props import *
from bpy_extras.io_utils import ImportHelper    # helps with file browser

# store image path and array of image texture filenames
img_dir = '//'
img_filenames = ['test-thumb-0.png', 'test-thumb-1.png', 'test-thumb-2.png']

# button click in active material's property
# open file browser
    # let user select as many images (only images) as desired
    # on left side panel, user selects from import options:
    #   (1) Should I use alpha?         Default: True if like png.
    #   (2) Should I use transparency?  Default: True if like png.
    #   (3) Should I set preview alpha? Default: True if like png.
    #   (4) Should I set to clipped?    Default: True.

class ImgTexturizer:
    
    def __init__ (self, texture_names, directory):
        # reference active material and user paths
        self.material = bpy.context.scene.objects.active.active_material
        self.texture_names = texture_names
        self.dir = directory

    def setup (self):
        # track created imgs (array) and number of tex slots filled (counter)
        img_counter = 0
        used_imgs = []
        
        # add images in material's open texture slots
        for i in range (0, len(self.material.texture_slots)-1):
            if self.material.texture_slots[i] == None and img_counter < len(self.texture_names):
                # create tex in this slot using the next img
                self.create_texture(i, img_counter, used_imgs)
                used_imgs.append (self.texture_names[img_counter])
                img_counter += 1
                # settings for created tex - assumes it's the active tex
                self.set_texslot_params(self.material.texture_slots[i])
            # deactivate all texture slots for this material
            self.material.use_textures[i] = False

        # activate the first texture for this material
        self.material.use_textures[0] = True
        
        # alpha and transparency for this material
        self.customize_material_params()

        # return uncreated imgs if not all images got turned into texs
        return self.check_if_created_all(img_counter)

    def check_if_created_all (self, count_created):
        # verify that all images were loaded into textures
        count_total = len(self.texture_names)
        if count_created >= count_total:
            return {'FINISHED'}
        # return the sublist of uncreated images
        return self.texture_names[count_created:]
        
    def create_texture (self, empty_slot, img_i, created_imgs_list):
        # set new location to the next open slot
        self.material.active_texture_index = empty_slot
        # create the new texture in this slot
        created_tex_name = self.strip_img_extension(self.texture_names[img_i])
        created_tex = bpy.data.textures.new (created_tex_name,'IMAGE')
        # update texture slot to hold this texture
        self.material.texture_slots.add()
        self.material.texture_slots[empty_slot].texture = created_tex
        # load and use imge file
        self.load_image(img_i, empty_slot, created_imgs_list)

    def build_path (self, filename):
        path = self.dir + filename
        return path
    
    def load_image (self, img_index, slot, created_images_list):
        path = self.build_path(self.texture_names[img_index])
        # load image to into blend db
        if self.texture_names[img_index] not in created_images_list:
            bpy.data.images.load(path)
        # point to loaded img
        found_img = bpy.data.images[bpy.data.images.find(self.texture_names[img_index])]
        # use loaded image as this texture's image
        self.material.active_texture.image = found_img
        return found_img

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
    def customize_material_params (self, custom_settings=True, use_transparency=True):
        if custom_settings:
            self.material.diffuse_intensity = 1.0
            self.material.specular_intensity = 0.0
            self.material.use_transparent_shadows = True
        if use_transparency:
            self.material.use_transparency = True
            self.material.transparency_method = 'Z_TRANSPARENCY'
            self.material.alpha = 0.0
        return None

    def set_texslot_params (self, tex_slot):
        self.material.active_texture.type = 'IMAGE'
        tex_slot.use_map_alpha = True
        self.material.active_texture.use_preview_alpha = True
        self.material.active_texture.extension = 'CLIP'

def load_image_as_plane (img_filename):
    # assure context is 3D
    area_3d = bpy.context.area
    bpy.context.area.type = 'VIEW_3D'
    bpy.ops.import_image.to_plane()

    # TODO set context to filebrowser
    
    # TODO set filepath to input filepath

    # import img
    bpy.ops.file.execute()

    # set context back to 3D
    bpy.context.area = area_3d

    # grab imported plane and its material
    obj = bpy.context.scene.objects.active
    mat = obj.active_material

    # configure material and texture (imports with only 1 of each)
    mat.diffuse_intensity = 1.0
    mat.specular_intensity = 0.0
    mat.use_transparency = True
    mat.transparency_method = 'Z_TRANSPARENCY'
    mat.alpha = 0.0
    mat.use_transparent_shadows = True
    mat.texture_slots[0].use_alpha = True
    mat.texture_slots[0].use_map_alpha = True
    mat.texture_slots[0].use_preview_alpha = True
    mat.texture_slots[0].extension = 'CLIP'
    return (obj, mat)

class ImgTexturesPanel (bpy.types.Panel):
    # Blender UI label, name, placement
    bl_label = 'Add Image Textures'
    bl_idname = 'material.texbatch_panel'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    # build the panel
    def draw (self, context):
        self.layout.operator('material.texbatch_op', text='Batch Add Image Textures')
        self.layout.operator('material.texbatch_paths', text='Browse & Add Images')
        # TODO: display the images that are loaded
        
class ImgTexturesImporter (bpy.types.Operator, ImportHelper):
    bl_idname = 'material.texbatch_paths' 
    bl_label = 'Import Texture Files'
    filepath = StringProperty (name='File Path')
    files = CollectionProperty(name='File Names', type=bpy.types.OperatorFileListElement)
    directory = StringProperty(maxlen=1024, subtype='DIR_PATH',options={'HIDDEN'})
    filter_image = BoolProperty(default=True, options={'HIDDEN'})
    filter_folder = BoolProperty(default=True, options={'HIDDEN'})
    filter_glob = StringProperty(default="", options={'HIDDEN'})
    
    def execute (self, ctx):
        img_filenames = []
        img_dir = bpy.path.relpath(self.directory)+'/'
        for f in self.files:
            img_filenames.append(f.name)
        imgTexs = ImgTexturizer (img_filenames, img_dir)
        imgTexs.setup()

        # TODO
        #  - create a "new material" task (use texs to create brand new obj)
        #       - grab 0th image and run "img as plane"
        #       - apply material settings to that img
        #       - use this as import
        #  - separate the current process out as an "update material" task
        return {'FINISHED'}

    def invoke (self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
## /!\ COMPARE: file browsing and adding
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
   
class ImgTexturesOperator (bpy.types.Operator):
    bl_label = 'Batch Add Image Textures'
    bl_idname = 'material.texbatch_op'
    bl_description = 'Add multiple images as textures for this material'
    def execute (self, context):
        # reference active object and names when instantiating
        imgTexs = ImgTexturizer (img_filenames, img_dir)
        imgTexs.setup()
        return {'FINISHED'}
 
def register():
    bpy.utils.register_class(ImgTexturesPanel)
    #bpy.utils.register_class(ImgTexturesOperator)
    bpy.utils.register_class(ImgTexturesImporter)

def unregister():
    bpy.utils.unregister_class(ImgTexturesPanel)
    #bpy.utils.unregister_class(ImgTexturesOperator)
    bpy.utils.register_class(ImgTexturesImporter)

if __name__ == '__main__':
    register()
    #unregister()