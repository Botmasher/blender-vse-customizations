import bpy

# audio input drives shape key value
# a Blender Python script by Botmasher (Josh)

# 0. select object in 3d view
# 1. Make sure this script is open in the text editor
# 2. click "Run script" with this script open in the text editor
# ?3. add your audio file

obj = bpy.context.object
starting_frame = 0

# no keys, add a basis key first
if obj.data.shape_keys == None:
    obj.shape_key_add()
audio_key = obj.shape_key_add()
audio_key.name = "Audio driven key"
audio_key.value = 1.0

# add keyframe to shape key value
bpy.context.scene.frame_current = 0
audio_key.keyframe_insert("value",frame=starting_frame)

# bake sound to the shape key fcurve

# add modifier > envelope > add point

# mess with r, min, max vals (can auto somehow?)

# set video to length of the audi

# add same audio file to vse starting at frame n

# driving from this key --
# bpy.context.object.data.shape_keys.key_blocks['Name'].driver_add("PATH TO THE PROPERTY TO DRIVE") # analogous to the fcurve's data path