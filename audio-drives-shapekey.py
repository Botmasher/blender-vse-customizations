import bpy

# audio input drives shape key value
# a Blender Python script by Botmasher (Josh)

# 0. select object in 3d view
# 1. Make sure this script is open in the text editor
# 2. click "Run script" with this script open in the text editor
# ?3. add your audio file

sound_file_path = '/Users/username/Desktop/testaudio.wav'
obj = bpy.context.object
starting_frame = 0

# no keys, add a basis key first
if obj.data.shape_keys == None:
    obj.shape_key_add()
audio_key = obj.shape_key_add()
audio_key.name = "audio-driven-key"
audio_key.value = 1.0

# add keyframe to shape key value
bpy.context.scene.frame_current = 0
kf = audio_key.keyframe_insert("value",frame=starting_frame)

# bake sound to the shape key fcurve
ctx = bpy.context.area.type
bpy.context.area.type = 'GRAPH_EDITOR'
bpy.ops.graph.sound_bake (filepath=sound_file_path)

# add modifier > envelope > add point
env = bpy.ops.graph.fmodifier_add(type='ENVELOPE')
bpy.context.area.type = ctx

# mess with r, min, max vals (can auto somehow?)
env.reference_value = 0.0
env.default_min = 0.0
env.default_max = 0.8

# add same audio file to vse starting at frame n
bpy.context.area.type = 'SEQUENCE_EDITOR'
bpy.ops.sequencer.sound_strip_add(filepath=sound_file_path)
sound_strip = bpy.context.scene.sequence_editor.active_strip
# set video to length of the audio
if bpy.context.scene.frame_start == 1:
    bpy.context.scene.frame_start = 0
if bpy.context.scene.frame_end < sound_strip.frame_final_duration:
    bpy.context.scene.frame_end = sound_strip.frame_final_duration
bpy.context.area.type = ctx


# driving from this key --
# bpy.context.object.data.shape_keys.key_blocks['Name'].driver_add("PATH TO THE PROPERTY TO DRIVE") # analogous to the fcurve's data path