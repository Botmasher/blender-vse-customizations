import bpy

## Every Other Cutter
##
## Checker cut every other frame or every other group of n frames from a strip
## or every other strip or every other group of n strips from a strip group.
## Used for eliminating noise such as motion blur frames in repetitive renders.

def arrange_strips_by_time(strips, descending=False):
    """Sort a list of strips by start frame"""
    return sorted(strips, lambda x: x.frame_start, reversed=descending)

def select_strip(strip, deselect=False):
    """Set one strip's select attribute to True"""
    if not strip or not hasattr(strip, 'frame_start'):
        return
    strip.select = not deselect
    return strip

def deselect_strips():
    """Set all sequencer strips' select attributes to False"""
    for strip in bpy.context.scene.sequence_editor.sequences_all:
        select_strip(strip, deselect=True)
    bpy.context.scene.sequence_editor.active_strip = None

def activate_lone_strip(strip):
    """Deselect all strips and activate only this strip"""
    deselect_strips()
    select_strip(strip)
    bpy.context.scene.sequence_editor.active_strip = strip
    return strip

def run_sequencer_op(op):
    """Switch area to sequence editor and run sequencer op"""
    original_area = bpy.context.area
    sequence_area = 'SEQUENCE_EDITOR'
    bpy.context.area.type = squence_area
    try:
        op()
    except:
        raise Exception("Failed to run op {0} in SEQUENCE_EDITOR".format(op))
    bpy.context.area.type = original_area
    return

def remove_strip(strip):
    """Delete the strip from the sequencer"""
    activate_lone_strip(strip)
    run_sequencer_op(bpy.ops.sequencer.delete)
    return

def duplicate_strip(strip):
    """Make and return a copy of the sequence"""
    activate_lone_strip(strip)
    run_sequencer_op(bpy.ops.sequencer.duplicate)
    new_strip = bpy.context.scene.sequence_editor.active_strip
    return new_strip

def strip_creator(strip):
    """Return new strip creation method accounting for strip type"""
    # store method for creating substrip copies of same strip type
    strip_type = strip.type.lower()
    try:
        create_strip = getattr(bpy.context.scene.sequence_editor.sequences, 'new_{0}'.format(strip_type))
    except:
        raise Exception("unable to find a new strip creation method on {0}".format(strip))
    return create_strip

def every_other_group_cut(strips):
    """Checker cut every other strip in a group of strips"""
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

def every_other_cut(strip=bpy.context.scene.sequence_editor.active_strip, interval=1, is_odd=False):
    """Cut a single strip into substrips of interval length then delete every other substrip"""
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
    checker_cut = is_odd    # T to cut even substrips, F for odd
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
        checker_cut and run_sequencer_op(bpy.ops.sequencer.delete)
        checker_cut = not checker_cut

        deselect_strips()
        continue

    return strips

def handle_strip_cuts(strips=[], use_selected=True):
    """Handler method for checker cutting either one or multiple strips"""
    if not strips and not use_selected:
        return
    if use_selected:
        strips = [strip for strip in bpy.context.scene.sequence_editor.sequences if strip.select]
    if len(strips) == 1:
        every_other_frame_cut(bpy.context.scene.sequence_editor.active_strip, interval=3)
    elif len(strips) > 1:
        every_other_group_cut(bpy.context.scene.sequence_editor.sequences)
    return strips

# run checker cut handler
handle_strip_cuts()
