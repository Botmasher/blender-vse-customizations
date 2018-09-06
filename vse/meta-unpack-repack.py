import bpy

def is_strip(obj):
    return hasattr(obj, 'bl_rna') and 'Sequence' in obj.rna_type.name

def has_meta_rna(obj):
    return hasattr(obj, 'bl_rna') and obj.bl_rna.name == 'Meta Sequence'

def has_meta_type(obj):
    return hasattr(obj, 'type') and obj.type == 'META'

def unpack_meta(strip):
    if not has_meta_type(strip):
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

def unpack_repack(meta):
    strips = unpack_meta(meta)
    op = bpy.ops.sequencer.gap_insert()     # example operation
    run_op(op)
    pack_meta(strips)
    return

m = bpy.context.scene.sequence_editor.active_strip
unpack_meta(m)
