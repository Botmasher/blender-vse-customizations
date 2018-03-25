####
# STRIP RECOLOR: VSE COLOR BALANCE MODIFIER ADDER-ADJUSTER
# script by Botmasher (Josh Rudder)
# automatically color balance all image or movie strips in your VSE sequencer!
# Requires:
#  - target strips contain a shared subname findable as a substring in strip names
#  - the strips are already placed in the sequence editor in the named sequencer scene
#  - the color balance strip modifier type='COLOR_BALANCE'
####

import bpy

# scene name for sequencer
sequencer_scene_name = 'Scene'
# string match name within movie strips to color balance
target_strips_name = 'vid-'
# default name of Color Balance modifiers on scene strips for add/remove
color_balance_name = 'Color Balance'
# choose whether to color strips that are desaturated
balance_desaturated = False

# lift, gamma and gain values to adjust color balance
new_lift = [0.97,0.97,1.0]
new_gamma = [0.88,0.83,0.83]
new_gain = [1.45,1.4,1.38]

# search through all sequencer strips
for i in bpy.data.scenes[sequencer_scene_name].sequence_editor.sequences:
    bpy.context.scene.sequence_editor.active_strip=None
    # find strips matching your name pattern
    if target_strips_name in i.name:
        bpy.context.scene.sequence_editor.active_strip=i
        # remove any Color Balance modifiers found on movie strips
        for modifier in i.modifiers:
            if color_balance_name in modifier.name:
                bpy.ops.sequencer.strip_modifier_remove(name=modifier.name)  
        # add one new Color Balance modifier to each movie strip
        try:
            if balance_desaturated or bpy.data.scenes[sequencer_scene_name].sequence_editor.sequences_all[i.name].color_saturation > 0.7:
                bpy.ops.sequencer.strip_modifier_add(type='COLOR_BALANCE')
                # set lift/gamma/gain colors
                bpy.data.scenes[sequencer_scene_name].sequence_editor.sequences_all[i.name].modifiers[color_balance_name].color_balance.lift=new_lift
                bpy.data.scenes[sequencer_scene_name].sequence_editor.sequences_all[i.name].modifiers[color_balance_name].color_balance.gamma=new_gamma
                bpy.data.scenes[sequencer_scene_name].sequence_editor.sequences_all[i.name].modifiers[color_balance_name].color_balance.gain=new_gain                
        except:
            pass
    else:
        pass