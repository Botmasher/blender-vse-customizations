import bpy
from bpy.props import *

bpy.types.Scene.cut_smash_direction = EnumProperty(
    items = [('left', 'Left', 'Cut and close gap after playhead'),
             ('right', 'Right', 'Cut and close gap before playhead'),
             #('simple', 'Starting cut', 'Cut to start strip for later cut smash')
             ],
    name = 'Type of cut/smash',
    description = 'Where to soft cut frames and close gap for this strip'
    )
    
bpy.types.Scene.lift_marker = EnumProperty(
    items = [('in', 'in', ''),
             ('out', 'out', '')],
    name = 'Chunk marker',
    description = 'Where to start and end extraction for this strip'
    )
        
bpy.types.Scene.lift_in_marker = StringProperty(
    name = 'In point',
    description = 'Marker for the starting point of this cut'
    )

bpy.types.Scene.lift_out_marker = StringProperty(
    name = 'Out point',
    description = 'Marker for the ending point of this cut'
    )

class CutSmashPanel (bpy.types.Panel):
    bl_label = 'Soft Cut & Smash'
    bl_idname = 'strip.cut_smash_panel'
    bl_space_type = 'SEQUENCE_EDITOR'
    bl_region_type = 'UI'
    def draw (self, context):
        # select and execute left or right cut smash
        self.layout.row().prop(bpy.context.scene,'cut_smash_direction', expand=True)
        self.layout.operator('strip.cut_smash', text="Jumpcut Smash")
        self.layout.separator()
        # select and execute marker lifting
        self.layout.row().prop(bpy.context.scene,'lift_marker', expand=True)
        self.layout.prop(bpy.context.scene,'lift_in_marker') 
        self.layout.prop(bpy.context.scene,'lift_out_marker')
        self.layout.operator('strip.mark_lift', text="Lift")

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

def cut_simple (memo):
    """Just cut strips at the current location"""
    for strip in memo:
        bpy.context.scene.sequence_editor.sequences_all[strip].select = True
        # cut operation currently does nothing - set to right context??
        #bpy.ops.sequencer.cut(type='SOFT')
        bpy.context.scene.sequence_editor.sequences_all[strip].select = False
    return None

def mark_in ():
    playhead = bpy.context.scene.frame_current
    markers = bpy.context.scene.timeline_markers
    bpy.context.scene.lift_in_marker = "in_"+str(playhead)
    markers.new(bpy.context.scene.lift_in_marker,frame=playhead)
    return None

def mark_out ():
    # check that in and out markers exist for lifting and extraction
    if bpy.context.scene.lift_in_marker != '':
        if bpy.context.scene.lift_out_marker != '':
            lift_clip()
        else:
            playhead = bpy.context.scene.frame_current
            markers = bpy.context.scene.timeline_markers
            bpy.context.scene.lift_out_marker = "out_"+str(playhead)
            markers.new(bpy.context.scene.lift_out_marker,frame=playhead)
    else:
        pass
    return None

def lift_clip ():
    # find the timeline marker at the index where the key matches in marker name
    in_marker = bpy.context.scene.timeline_markers[bpy.context.scene.timeline_markers.find(bpy.context.scene.lift_in_marker)]
    out_marker = bpy.context.scene.timeline_markers[bpy.context.scene.timeline_markers.find(bpy.context.scene.lift_out_marker)]
    
    # cut and lift strips at this position
    # - cut selected strips at in_marker
    # - cut selected strips at out marker
    # - move cursor position cursor between them
    # - delete the selected strips
    # - move playhead back to initial location
    
    # delete the markers
    bpy.context.scene.timeline_markers.remove(in_marker)
    bpy.context.scene.timeline_markers.remove(out_marker)
    
    # reset the in and out properties
    bpy.context.scene.lift_in_marker = ''
    bpy.context.scene.lift_out_marker = ''
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
        elif bpy.context.scene.cut_smash_direction == 'right':
            cut_smash_right(memos)
        #elif bpy.context.scene.cut_smash_direction == 'simple':
        #    cut_simple(memos)
        else:
            pass
        return{'FINISHED'}

class MarkLiftOperator (bpy.types.Operator):
    bl_label = 'Mark Lift'
    bl_idname = 'strip.mark_lift'
    bl_description = 'Set start and end markers, then lift the selected strip between them'
    def execute (self, context):
        if bpy.context.scene.lift_marker == 'in':
            mark_in()
        elif bpy.context.scene.lift_marker == 'out':
            mark_out()
        else:
            pass
        return{'FINISHED'}
    
def register():
    bpy.utils.register_class(CutSmashPanel)
    bpy.utils.register_class(CutSmashOperator)
    bpy.utils.register_class(MarkLiftOperator)

def unregister():
    bpy.utils.unregister_class(CutSmashPanel)
    bpy.utils.unregister_class(CutSmashOperator)
    bpy.utils.unregister_class(MarkLiftOperator)

if __name__ == '__main__':
    register()
    #unregister()