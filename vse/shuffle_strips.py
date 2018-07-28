import bpy
from random import shuffle

## Shuffle Selected Strips
##
## Perform a pseudorandom reordering of selected VSE sequences
## Used for giving variation to repetitive animations like typing or background talking

# TODO:
# - currently iterating over selected strips multiple times
#   - consider what can be done in selected_strips()
# - subshuffle just within blocks of strips
# - optionally move strips into same channel (on base shuffle not by channel)

def move_strips_away(strips):
    """Move sequences out of the way to make space for easy reordering"""
    # /!\ break risk: very long strips or many h of strips
    for s in strips:
        s.frame_start += 999999
    return strips

def swap_two_strips(strip_1, strip_2):
    """Switch the start frame and the channel of two strips"""
    swap_frames = [strip_1.frame_start, strip_2.frame_start]
    swap_channels = [strip_1.channel, strip_2.channel]
    # move one out of the way
    move_strips_away([strip_1])
    # swap
    strip_2.frame_start = swap_frames[0]
    strip_2.channel = swap_channels[0]
    strip_1.frame_start = swap_frames[1]
    strip_1.channel = swap_channels[1]
    return (strip_1, strip_2)

def shuffle_strips(strips):
    """Reorder sequences pseudorandomly along timeline"""
    if not strips or len(strips) < 2: return
    strips = sorted(strips, key=lambda x: x.frame_start)
    start_frame = strips[0].frame_start
    #shuffled_strips = strips[:]
    move_strips_away(strips)
    shuffle(strips)
    for strip in strips:
        strip.frame_start = start_frame
        start_frame += strip.frame_final_duration
    return strips

def shuffle_strips_by_channel(strips):
    """Reorder sequences in the same channel pseudorandomly along timeline"""
    strips_by_channel = {}
    for strip in strips:
        if not strip.channel in strips_by_channel:
            strips_by_channel[strip.channel] = [strip]
        else:
            strips_by_channel[strip.channel].append(strip)
    for channel_strips in strips_by_channel.values():
        shuffle_strips(channel_strips)
    return strips_by_channel

def selected_strips(same_type=False, strip_type=''):
    """List all currently selected sequences"""
    strips = []
    for s in bpy.context.scene.sequence_editor.sequences:
        if s.select:
            if same_type and s.type != strip_type:
                continue
            strips.append(s)
    return strips

shuffle_strips_by_channel(selected_strips())
