import bpy

# audio input drives shape key value
# a Blender Python script by Botmasher (Josh)

# 0. select object in 3d view
# 1. Make sure this script is open in the text editor
# 2. click "Run script" with this script open in the text editor
# ?3. add your audio file

# audio to use and when to start playing
sound_file_path = '/Users/username/Desktop/testaudio.wav'
starting_frame = 0
custom_key_name = 'audio-shape-key'

# which object to keyframe
obj = bpy.context.object

def set_ctx (context):
	old_context = bpy.context.area.type
	bpy.context.area.type = context
	return (old_context, bpy.context.area.type)

def add_shape_key (selected_object, key_name):
	# no keys, add a basis key first
	if selected_object.data.shape_keys == None:
	    selected_object.shape_key_add()
	shape_key = selected_object.shape_key_add()
	shape_key.name = key_name
	shape_key.value = 1.0
	return shape_key

def keyframe (key, frame):
	bpy.context.scene.frame_current = frame
	did_keyframe = key.keyframe_insert ("value", frame = starting_frame)
	return did_keyframe

# add shape key
audio_key = add_shape_key (obj, custom_key_name)

# add keyframe to shape key value
keyframe (audio_key, 0)
kf = audio_key.value # ? get reference to specific keyframe MODIFIER
print (kf)

# bake sound to the shape key fcurve
set_ctx ('GRAPH_EDITOR')
bpy.ops.graph.sound_bake (filepath=sound_file_path)

# add modifier > envelope > add point
bpy.ops.graph.fmodifier_add(type='ENVELOPE')

## get reference to keyframe envelope
#envelope = kf.modifiers[0]
#print (envelope)

## mess with r, min, max vals (can auto somehow?)
#envelope.reference_value = 0.0
#envelope.default_min = 0.0
#envelope.default_max = 0.8

# add same audio file to vse starting at frame n
set_ctx ('SEQUENCE_EDITOR')
bpy.ops.sequencer.sound_strip_add(filepath=sound_file_path)
sound_strip = bpy.context.scene.sequence_editor.active_strip

# set video to length of the audio
if bpy.context.scene.frame_start == 1:
    bpy.context.scene.frame_start = 0
if bpy.context.scene.frame_end < sound_strip.frame_final_duration:
    bpy.context.scene.frame_end = sound_strip.frame_final_duration

set_ctx ('TEXT_EDITOR')

# Get a specific key
bpy.context.object.data.shape_keys.key_blocks[custom_key_name]
# Get at the fcurve for a key
bpy.context.object.data.shape_keys.animation_data.drivers[0].modifiers[0]