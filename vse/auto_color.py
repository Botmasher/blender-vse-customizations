####
# STRIP RECOLOR: VSE COLOR BALANCE MODIFIER ADDER-ADJUSTER
# script by GitHub user Botmasher (Joshua R)
# automatically color balance all image or movie strips in your VSE sequencer!
# Requires:
#  - target strips contain a shared subname findable as a substring in strip names
#  - the strips are already placed in the sequence editor in the named sequencer scene
#  - the color balance strip modifier type='COLOR_BALANCE'
####

import bpy

# string match name within movie strips to color balance
# TODO more flexible name matching using regex
target_strips_name = 'vid-'

# choose whether to color strips that are desaturated
balance_desaturated = False

# only set selected strips (combine with name to filter)
use_selected = False

# lift, gamma and gain values to adjust color balance
new_lift = [0.97, 0.97, 1.0]
new_gamma = [0.88, 0.83, 0.83]
new_gain = [1.45, 1.4, 1.38]

def recolor_sequence(strip, lift, gamma, gain, modifier_name='Color Balance', remove_existing=True, balance_desaturated=True, desaturated_threshold=0.0):
    """Add and set a color balance modifier on a single sequence"""
    if not hasattr(strip, 'bl_rna') or not strip.bl_rna.name in ['Image Sequence', 'Movie Sequence']:
        return

    # remove any Color Balance modifiers
    if remove_existing:
        for modifier in strip.modifiers:
            remove_modifiers and modifier_name in modifier.name and bpy.ops.sequencer.strip_modifier_remove(name=modifier.name)

    # setup new Color Balance modifier
    if balance_desaturated or strip.color_saturation > desaturated_threshold:
        modifier = strip.modifiers.new(name=modifier_name, type='COLOR_BALANCE')
        # set lift/gamma/gain colors
        modifier.color_balance.lift = lift
        modifier.color_balance.gamma = gamma
        modifier.color_balance.gain = gain

    return strip

def recolor_named_sequences(name_match='', use_selected=False, lift=[], gamma=[], gain=[], balance_desaturated=True):
    """Search through sequences and color balance ones with a matching name"""

    if not lift or not gamma or not gain:
        return

    scene = bpy.context.scene
    bpy.context.scene.sequence_editor_create()

    modified_sequences = []

    # search through all sequencer strips
    for s in scene.sequence_editor.sequences:
        scene.sequence_editor.active_strip = None
        # find strips matching your name pattern
        if name_match in s.name and (not use_selected or s.select):
            print("modifying sequence {0}".format(s.name))
            scene.sequence_editor.active_strip = s
            colored_s = recolor_sequence(s, new_lift, new_gamma, new_gain, balance_desaturated=balance_desaturated)
            colored_s and modified_sequences.append(s)

    return modified_sequences

recolor_named_sequences(name_match=target_strips_name, use_selected=use_selected, lift=new_lift, gamma=new_gamma, gain=new_gain, balance_desaturated=balance_desaturated)
