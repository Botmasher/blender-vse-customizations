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

def unpack_repack_meta(meta, op=None, add_selected=True):

    if not is_meta(meta):
        return

    added_strips = []
    if add_selected:
        added_strips = get_selected_strips()

    strips = unpack_meta(meta)

    op and op()

    # add new strips to meta
    strips = [*strips, *added_strips]
    pack_meta(strips)

    return bpy.context.scene.sequence_editor.active_strip

# example adding selected strips
m = bpy.context.scene.sequence_editor.active_strip
unpack_repack_meta(m)

# example running operation while unpacked
#def op_handler():
#   bpy.ops.sequencer.gap_insert()
#
#unpack_repack(m, op=op_handler)

# example unpacking all meta strips
def unpack_repack_meta_all(op=None):
    for s in bpy.context.scene.sequence_editor.sequences:
        if is_meta(s):
            unpack_repack_meta(s)
            # TODO callback to allow running op once then packing all
#unpack_repack_all()
