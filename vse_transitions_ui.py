import bpy
from bpy.props import *
import vse_transitions

bpy.types.TransformSequence.transition_type = EnumProperty(
    items = [('push', 'Push', 'from left to right'),
             ('pull', 'Pull', 'from right to left'),
             ('drop', 'Drop', 'from top to bottom'),
             ('hoist', 'Hoist', 'from bottom to top'),
             ('fade', 'Fade', 'to or from transparent')],
    name = 'Type',
    description = 'Type of transition to add to this strip'
    )

bpy.types.TransformSequence.transition_frames = IntProperty (
    name = 'Duration (frames)', 
    default = 10,
    description = 'Number of frames the transition will last'
    )

bpy.types.TransformSequence.transition_in = BoolProperty(
    name = 'In',
    description = 'Add left edge transition (duration counted forwards from left edge of of this strip)'
    )

bpy.types.TransformSequence.transition_out = BoolProperty(
    name = 'Out',
    description = 'Add right edge transition (duration counted backwards from right edge of this strip)'
    )
    
bpy.types.TransformSequence.transition_mid = BoolProperty(
    name = 'Current Frame',
    description = 'Add transition at this point (duration counted forwards from current frame)'
    )

class CustomTransitionsPanel (bpy.types.Panel):
    """Create a Panel in Strip Properties"""
    bl_label = 'Transitions'
    bl_idname = 'strip.transitions_panel'
    bl_space_type = 'SEQUENCE_EDITOR'
    bl_region_type = 'UI'
    def draw (self, context):
        strip = context.scene.sequence_editor.active_strip
        # drop down menu for selecting transition function
        self.layout.row().prop(strip,'transition_type')
        # integer input for setting transition length in frames
        self.layout.row().prop(strip,'transition_frames')
        # check boxes for toggling transition in/out
        row_1 = self.layout.split(0.4)
        row_1.prop(strip,'transition_in')
        row_1.prop(strip,'transition_out')
        self.layout.row().prop(strip,'transition_mid')
        # execute button
        self.layout.separator()
        self.layout.operator('strip.transitions', text="Keyframe Transition")

class CustomTransitions (bpy.types.Operator):
    bl_label = 'Custom Transitions'
    bl_idname = 'strip.transitions'
    bl_description = 'Use transition settings to create keyframes in active strip'
    def execute (self, context):
        strip = context.scene.sequence_editor.active_strip
        try:
            func = getattr(Transitions,strip.transition_type)
            func(strip.transition_in, strip.transition_out, strip.transition_frames)
        except:
            raise NotImplementedError('Method %s not implemented'%func)
        return{'FINISHED'}

def register():
    bpy.utils.register_class(CustomTransitionsPanel)
    bpy.utils.register_class(CustomTransitions)

def unregister():
    bpy.utils.unregister_class(CustomTransitions)
    bpy.utils.unregister_class(CustomTransitionsPanel)

if __name__ == '__main__':
    register()
    #unregister()