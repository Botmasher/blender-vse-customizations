import bpy

## Change areas to run contextual bpy.ops methods

def switch_area(new_area=None):
    area = bpy.context.area
    if not area_target or area.type == new_area:
        return
    old_area = area.type
    area.type = new_area
    def switch_area_back():
        area.type = old_area
        return new_area
    return switch_area_back

def build_areas_map():
    # TODO: account for every ops attr
    ops_areas_map = {
        'view3d': 'VIEW_3D',
        'time': 'TIMELINE',
        'graph': 'GRAPH_EDITOR',
        'action': 'DOPESHEET_EDITOR',
        'nla': 'NLA_EDITOR',
        'image': 'IMAGE_EDITOR',
        'clip': 'CLIP_EDITOR',
        'sequencer': 'SEQUENCE_EDITOR',
        'node': 'NODE_EDITOR',
        'text': 'TEXT_EDITOR',
        'logic': 'LOGIC_EDITOR',
        'buttons': 'PROPERTIES',    # /!\ render, buttons, object and many other ops here
        'outliner': 'OUTLINER',
        'wm': 'USER',
        # other proposed maps
        'object': 'VIEW_3D',    # or 'PROPERTIES'?
        'material': 'VIEW_3D',  # or 'PROPERTIES'?
        'texture': 'VIEW_3D'    # or 'PROPERTIES'?
    }
    return ops_areas_map

def switch_areas_run_op(op, params=[]):
    ops_areas = build_areas_map()

    # determine run area and swap areas
    op_id = op.idname_py()
    op_key = op_id.split('.', 1)[0]
    new_area = ops_areas[op_key]
    switchback = switch_area(new_area=new_area)

    # run op
    res = op(*params) if params else op()

    # revert to original area
    switchback()

    return res
