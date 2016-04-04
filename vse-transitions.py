import bpy
import math

# capture scene name
scene_name = 'Scene'

# attach driver to every strip's channel
#for strip in bpy.data.scenes[scene_name].sequence_editor.sequences_all:
#    strip.select = True
#    strip.driver_add("channel", 0)
#    strip.select = False

def slide_in ():
    x=True
    strip = bpy.data.scenes[scene_name].sequence_editor.active_strip
    parent_strip = strip.input_1
    playhead = bpy.data.scenes[scene_name].frame_current
    if strip.type != "TRANSFORM":
        return False
    if x:
        playhead = strip.frame_start+1
        strip.translate_start_x=110+62
        strip.keyframe_insert("translate_start_x",-1,strip.frame_start+1)
        playhead = strip.frame_start+13
        strip.translate_start_x=0
        strip.keyframe_insert("translate_start_x",-1,strip.frame_start+13)
    return None

class CustomTransitionsPanel (bpy.types.Panel):
    """Creates a Panel in the Strip properties window"""
    bl_label = "Transitions"
    bl_idname = "strip.transitions.panel"
    bl_space_type = 'SEQUENCE_EDITOR'
    bl_region_type = 'UI'
    #bl_context = "PROPERTIES"
    def draw (self, context):
        layout = self.layout
        strip = bpy.data.scene[scene_name].sequence_editor.active_strip
        row = layout.row()
        row.label(text="Strip ")
        row = layout.row()
        row.operator("strip.transitions")

class CustomTransitions (bpy.types.Operator):
    bl_label = "Custom Transitions"
    bl_idname = "strip.transitions"
    bl_description = "Transition in and out"
    def execute(self, context):
        print ("executing")
        return {'FINISHED'}

def register():
    bpy.utils.register_class(CustomTransitionsPanel)
    bpy.utils.register_class(CustomTransitions)

def unregister():
    bpy.utils.unregister_class(CustomTransitions)
    bpy.utils.unregister_class(CustomTransitionsPanel)

if __name__ == "__main__":
    register()
    #unregister()