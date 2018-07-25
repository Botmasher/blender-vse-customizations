import bpy
from random import shuffle

## Shuffle Selected Strips

def move_strips_away(strips):
    original_start_frame
    for s in strips:
        if not start_frame or s.frame_start < start_frame:
            start_frame = s.frame_start
        s.frame_start -= 9999999999     # move all strips out of the way
    return original_start_frame

def shuffle_strips(strips, frame):
    #start_frame = move_strips_away(strips)
    start_frame = strips[0].frame_start
    shuffle(strips)
    for s in strips:
        s.frame_start = start_frame
        start_frame += s.length
    return strips

strips = sorted((s for s in bpy.context.scene.sequence_editor.sequences if s.select), key=lambda x: x.frame_start)
start_frame = min([s.frame_start for s in strips])
shuffle_strips(strips)
