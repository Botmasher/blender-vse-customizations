import bpy
from random import shuffle

## Shuffle Selected Strips

def shuffle_strips(strips, frame):
    lengths = []
    start_frame = None
    for s in strips:
        if not start_frame or s.frame_start < start_frame:
            start_frame = s.frame_start
        lengths.append(s.length)
        s.frame_start -= 9999999999     # move all strips out of the way
    shuffle(strips)
    for s in strips:
        s.frame_start = start_frame
        start_frame += s.length
    return strips

strips = [s for s in bpy.context.scene.sequence_editor.sequences if s.select]
start_frame = min([s.frame_start for s in strips])
shuffle(strips)
