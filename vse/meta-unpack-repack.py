import bpy

def is_strip(obj):
    return hasattr(obj, 'bl_rna') and 'Sequence' in obj.rna_type.name

def is_meta(obj):
    return hasattr(obj, 'bl_rna') and obj.bl_rna.name == 'Meta Sequence' and hasattr(obj, 'type') and obj.type == 'META'

def get_selected_strips(strip_type=None):
    strips = []
    for s in bpy.context.scene.sequence_editor.sequences:
        if is_strip(s):
            if not strip_type or s.type == strip_type:
                strips.append(s)
    return strips

def unpack_meta(strip):
    if not is_meta(strip):
        return [strip]
    bpy.ops.sequencer.meta_separate()
    strips = [s for s in bpy.context.scene.sequence_editor.sequences if s.select]
    return strips

def pack_meta(strips):
    if not type(strips) is list:
        return
    packable_strips = []
    for s in strips:
        s.select = True if is_strip(s) else False
    bpy.ops.sequencer.meta_make()
    return packable_strips

def run_op(strips, op):
    return op(strips)

def unpack_add_repack_meta(meta, add_selected=False):

    added_strips = []
    if add_selected:
        added_strips = get_selected_strips()

    strips = unpack_meta(meta)

    # example operation
    #op = bpy.ops.sequencer.gap_insert()
    #run_op(op)

    # add new strips to meta
    strips = [*strips, *added_strips]
    pack_meta(strips)

    return bpy.context.scene.sequence_editor.active_strip

m = bpy.context.scene.sequence_editor.active_strip
unpack_add_repack_meta(m)
