import bpy
import re

####
# MASS AUDIO VOLUME SET
# script by GitHub user Botmasher
# automatically adjust the volume of audio strips in your VSE sequencer!
####

# scene name for sequencer
sequencer_scene_name = 'Scene'
# string match name within audio strips to edit
target_strips_name = 'audio-'

# new target volume to set
updated_volume = 1.92

def is_audio_sequence(obj):
    if obj and hasattr(obj, 'volume'):
        return True
    return False

def set_volume(strip, new_volume):
    if is_audio_sequence(strip):
        strip.volume = new_volume
        return True
    return False

def filter_strips(strips, match_name, strip_type='AUDIO'):
    r_name = re.compile(match_name)
    matches = []
    for strip in strips:
        match = re.match(r_name, strip.name)
        match and strip.type == strip_type and matches.append(strip)
    return matches

def handle_mass_vol(strips=bpy.context.scene.sequence_editor.sequences, name='', volume=1.0):
    target_strips = filter_strips(strips, match_name=name)
    for strip in target_strips:
        set_volume(strip, volume)
    return strips

handle_mass_vol(volume=updated_volume)
