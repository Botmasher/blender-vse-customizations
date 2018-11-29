import bpy

## Keyframe Shifter
##
## Blender Python script by Joshua R (GitHub user Botmasher)
## Description: move all keyframes forward or back in time

scene = bpy.context.scene

# NOTE trial run - shift every keyframe in one obj
def shift_keyframes(obj=None, frameshift=0, is_relative=True):
    """Shift an object's keyframes forwards or backwards in timeline"""
    if not (obj and obj.animation_data and frameshift):
        return

    # set relative to current kf frame xor absolute to frame number
    #   - ? absol very limited use since set all to same frame

    try:
        obj.animation_data.action.fcurves
    except:
        raise Exception("Failed to shift keyframes using keyframe_shifter - object contains no animation fcurves: {0}".format(obj))

    obj_fcurves = [*obj.animation_data.action.fcurves]
    modified_kfs = []

    # set all kfs within all anim fcurves
    for fcurve in obj_fcurves:
        for kf in fcurve.keyframe_points:
            if is_relative:
                kf.co.x += frameshift
            else:
                kf.co.x = frameshift
            modified_kfs.append(kf)

    print(modified_kfs)
    return modified_kfs

# TODO filter by keyframe attr (like transform, shape, ...)

shift_keyframes(obj=scene.objects.active, frameshift=10)
