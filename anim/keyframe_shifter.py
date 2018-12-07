import bpy
from bpy.props import IntProperty

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
        prev_obj = self.current_object
        self.current_object = obj
        if not self.is_anim_object():
            self.current_object = prev_obj
            return
        return self.current_object

    def _shift_keyframes(self, frameshift=0):
        """Internal method to shift an object's keyframes forwards or backwards in timeline"""
        obj_fcurves = [*self.current_object.animation_data.action.fcurves]
        modified_kfs = []

        # set all kfs within all anim fcurves
        for fcurve in obj_fcurves:
            for kf in fcurve.keyframe_points:
                kf.co.x += frameshift
                modified_kfs.append(kf)

        return modified_kfs

    def shift(self, obj, frameshift=0):
        """Set the current object and run the keyframe shift"""
        current_obj = self.set_obj(obj)
        kfs = self._shift_keyframes(frameshift=frameshift)
        if not (current_obj and kfs and frameshift):
            return
        # TODO revisit storage after allowing separate attr adjustments
        self.modified_keyframes[self.current_object] = kfs
        return kfs

# TODO filter by keyframe attr (like transform, shape, ...)
kf_shifter = KeyframeShifter()

bpy.types.Scene.keyframe_shifter_frameshift = IntProperty(
    name="Frameshift",
    description="Frames to shift all keyframes along timeline",
    default=1
)

class KfShifterOperator(bpy.types.Operator):
    bl_label = "Keyframe Shifter"
    bl_idname = "object.keyframe_shifter"
    bl_description = "Move an object's keyframes along timeline"

    def execute(self, ctx):
        frameshift = ctx.scene.keyframe_shifter_frameshift
        kf_shifter.shift(ctx.scene.objects.active, frameshift=frameshift)
        return {'FINISHED'}

class KfShifterPanel(bpy.types.Panel):
    bl_label = "Keyframe Shifter"
    bl_idname = "object.keyframe_shifter_panel"
    bl_category = "Keyframe Shifter"
    bl_context = "objectmode"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"

    def draw(self, ctx):
        layout = self.layout
        layout.row().prop(ctx.scene, 'keyframe_shifter_frameshift')
        layout.row().operator("object.keyframe_shifter", text="Shift Keyframes")

def register():
	bpy.utils.register_class(KfShifterOperator)
	bpy.utils.register_class(KfShifterPanel)

def unregister():
	bpy.utils.unregister_class(KfShifterOperator)
	bpy.utils.unregister_class(KfShifterProperties)

if __name__ == '__main__':
	register()
	#unregister()
