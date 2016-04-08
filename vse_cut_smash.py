import bpy
from bpy.props import *

bpy.types.Scene.cut_smash_direction = EnumProperty(
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
        self.layout.row().prop(bpy.context.scene,'cut_smash_direction', expand=True)
        # execute button
        self.layout.operator('strip.cut_smash', text="Jumpcut Smash")

def cut_smash_left(memos):
    """Offset selected strips at current frame and close gap with previous strips"""
    # store location of the gap created by this soft cut
    gap = bpy.context.scene.frame_current - 1
    # iterate through all strips in sequencer
    for strip in bpy.context.scene.sequence_editor.sequences_all:
        # check only selected strips that haven't been analyzed
        if strip.select and strip.name not in memos:
            # "soft cut" (offset) the strip and store solution in memos
            try:
                strip.frame_offset_start = bpy.context.scene.frame_current-strip.frame_start
                memos.append(strip.name)
                # run function again to catch any uncut selected strips
                #cut_smash(memos)
            except:
                pass
    # skip to the frame before this strip and close gap
    bpy.context.scene.frame_current = gap
    bpy.ops.sequencer.gap_remove()
    return None

def cut_smash_right (memo):
    print ('cut_smash_right')
    return None

class CutSmashOperator (bpy.types.Operator):
    bl_label = 'Jumpcut Smash'
    bl_idname = 'strip.cut_smash'
    bl_description = 'Cut strip at current location and place against previous strip'
    def execute (self, context):
        # memoization for cut_smash
        memos = []
        if bpy.context.scene.cut_smash_direction == 'left':
            cut_smash_left(memos)
        else:
            cut_smash_right(memos)
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