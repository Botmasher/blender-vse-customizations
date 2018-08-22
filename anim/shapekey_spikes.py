import bpy
from bpy.props import *

## Shape Key Spikes
##
## Transition shape key to a new value then return back to original value.
## Optionally flattened spike keys in the middle around the target value.
## Example use: blink plane eyes

def current_frame_setter():
    """Return a function for advancing the scene playhead frame"""
    scene = bpy.context.scene
    def set_ahead(frames_ahead):
        scene.frame_current += frames_ahead
        return scene.frame_current
    return set_ahead

def is_shape_key(object):
    """Check for a shape key"""
    return object and object.bl_rna and object.bl_rna.name == 'Shape Key'

def set_shape_keyframe(shape_key, key_value):
    """Change shape key's value and keyframe at the current frame"""
    if not is_shape_key(shape_key):
        return
    shape_key.value = key_value
    shape_key.keyframe_insert('value')
    return shape_key

def get_active_shape_key(object):
    """Return the active shape key for a given object"""
    return object.active_shape_key

def spike_shape_key(object=bpy.context.object, target_val=1.0, spike_frames=1, left_frames=1, asymmetric=False, right_frames=1):
    """Move and set shape key value to create shape key spike"""
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
    """Define custom properties for the Shapekey Spike UI"""
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

# UI
class ShapeKeySpike (bpy.types.Operator):
    bl_label = "Shapekey Spike Operator"
    bl_idname = "object.shapekey_spike"
    bl_description = "Take shape key to a target value then return to original value"

    def execute (self, context):
        obj = bpy.context.object
        hasattr(obj, 'active_shape_key') and spike_shape_key(left_frames=obj.shapekey_spike_frames_left, spike_frames=obj.shapekey_spike_frames_mid, right_frames=obj.shapekey_spike_frames_right, target_val=obj.shapekey_spike_value, asymmetric=obj.shapekey_spike_asymmetric)
        return {'FINISHED'}

def shape_key_spike_panel(self, context):
    obj = bpy.context.object
    # do not show for relative basis key
    if obj.active_shape_key.relative_key == obj.active_shape_key:
        return
    shapekey_props = [
        "shapekey_spike_value",
        "shapekey_spike_frames_left",
        "shapekey_spike_frames_mid",
        "shapekey_spike_asymmetric"
    ]
    obj.shapekey_spike_asymmetric and shapekey_props.append("shapekey_spike_frames_right")
    self.layout.row().label("Shape Key Spike")
    rows = [self.layout.row().prop(obj, property) for property in shapekey_props]
    self.layout.row().operator("object.shapekey_spike", text="Spike Shape Key")

def register():
    obj = bpy.context.object
    add_shapekey_spike_props()
    bpy.utils.register_class(ShapeKeySpike)
    bpy.types.DATA_PT_shape_keys.append(shape_key_spike_panel)

def unregister():
    bpy.utils.unregister_class(ShapeKeySpike)
    bpy.types.DATA_PT_shape_keys and bpy.types.DATA_PT_shape_keys.remove(shape_key_spike_panel)

if __name__ == '__main__':
    register()
