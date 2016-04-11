####
# MASS AUDIO VOLUME SET
# script by Botmasher (Josh Rudder)
# automatically adjust the volume of audio strips in your VSE sequencer!
####

import bpy

# scene name for sequencer
sequencer_scene_name = 'Scene'
# string match name within audio strips to edit
target_strips_name = 'audio-'

# new target volume to set
new_vol = 1.92

# search through all sequencer strips
for i in bpy.data.scenes[sequencer_scene_name].sequence_editor.sequences:
    bpy.context.scene.sequence_editor.active_strip=None
    # find strips matching your name pattern
    if target_strips_name in i.name:
        bpy.context.scene.sequence_editor.active_strip=i
        # adjust the volume of the active strip
        try:
            bpy.data.scenes[sequencer_scene_name].sequence_editor.sequences_all[i.name].volume=new_vol              
        except:
            pass
    else:
        pass