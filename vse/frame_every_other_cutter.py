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

def every_other_frame_cut(strip=bpy.context.scene.sequence_editor.active_strip, interval=1):
    if not strip or not hasattr(strip, 'frame_start') or interval < 1:
        return
    strips_remaining = []
    toggle = False
    deselect_strips()
    activate_lone_strip(strip)
    frame = bpy.context.scene.frame_current

    # store method for creating substrip copies of same strip type
    strip_type = strip.type.lower()
    create_strip = getattr(bpy.context.scene.sequence_editor.sequences, 'new_{0}'.format(strip_type))

    # subcut strip and checker cut
    # TODO verify range includes cut within final incomplete interval
    substrips_count = int(strip.frame_final_duration / interval)   # how many frame groups
    for substrip_i in range(substrips_count):

        # TODO use ops to duplicate to keep loaded images
        #bpy.ops.sequencer.duplicate()
        #new_strip = bpy.context.scene.sequence_editor.active_strip

        # move ahead interval frames
        bpy.context.scene.frame_current += interval
        # hard cut strip
        orig_end_length = strip.frame_final_duration
        strip_two = copy_strip(strip, create_new=create_strip, channel=5, frame_start=bpy.context.scene.frame_current)
        strip_two.frame_final_duration = orig_end_length - bpy.context.scene.frame_current - strip.frame_start
        # move ahead interval frames
        bpy.context.scene.frame_current += interval
        # hard cut strip
        new_uncut_strip = create_strip(name=strip.name)
        new_uncut_strip.frame_final_duration = strip.frame_final_duration
        strip.frame_final_duration = bpy.context.scene.frame_current - strip.frame_start
        # select second new strip
        activate_lone_strip(strip_two)
        # remove second new strip
        bpy.ops.sequencer.remove()
        deselect_strips()

        # only one more noncut strip left
        if bpy.context.scene.frame_current + interval > strip.frame_start + strip.length:
            # done cutting
            break

        continue

strips = [strip for strip in bpy.context.scene.sequence_editor.sequences if strip.select]
len(strips) == 1 and every_other_frame_cut(bpy.context.scene.sequence_editor.active_strip)
#len(strips) > 1 and every_other_group_cut(bpy.context.scene.sequence_editor.sequences)
