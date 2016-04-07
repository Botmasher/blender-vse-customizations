import bpy
from bpy.props import *

bpy.types.Sequence.cut_smash_direction = EnumProperty(
    items = [('left', 'Left', 'Cut and close gap after playhead'),
             ('right', 'Right', 'Cut and close gap before playhead')],
    name = 'Cut off the:',
    description = 'Where to soft cut frames and close gap for this strip'
    )

class CutSmashPanel (bpy.types.Panel):
    bl_label = 'Super Cut & Smash'
    bl_idname = 'strip.cut_smash_panel'
    bl_space_type = 'SEQUENCE_EDITOR'
    bl_region_type = 'UI'
    def draw (self, context):
        strip = bpy.context.scene.sequence_editor.active_strip
        try:
            self.layout.row().prop(strip,'cut_smash_direction', expand=True)
        except:
            # /!\ location: <unknown location>:-1
        # execute button
        self.layout.operator('strip.cut_smash', text="Jumpcut Smash")

class CutSmashOperator (bpy.types.Operator):
    bl_label = 'Jumpcut Smash'
    bl_idname = 'strip.cut_smash'
    bl_description = 'Cut strip at current location and place against previous strip'
    def execute (self, context):
        for strip in context.scene.sequence_editor.sequences_all:
            if strip.select:
                strip.frame_offset_start = bpy.context.scene.frame_current-strip.frame_start
                print (strip)
                # store frame location of the gap created by this soft cut
                #gap = strip.frame_start + strip.frame_offset_start - 1
        # skip to the frame before this strip and close gap
        #context.scene.frame_current = gap
        #bpy.ops.sequencer.gap_remove()
        return{'FINISHED'}

def register():
    bpy.utils.register_class(CutSmashPanel)
    bpy.utils.register_class(CutSmashOperator)

def unregister():
    bpy.utils.unregister_class(CutSmashPanel)
    bpy.utils.unregister_class(CutSmashOperator)

if __name__ == '__main__':
    register()
    #unregister()