import bpy
from bpy.props import *
from bpy_extras.io_utils import ImportHelper    # help with file browser

# Take image paths and create textures to fill active object's material slots
class ImgTexturizer:
    def __init__ (self, texture_names, directory, transparency, update_existing):
        # reference user paths
        self.texture_names = texture_names
        self.dir = directory
        # point to or create object's active material
        # /!\ ERROR PRONE - UPDATE THIS CHECK && COMPARE TO PANEL/OP LOGIC
        if bpy.context.scene.objects.active.active_material == None:
            mat = bpy.data.materials.new(self.strip_img_extension(texture_names[0]))
            self.material = mat
            bpy.context.scene.objects.active.active_material = mat
        else:
            self.material = bpy.context.scene.objects.active.active_material
        # setting checks for setup control flow
        self.transparency = transparency
        self.update_existing = update_existing

    def create_img_plane (self):
        # add 0th image as plane
        area=bpy.context.area.type
        bpy.context.area.type="VIEW_3D"
        bpy.ops.import_image.to_plane(files=[{'name':self.texture_names[0]}],directory=self.dir)
        bpy.context.area.type=area
        # set 0th image's texture properties
        obj = bpy.context.scene.objects.active
        obj.active_material.active_texture.extension = 'CLIP'
        if self.transparency:
            obj.active_material.active_texture.use_preview_alpha = True
            obj.active_material.texture_slots[0].use_map_alpha = True    
        # plane now contains 0th image, so remove from list
        self.texture_names = self.texture_names[1:]
        # update the reference material
        self.material = obj.active_material
        
    def update_filepaths (self, names, path):
        # TODO build out option to completely rewrite an object's textures
        self.texture_names = names
        self.dir = path

    def setup (self):
        # create new image plane if not just updating
        if not self.update_existing:
            self.create_img_plane()
        
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
        # concatenate '//directory/path/' and 'filename.ext'
        return self.dir + filename
    
    def load_image (self, img_index, slot, created_images_list):
        path = self.build_path(self.texture_names[img_index])
        # load image to into blend db
        if self.texture_names[img_index] not in created_images_list:
            bpy.data.images.load(path)
        # point to loaded img
        found_img = bpy.data.images[bpy.data.images.find(self.texture_names[img_index])]
        # use loaded image as this texture's image
        self.material.active_texture.image = found_img

    # take an image filename string
    # output the string without the file extension
    def strip_img_extension (self, filename):
        short_ext = ['.png','.jpg','.gif','.tif','.bmp']
        long_ext = ['.jpeg']
        if any(filename.endswith(e) for e in short_ext):
            filename = filename[:-4]
        elif any(filename.endswith(e) for e in long_ext):
            filename = filename[:-5]        
        return filename

    # apply settings to the material
    def customize_material_params (self, custom_settings=True):
        if custom_settings:
            self.material.preview_render_type = 'FLAT'
            self.material.diffuse_intensity = 1.0
            self.material.specular_intensity = 0.0
            self.material.use_transparent_shadows = True
        if self.transparency:
            self.material.use_transparency = True
            self.material.transparency_method = 'Z_TRANSPARENCY'
            self.material.alpha = 0.0
        return None

    # apply settings to each texture created
    def set_texslot_params (self, tex_slot):
        self.material.active_texture.type = 'IMAGE'
        if self.transparency:
            tex_slot.use_map_alpha = True
            self.material.active_texture.use_preview_alpha = True
        self.material.active_texture.extension = 'CLIP'

# Panel and button
class ImgTexturesPanel (bpy.types.Panel):
    # Blender UI label, name, placement
    bl_label = 'Import Textures as One Plane'
    bl_idname = 'material.texbatch_panel'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'texture'
    update_existing = BoolProperty(name="Add to this object", default=True)
    # build the panel
    def draw (self, context):
        self.update_existing = True
        if bpy.context.scene.objects.active != None and bpy.context.scene.objects.active.active_material.active_texture != None:
            self.layout.operator('material.texbatch_import', text='Add Texs to this Object').update_existing = True
        else:
            self.layout.operator('material.texbatch_import', text='Make Plane of Many Texs').update_existing = False
        # selection to allow for create vs update
        
class ImgTexturesImport (bpy.types.Operator, ImportHelper):
    bl_idname = 'material.texbatch_import' 
    bl_label = 'Import Texs to Single Plane'
    # file browser info and settings
    filepath = StringProperty (name='File Path')
    files = CollectionProperty(name='File Names', type=bpy.types.OperatorFileListElement)
    directory = StringProperty(maxlen=1024, subtype='DIR_PATH',options={'HIDDEN'})
    filter_image = BoolProperty(default=True, options={'HIDDEN'})
    filter_folder = BoolProperty(default=True, options={'HIDDEN'})
    filter_glob = StringProperty(default="", options={'HIDDEN'})
    # img alpha setting to pass to batch texturizer
    use_transparency = BoolProperty (name="Use transparency")
    update_existing = BoolProperty (options={'HIDDEN'})

    def store_files (self, files):
        img_filenames = []
        for f in files:
            img_filenames.append (f.name)
        return img_filenames

    def store_directory (self, path):
        img_dir = bpy.path.relpath (path)+'/'
        return img_dir

    def execute (self, ctx):
        # store files in array and add them to material as textures 
        img_filenames = self.store_files(self.files)
        img_dir = self.store_directory(self.directory)

        # add textures to plane
        texBatchAdder = ImgTexturizer(img_filenames, img_dir, self.use_transparency, self.update_existing)
        texBatchAdder.setup()
        return {'FINISHED'}

    def invoke (self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


# Panel and button registration
def register():
    bpy.utils.register_class(ImgTexturesPanel)
    bpy.utils.register_class(ImgTexturesImport)
    #bpy.types.Texture.texbatch_update_existing_object = bpy.props.BoolProperty(name="Add to this object", default="False")

def unregister():
    bpy.utils.unregister_class(ImgTexturesPanel)
    bpy.utils.register_class(ImgTexturesImport)

if __name__ == '__main__':
    register()
    #unregister()