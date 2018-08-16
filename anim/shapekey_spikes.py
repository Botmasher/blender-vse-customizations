import bpy

## Shape Key Spikes
##
## Transition shape key to a new value then return back to original value.
## Optionally flattened spike keys in the middle around the target value.
## Example use: blink plane eyes

# NOTE
# - check for shape keys
# - get active shape key
# - take in target value (see props below; create UI slider)
# - keyframe active to current value
# - move ahead frames
# - keyframe active to target value
# - (optional middle frames at top of spike)
#   - move ahead frames
#   - keyframe active to target value again
# - move ahead frames
# - keyframe active to original value

def current_frame():
    scene = bpy.context.scene
    def set_ahead(frames_ahead):
        scene.frame_current += frames_ahead
    return set_ahead

def shapekey_spike(target_val=1.0):
    sk = bpy.context.scene.objects.active.active_shape_key
    sk_i = bpy.context.scene.objects.active.active_shape_key_index
    sks = bpy.context.scene.objects.active.data.shape_keys
    # get object from sk
    obj = sks.user
    playhead = current_frame()
    return

# TODO add props for custom config
# - number of frames on spike sides
# - asymmetrical boolean if spike sides have different frames
# - number of frames on downward side if asymmetrical
# - number of frames at top of spike

# TODO add interface
# - discover how to add UI to shape keys tab of object
# Props UI:
# - slider for 0.0-1.0 target value
# - number of frames on spike sides
# - checkbox for asymmetrical sides
#   - if checked show number of frames on return side
# - number of spike frames
