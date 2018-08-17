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
        return scene.frame_current
    return set_ahead

def is_shape_key(object):
    return object and object.bl_rna and object.bl_rna.rna_type == 'Shape Key'

def set_shape_keyframe(shape_key, key_value):
    if not is_shape_key(shape_key):
        return
    shape_key.value = key_value
    shape_key.keyframe_insert('value')
    return shape_key

def get_active_shape_key(object):
    return object.active_shape_key

def spike_shape_key(object=bpy.context.object, target_val=1.0, spike_frames=1, left_frames=1, asymmetrical=False, right_frames=1):

    if not object or not hasattr(object, 'active_shape_key') not target_val or not left_frames:
        return

    shape_key = get_active_shape_key(object)

    if not shape_key:
        return

    initial_val = shape_key.value

    # retrieve other potentially relevant objects
    #shape_key_i = bpy.context.scene.objects.active.active_shape_key_index
    #shape_keys = bpy.context.scene.objects.active.data.shape_keys
    #obj = shape_keys.user

    # store timeline movement method
    move_playhead = current_frame()

    # create spike keyframes
    set_shape_keyframe(shape_key, initial_val)
    move_playhead(left_frames)
    set_shape_keyframe(shape_key, target_val)
    move_playhead(spike_frames)
    set_shape_keyframe(shape_key, target_val)
    current_frame = move_playhead(right_frames) if asymmetrical else move_playhead(left_frames)
    set_shape_keyframe(shape_key, initial_val)

    return shape_key

spike_shape_key()

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
