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

def current_frame_setter():
    scene = bpy.context.scene
    def set_ahead(frames_ahead):
        scene.frame_current += frames_ahead
        return scene.frame_current
    return set_ahead

def is_shape_key(object):
    return object and object.bl_rna and object.bl_rna.name == 'Shape Key'

def set_shape_keyframe(shape_key, key_value):
    if not is_shape_key(shape_key):
        print("Not a shape key: {0}".format(shape_key))
        return
    shape_key.value = key_value
    shape_key.keyframe_insert('value')
    return shape_key

def get_active_shape_key(object):
    return object.active_shape_key

def spike_shape_key(object=bpy.context.object, target_val=1.0, spike_frames=1, left_frames=1, asymmetrical=False, right_frames=1):

    if not object or not hasattr(object, 'active_shape_key') or not target_val or not left_frames:
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
    move_playhead = current_frame_setter()

    # create spike keyframes
    set_shape_keyframe(shape_key, initial_val)
    move_playhead(left_frames)
    set_shape_keyframe(shape_key, target_val)
    move_playhead(spike_frames)
    set_shape_keyframe(shape_key, target_val)
    current_frame = move_playhead(right_frames) if asymmetrical else move_playhead(left_frames)
    set_shape_keyframe(shape_key, initial_val)

    return shape_key

# test run
shapes = {
    'blink': {
        'left': 3,
        'right': 0,
        'mid': 2,
        'asymmetrical': False
    }
}
spike_shape_key(left_frames=shapes['blink']['left'], spike_frames=shapes['blink']['mid'])

def add_props():
    # TODO add props for custom config
    # - number of frames on spike sides
    # - asymmetrical boolean if spike sides have different frames
    # - number of frames on downward side if asymmetrical
    # - number of frames at top of spike
    return

# UI

# TODO add interface
# - discover how to add UI to shape keys tab of object
# Props UI:
# - slider for 0.0-1.0 target value
# - number of frames on spike sides
# - checkbox for asymmetrical sides
#   - if checked show number of frames on return side
# - number of spike frames

class ShapekeySpikePanel (bpy.types.Panel):
    bl_label = "Shapekey Spike"
    bl_context = "objectmode"
    bl_idname = "object.shapekey_spike_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    def draw (self, context):
        obj = bpy.context.object
        rows = [self.layout.row() for i in range(5)]
        # TODO add props
        rows[0].prop(obj, "shapekey_spike_frames_left")
        rows[1].prop(obj, "shapekey_spike_frames_mid")
        rows[2].prop(obj, "shapekey_spike_frames_right")
        rows[3].prop(obj, "shapeky_spike_asymmetrical")
        props = rows[4].operator("object.shapekey_spike", text="Spike Shape Key")
        return

class ShapekeySpikeOperator (bpy.types.Operator):
    bl_label = "Shapekey Spike Operator"
    bl_idname = "object.shapekey_spike"
    bl_description = "Take shape key to a target value then return to original value"

    def execute (self, context):
        obj = bpy.context.object
        hasattr(obj, 'active_shape_key') and spike_shape_key()
        return {'FINISHED'}

def register():
    bpy.utils.register_class(PopinOperator)
    bpy.utils.register_class(PopinPanel)

def unregister():
    bpy.utils.unregister_class(PopinPanel)
    bpy.utils.unregister_class(PopinOperator)

__name__ == '__main__' and register()
