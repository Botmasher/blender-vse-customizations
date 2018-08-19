import bpy
from bpy.props import *

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

def spike_shape_key(object=bpy.context.object, target_val=1.0, spike_frames=1, left_frames=1, asymmetric=False, right_frames=1):

    if not object or not hasattr(object, 'active_shape_key') or not target_val or not left_frames:
        return

    shape_key = get_active_shape_key(object)

    if not shape_key:
        return

    initial_val = shape_key.value

    # store timeline movement method
    move_playhead = current_frame_setter()

    # create spike keyframes
    set_shape_keyframe(shape_key, initial_val)
    move_playhead(left_frames)
    set_shape_keyframe(shape_key, target_val)
    move_playhead(spike_frames)
    set_shape_keyframe(shape_key, target_val)
    current_frame = move_playhead(right_frames) if asymmetric else move_playhead(left_frames)
    set_shape_keyframe(shape_key, initial_val)

    return shape_key

def add_shapekey_spike_props():
    O = bpy.types.Object
    # number of frames on spike sides
    O.shapekey_spike_frames_left = IntProperty(name="Side Length", description="Frames to the left and right of spike target value (just left if asymmetric)", default=1)
    # number of frames at top of spike
    O.shapekey_spike_frames_mid = IntProperty(name="Mid Length", description="Frames to hold spike target value", default=1)
    O.shapekey_spike_value = FloatProperty(name="Spike target value", description="", default=1.0)
    # number of frames on downward side if asymmetrical
    O.shapekey_spike_frames_right = IntProperty(name="Right length", description="Frames to the right of spike target value (only if asymmetric)", default=1)
    # spike sides have different frames
    O.shapekey_spike_asymmetric = BoolProperty(name="Asymmetric", description="Option to use different frame counts to the left and right of spike target value", default=False)
    return

class ShapekeySpikePanel (bpy.types.Panel):
    bl_label = "Shapekey Spike"
    bl_context = "objectmode"
    bl_idname = "object.shapekey_spike_panel"
    bl_category = "Shape Keys"
    bl_space_type = "OUTLINER"
    bl_region_type = "WINDOW"
    def draw (self, context):
        obj = bpy.context.object
        rows = [self.layout.row() for i in range(6)]
        rows[0].prop(obj, "shapekey_spike_frames_left")
        rows[1].prop(obj, "shapekey_spike_frames_mid")
        rows[2].prop(obj, "shapekey_spike_value")
        rows[3].prop(obj, "shapekey_spike_frames_right")
        rows[4].prop(obj, "shapeky_spike_asymmetric")
        props = rows[5].operator("object.shapekey_spike", text="Spike Shape Key")
        return

class ShapekeySpikeOperator (bpy.types.Operator):
    bl_label = "Shapekey Spike Operator"
    bl_idname = "object.shapekey_spike"
    bl_description = "Take shape key to a target value then return to original value"

    def execute (self, context):
        obj = bpy.context.object
        if hasattr(obj, 'active_shape_key'):
            spike_shape_key(left_frames=obj.shapekey_spike_frames_left, spike_frames=obj.shapekey_spike_frames_mid, right_frames=obj.shapekey_spike_frames_right, target_val=obj.shapekey_spike_value, asymmetric=obj.asymmetric)
        return {'FINISHED'}

def register():
    add_shapekey_spike_props()
    bpy.utils.register_class(ShapekeySpikeOperator)
    bpy.utils.register_class(ShapekeySpikePanel)

def unregister():
    bpy.utils.unregister_class(ShapekeySpikePanel)
    bpy.utils.unregister_class(ShapekeySpikeOperator)

__name__ == '__main__' and register()
