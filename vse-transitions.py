import bpy
import math

# capture scene name
scene_name = 'Scene'

# attach driver to every strip's channel
#for strip in bpy.data.scenes[scene_name].sequence_editor.sequences_all:
#    strip.select = True
#    strip.driver_add("channel", 0)
#    strip.select = False

def slide_in ():
    x=True
    strip = bpy.data.scenes[scene_name].sequence_editor.active_strip
    parent_strip = strip.input_1
    playhead = bpy.data.scenes[scene_name].frame_current
    if strip.type != "TRANSFORM":
        return False
    if x:
        playhead = strip.frame_start+1
        strip.translate_start_x=110+62
        strip.keyframe_insert("translate_start_x",-1,strip.frame_start+1)
        playhead = strip.frame_start+13
        strip.translate_start_x=0
        strip.keyframe_insert("translate_start_x",-1,strip.frame_start+13)
    return None

slide_in()