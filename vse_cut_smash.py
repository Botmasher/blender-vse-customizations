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
    # Blender UI label, name, placement
    bl_label = 'Soft Cut & Smash'
    bl_idname = 'strip.cut_smash_panel'
    bl_space_type = 'SEQUENCE_EDITOR'
    bl_region_type = 'UI'
    # build the panel
    def draw (self, context):
        # select and execute left or right cut smash
        self.layout.row().prop(bpy.context.scene,'cut_smash_direction', expand=True)
        self.layout.operator('strip.cut_smash', text="Jumpcut Smash")
        self.layout.separator()
        # select and execute marker lifting
        self.layout.row().prop(bpy.context.scene,'lift_marker', expand=True)
        self.layout.prop(bpy.context.scene,'lift_in_marker') 
        self.layout.prop(bpy.context.scene,'lift_out_marker')
        # display button with set or lift text depending on whether markers are set
        if bpy.context.scene.lift_in_marker != '' and bpy.context.scene.lift_out_marker != '':
            self.layout.operator('strip.mark_lift', text="Lift")
        else:
            self.layout.operator('strip.mark_lift', text="Set")

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
    # remove current in-marker if one exists
    if bpy.context.scene.lift_in_marker != '':
            in_marker = bpy.context.scene.timeline_markers[bpy.context.scene.timeline_markers.find(bpy.context.scene.lift_in_marker)]
            bpy.context.scene.timeline_markers.remove(in_marker)
    # add and name a new in-marker at the playhead location 
    playhead = bpy.context.scene.frame_current
    markers = bpy.context.scene.timeline_markers
    bpy.context.scene.lift_in_marker = "in_"+str(playhead)
    markers.new(bpy.context.scene.lift_in_marker,frame=playhead)
    return None

def mark_out ():
    # check that in and out markers exist for lifting and extraction
    if bpy.context.scene.lift_in_marker != '':
        # if both in and out are marked, lift strip between them
        if bpy.context.scene.lift_out_marker != '':
            lift_clip()
        else:
            # reference current frame and timeline markers
            playhead = bpy.context.scene.frame_current
            markers = bpy.context.scene.timeline_markers
            # abort if out frame and in frame match (cannot lift 0 frames)
            if int(bpy.context.scene.lift_in_marker.split("_")[1]) == playhead:
                return {'CANCELLED'}
            # create and name a new out marker at this location
            bpy.context.scene.lift_out_marker = "out_"+str(playhead)
            markers.new(bpy.context.scene.lift_out_marker,frame=playhead)
    else:
        pass
    return None

def lift_clip ():
    # problem: when markers deleted manually, but names still stored
    markers_exist = True

    # find the timeline marker at the index where the key matches marker name
    try:
        in_marker = bpy.context.scene.timeline_markers[bpy.context.scene.timeline_markers.find(bpy.context.scene.lift_in_marker)]
        out_marker = bpy.context.scene.timeline_markers[bpy.context.scene.timeline_markers.find(bpy.context.scene.lift_out_marker)]
    except:
        markers_exist = False
    
    if not markers_exist:
        # no in/out markers found - ghost values leftover from a previous operation
        # Just reset the in/out points and cancel
        bpy.context.scene.lift_in_marker = ''
        bpy.context.scene.lift_out_marker = ''
        return {'CANCELLED'}
        
    # extract the frame number within each marker's name
    in_frame = int(in_marker.name.split('_')[1])
    out_frame = int(out_marker.name.split('_')[1])
    
    # cut selected strips at marked in and out points
    for strip in bpy.context.scene.sequence_editor.sequences_all:
        if strip.select:
            bpy.ops.sequencer.cut (frame=in_frame, type='SOFT')
            bpy.ops.sequencer.cut (frame=out_frame, type='SOFT')
            # - delete the selected strips surrounding lifted segments
            # - move playhead back to initial location
        else:
            pass

    # prepare trash list of edge strips beyond the marked in and out points
    marked_for_deletion = []
    for strip in bpy.context.scene.sequence_editor.sequences_all:
        if strip.select:
            # check if this strip start value doesn't match our new one
            if strip.frame_start + strip.frame_offset_start != in_frame:
                marked_for_deletion.append(strip)

    # toggle to deselect all strips
    bpy.ops.sequencer.select_all()
    
    # select and delete the strips that surround the lifted strip
    for trash in marked_for_deletion:
        trash.select = True
        bpy.ops.sequencer.delete()
    
    # delete the in and out markers
    bpy.context.scene.timeline_markers.remove(in_marker)
    # current code was already removing out_marker, so next command threw not found
    # - tests fine for now but keep an eye on it
    bpy.context.scene.timeline_markers.remove(out_marker)
    
    # reset the in and out properties
    bpy.context.scene.lift_in_marker = ''
    bpy.context.scene.lift_out_marker = ''
    return None

class CutSmashOperator (bpy.types.Operator):
    # Blender UI label, id and description
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