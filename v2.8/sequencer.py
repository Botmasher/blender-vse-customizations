import bpy

# Experimenting with sequencer in 2.8 update
# NOTE: so far api interacted with feels much less overhauled
# than when working with objects in 3D view / scene

# read sequencer data
sequencer = bpy.context.scene.sequence_editor
sequences = sequencer.sequences_all

# add strip
channel = 2
frame_start = 0
sequences.new_image("test", "test.png", channel, frame_start)
strip = sequencer.active_strip
strip.type
strip.elements

# modify strip
def deselect(sequence):
    sequence.select = False
    return sequence.select
[deselect(s) for s in sequences]
strip.select = True
strip.frame_still_end = 50
def flip(sequence):
    sequence.use_flip_x = True
    sequence.use_flip_y = True
flip(strip)

# transform strip
transform_strip = sequences.new_effect(
    "test-transform",
    type="TRANSFORM",
    channel=channel+1,
    frame_start=frame_start,
    seq_1 = strip
    )
transform_strip.use_uniform_scale = False
transform_strip.scale_start_x = 2.0
transform_strip.scale_start_y = 0.5
transform_strip.translate_start_x = 10.0
transform_strip.rotate_start = 5.3

# cut strip
bpy.context.scene.frame_current += 25
bpy.ops.sequencer.cut(Type="SOFT")

# remove strip
sequences.remove(transform_strip)
