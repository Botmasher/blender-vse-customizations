import bpy

## Every Other Cutter
##
## Checker cut every other frame or every other group of n frames from a strip
## or every other strip or every other group of n strips from a strip group.
## Used for eliminating noise such as motion blur frames in repetitive renders.

# pseudocode sketch

def arrange_strips_by_time(strips, descending=False):
    return sorted(strips, lambda x: x.frame_start, reversed=descending)

def select_strip(strip, deselect=False):
    if not strip or not hasattr(strip, 'frame_start'):
        return
    strip.select = not deselect
    return strip

def deselect_strips():
    for strip in bpy.context.scene.sequence_editor.sequences_all:
        select_strip(strip, deselect=True)
    bpy.context.scene.sequence_editor.active_strip = None

def activate_lone_strip(strip):
    deselect_strips()
    select_strip(strip)
    bpy.context.scene.sequence_editor.active_strip = strip
    return strip

def remove_strip(strip):
    select_strip(strip)
    bpy.context.scene.sequence_editor.active_strip = strip
    # TODO non-ops method of removing sequence and strip data
    try:
        bpy.ops.sequencer.delete()
        return True
    except:
        raise Exception("Unable to delete strip - {0}".format(strip))
    return False

def every_other_group_cut(strips):
    if strips.type != list:
        return
    strips_remaining = []
    toggle = False
    arrange_strips_by_time(strips)
    deselect_strips()
    for strip in strips:
        if toggle:
            remove_strip(strip)
            strips_remaining.append(strip)
        toggle = not odds
    return strips_remaining

def copy_strip(strip, create_new=None, channel=None, frame_start=None):
    if not strip or not create_new:
        return
    path = strip.directory  # /!\ fails to load path for image sequence
    channel = strip.channel if not channel else channel
    frame_start = strip.frame_start if not frame_start else frame_start
    new_strip = create_new(name=strip.name, filepath=path, channel=channel, frame_start=frame_start)
    return new_strip

## Switch ops areas
# TODO: break out area ops exec into own script
def switch_area(area=bpy.context.area, area_type=None):
    if not area or not area_type or area.type == area_type:
        return
    try:
        old_type = area.type
        area.type = area_type
    except:
        raise Exception("Unknown area {0} or area type {1}".format(area, area_type))
    return old_type

def switch_areas_run_op(op):
    """Run a contextual operation in the associated area"""

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

    # determine run area and swap areas
    op_id = op.idname_py()
    op_key = op_id.split('.', 1)[0]
    new_area = ops_areas_map[op_key]
    old_area = switch_area(area_type=new_area)

    # run op
    op()

    # revert to original area
    switch_area(area_type=old_area)

    return

def switch_areas_run_method(area, method, params=[]):
    """Run a method with the current context switched to the target area"""
    old_area = switch_area(area_type=area)
    res = None
    res = method(*params) if params else method()
    switch_area(area_type=old_area)
    return res

## END switch ops areas

def duplicate_strip(strip):
    activate_lone_strip(strip)
    switch_areas_run_op(bpy.ops.sequencer.duplicate)
    new_strip = bpy.context.scene.sequence_editor.active_strip
    return new_strip

def strip_creator(strip):
    # store method for creating substrip copies of same strip type
    strip_type = strip.type.lower()
    try:
        create_strip = getattr(bpy.context.scene.sequence_editor.sequences, 'new_{0}'.format(strip_type))
    except:
        raise Exception("unable to find a new strip creation method on {0}".format(strip))
    return create_strip

def every_other_frame_cut(strip=bpy.context.scene.sequence_editor.active_strip, interval=1):
    if not strip or not hasattr(strip, 'frame_start') or interval < 1:
        return
    strips_remaining = []
    toggle = False
    deselect_strips()
    bpy.context.scene.frame_current = strip.frame_start

    # subcut strip and checker cut
    # TODO verify range includes cut within final incomplete interval
    # TODO allow reverse (neg) strip traversal and checker cutting
    substrip_count = int(strip.frame_final_duration / interval)   # how many frame groups

    strips = [strip]
    checker_cut = False
    print("There are {0} substrips to checker cut".format(substrip_count))

    channel = strip.channel

    for i in range(substrip_count):
        activate_lone_strip(strip)

        # move ahead interval frames
        bpy.context.scene.frame_current += interval

        # copy strip as first strip
        substrip = duplicate_strip(strip)
        strips.append(substrip)

        # cut first strip along interval
        strip.frame_start = bpy.context.scene.frame_current - interval
        substrip.frame_final_duration = bpy.context.scene.frame_current - substrip.frame_start

        # offset internal animation for frames
        strip.animation_offset_start += interval
        strip.frame_start += interval

        # place in channel now that strips are cut
        strip.channel = channel
        substrip.channel = channel

        # remove second strip
        checker_cut and switch_areas_run_op(bpy.ops.sequencer.delete)
        checker_cut = not checker_cut

        deselect_strips()
        continue

    return strips

strips = [strip for strip in bpy.context.scene.sequence_editor.sequences if strip.select]
len(strips) == 1 and every_other_frame_cut(bpy.context.scene.sequence_editor.active_strip, interval=3)
#len(strips) > 1 and every_other_group_cut(bpy.context.scene.sequence_editor.sequences)
