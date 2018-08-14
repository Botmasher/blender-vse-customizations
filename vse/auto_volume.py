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
target_strips_re = '001'

# new target volume to set
updated_volume = 1.92

def is_audio_sequence(obj):
    """Check if the object is a sequencer strip"""
    if obj and hasattr(obj, 'volume'):
        return True
    return False

def set_volume(strip, new_volume):
    """Set the volume value of a sequence"""
    if is_audio_sequence(strip):
        strip.volume = new_volume
        return True
    return False

def filter_strips(strips, match_name='', strip_type='SOUND'):
    """Filter down sequences of a type that have names matching a regex"""
    match_name = '.*' if not match_name else match_name
    r_name = re.compile(match_name)
    matches = []
    for strip in strips:
        match = r_name.search(strip.name)
        match and strip.type == strip_type and matches.append(strip)
    return matches

def get_selected(strips):
    """Return only sequences where select is True"""
    return [strip for strip in strips if strip.select]

def set_mass_volume(strips=bpy.context.scene.sequence_editor.sequences, name='', volume=1.0, selected_only=False):
    """Set the volume for sequences, optionally limiting by name regex or selection"""
    strips = get_selected(strips) if selected_only else strips
    volume_strips = filter_strips(strips, match_name=name)
    print(volume_strips)
    for strip in volume_strips:
        set_volume(strip, volume)
    return volume_strips

set_mass_volume(volume=updated_volume, name=target_strips_re)
