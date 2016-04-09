import bpy
from bpy.props import *

bpy.types.Scene.cut_smash_direction = EnumProperty(
    items = [('left', 'Left', 'Cut and close gap after playhead'),
             ('right', 'Right', 'Cut and close gap before playhead')],
    name = 'Cut off the:',
    description = 'Where to soft cut frames and close gap for this strip'
    )

class CutSmashPanel (bpy.types.Panel):
    bl_label = 'Soft Cut & Smash'
    bl_idname = 'strip.cut_smash_panel'
    bl_space_type = 'SEQUENCE_EDITOR'
    bl_region_type = 'UI'
    def draw (self, context):
        strip = bpy.context.scene.sequence_editor.active_strip
        self.layout.row().prop(bpy.context.scene,'cut_smash_direction', expand=True)
        # execute button
        self.layout.operator('strip.cut_smash', text="Jumpcut Smash")

def cut_smash_left(memos):
    """Offset beginning of selected strips to current frame and close gap with previous strips"""
    vse = bpy.context.scene.sequence_editor
    # store location of the gap created by this soft cut
    gap = bpy.context.scene.frame_current - 1
    # iterate through all strips in sequencer
    for strip_name in memos:
        # check only selected strips that haven't been analyzed
        if memos[strip_name] == 0:
            # "soft cut" (offset) the strip and store solution in memos
            try:
                vse.sequences_all[strip_name].frame_offset_start = bpy.context.scene.frame_current - vse.sequences_all[strip_name].frame_start
                memos[strip_name] = 1
                # run function again to catch any uncut selected strips
                #cut_smash(memos)
            except:
                pass
    # skip to the frame before this strip and close gap
    bpy.context.scene.frame_current = gap
    bpy.ops.sequencer.gap_remove()
    # set the playhead to new beginning of strip to resume editing at same video location
    if strip_name != None:
        bpy.context.scene.frame_current = vse.sequences_all[strip_name].frame_offset_start + vse.sequences_all[strip_name].frame_start
    return None

def cut_smash_right (memo):
    """Offset end of selected strips to current frame and close gap with next strips"""
    # store shortened reference to sequencer
    vse = bpy.context.scene.sequence_editor
    # store location of the gap created by this soft cut
    playhead = bpy.context.scene.frame_current
    # "soft cut" (offset) the strips and set as solved in memo ('name':1)
    for strip_name in memo:
        # select the sequence and its ending handle
        vse.sequences_all[strip_name].select = True
        vse.sequences_all[strip_name].select_right_handle = True
        bpy.ops.sequencer.snap (frame=playhead)
        vse.sequences_all[strip_name].select = False
        vse.sequences_all[strip_name].select_right_handle = False
        memo[strip_name] = 1
    # close gap to the right of the playhead (note playhead frame is now empty)
    bpy.ops.sequencer.gap_remove()
    return None

class CutSmashOperator (bpy.types.Operator):
    bl_label = 'Jumpcut Smash'
    bl_idname = 'strip.cut_smash'
    bl_description = 'Cut strip at current location and place against previous strip'
    def execute (self, context):
        # memoization for cut_smash
        memos = {}
        for strip in bpy.context.scene.sequence_editor.sequences_all:
            if strip.select:
                memos[strip.name] = 0
                strip.select = False
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