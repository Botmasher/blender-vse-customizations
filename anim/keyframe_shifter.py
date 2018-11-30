import bpy

## Keyframe Shifter
##
## Blender Python script by Joshua R (GitHub user Botmasher)
## Description: move all keyframes forward or back in time

scene = bpy.context.scene

# NOTE basic shift on every keyframe in one obj

class KeyframeShifter:
    def __init__(self):
        self.shifted_objects = []
        self.current_object = None
        self.modified_keyframes = {}

    def is_anim_object(self):
        if not (self.current_object and self.current_object.animation_data):
            return False
        if not self.current_object.animation_data.action.fcurves:
            raise Exception("Failed to shift keyframes using keyframe_shifter - object contains no animation fcurves: {0}".format(self.current_object))
            return False
        return True

    def set_obj(self, obj):
        if not is_anim_object(obj):
            return
        self.current_object = obj
        return self.current_object

    def _shift_keyframes(self, frameshift=0):
        """Internal method to shift an object's keyframes forwards or backwards in timeline"""
        obj_fcurves = [*obj.animation_data.action.fcurves]
        modified_kfs = []

        # set all kfs within all anim fcurves
        for fcurve in obj_fcurves:
            for kf in fcurve.keyframe_points:
                modified_kfs.append(kf)

        return modified_kfs

    def shift(self, obj, frameshift=0):
        """Set the current object and run the keyframe shift"""
        current_obj = self.set_obj(obj)
        kfs = self.shift_keyframes(frameshift=frameshift)
        if not (current_obj and kfs and frameshift):
            return
        # TODO revisit storage after allowing separate attr adjustments
        self.modified_keyframes[self.current_object] = kfs
        return kfs

# TODO filter by keyframe attr (like transform, shape, ...)

kf_shifter = KeyframeShifter()
kf_shifter.shift(scene.objects.active, frameshift=10)

# TODO ui
