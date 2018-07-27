import bpy
from random import shuffle


## TODO: split by channel
## TODO: ? subshuffle just within blocks of strips

## Shuffle Selected Strips

def move_strips_away(strips):
    initial_start_frame = None
    for s in strips:
        if not initial_start_frame or s.frame_start < initial_start_frame:
            initial_start_frame = s.frame_start
        # TODO instead of moving strips, store current and future placement
        # then consider other workarounds like shrinking/hiding/other
        s.frame_start -= 999999     # move all strips out of the way
    return initial_start_frame

def shuffle_strips(strips):
    strips = sorted(strips, key=lambda x: x.frame_start)
    start_frame = move_strips_away(strips)
    shuffle(strips)
    for s in strips:
        s.frame_start = start_frame
        start_frame += s.frame_final_duration
    return strips

def shuffle_strips_by_channel(strips):
    strips_by_channel = {}
    for strip in strips:
        if not strip.channel in strips_by_channel:
            strips_by_channel[strip.channel] = [strip]
        else:
            strips_by_channel[strip.channel].append(strip)
    for channel_strips in strips_by_channel.values():
        shuffle_strips(channel_strips)
    return strips_by_channel

strips = [s for s in bpy.context.scene.sequence_editor.sequences if s.select]
#start_frame = min([s.frame_start for s in strips])
shuffle_strips(strips)
