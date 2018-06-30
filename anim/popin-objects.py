import bpy
from bpy.props import *

## Object Pop-in Effect
##
## Blender Python script by Joshua R (GitHub user Botmasher)
##
## Keyframe a pop-in effect on the current object
## 1) translate from outside of view
## 2) resize from tiny to overshoot
## 3) rebound to final size
##

# TODO reverse popout effect

def keyframe_prop(obj, prop_name='', prop_val=None, frame=None):
    """Keyframe a property on an object at this frame"""
    if not obj or not prop_name or not prop_val or not frame: return
    bpy.context.scene.frame_current = frame
    try:
        setattr(obj, prop_name, prop_val)
    except:
        raise Exception("Unable not set {0} on object {1} to value {2}".format(obj, prop_name, prop_val))
    obj.keyframe_insert(data_path=prop_name, frame=frame)
    fc = obj.animation_data.action.fcurves.find(prop_name)  # actually returns fc with all points for prop_name
    return fc

def popin(obj=bpy.context.scene.objects.active, start_frame=bpy.context.scene.frame_current, hide_vec=(0,0,-1), scale_frames=0, rebound_frames=0, overshoot_factor=1.0):
    end_loc = obj.location.to_tuple()
    end_size = obj.scale.to_tuple()
    bpy.context.scene.frame_current = start_frame
    # keyframe initial state
    keyframe_prop(obj, prop_name='location', prop_val=end_loc, frame=bpy.context.scene.frame_current)
    keyframe_prop(obj, prop_name='scale', prop_val=(0, 0, 0), frame=bpy.context.scene.frame_current)
    # keyframe hidden state
    bpy.context.scene.frame_current -= 1
    keyframe_prop(obj, prop_name='location', prop_val=hide_vec, frame=bpy.context.scene.frame_current)
    keyframe_prop(obj, prop_name='scale', prop_val=(0, 0, 0), frame=bpy.context.scene.frame_current)
    # keyframe overshoot state
    bpy.context.scene.frame_current += (scale_frames + 1)
    keyframe_prop(obj, prop_name='location', prop_val=end_loc, frame=bpy.context.scene.frame_current)
    keyframe_prop(obj, prop_name='scale', prop_val=[x * overshoot_factor for x in end_size], frame=bpy.context.scene.frame_current)
    # keyframe final state
    bpy.context.scene.frame_current += (rebound_frames)
    keyframe_prop(obj, prop_name='location', prop_val=end_loc, frame=bpy.context.scene.frame_current)
    keyframe_prop(obj, prop_name='scale', prop_val=end_size, frame=bpy.context.scene.frame_current)
    return obj

def popin_handler(hide_vec=[0,0,0], hide_dir=2, hide_magnitude=0, scale_frames=0, rebound_frames=0):
    hide_vec[hide_dir] = hide_magnitude
    return popin(hide_vec=hide_vec, scale_frames=scale_frames, rebound_frames=rebound_frames)

popin_handler(hide_magnitude=-5, scale_frames=7, rebound_frames=3)


# UI menu properties
# def setup_ui_props():
# 	Obj = bpy.types.Object
# 	Obj.hide_vec = CollectionProperty(name="Hide Vector", description="Offscreen location to hide the popin object", default=[0, 0, 0])
#     Obj.hide_dir = IntProperty(name="Hide Direction", description="Index of X, Y or Z (0, 1 or 2) to set popin object hiding direction", min=0, max=2)
#     Obj.hide_magnitude = FloatProperty(name="Hide Magnitude", description="How far to move the popin object when hiding - used with hide direction", default=0)
#     Obj.scale_frames = IntProperty(name="Scale Frames", description="How long it takes object to scale up to popin", default=0)
#     Obj.rebound_frames = IntProperty(name="Rebound Frames", description="How long it takes object to settle after popin", default=0)
#     Obj.popin_strength = FloatProperty(name="Popin Strength", description="How much to overshoot object scale on popin", default=1)
# 	return

## TODO revamp hiding params (is scale enough?)

popin_params = {
    'hide_vec' : CollectionProperty(name="Hide Vector", description="Offscreen location to hide the popin object", default=[0, 0, 0])
    'hide_dir' : IntProperty(name="Hide Direction", description="Index of X, Y or Z (0, 1 or 2) to set popin object hiding direction", min=0, max=2)
    'hide_magnitude' : FloatProperty(name="Hide Magnitude", description="How far to move the popin object when hiding - used with hide direction", default=0)
    'scale_frames' : IntProperty(name="Scale Frames", description="How long it takes object to scale up to popin", default=0)
    'rebound_frames' : IntProperty(name="Rebound Frames", description="How long it takes object to settle after popin", default=0)
    'popin_strength' : FloatProperty(name="Popin Strength", description="How much to overshoot object scale on popin", default=1)
}

# UI

class PopinPanel (bpy.types.Panel):
    bl_label = "Popin Panel"
    bl_idname = 'object.popin_panel'
    bl_space_type = '3D_VIEW'
    bl_region_type = 'UI'
    def draw (self, context):
        row = self.layout.row()
        row.operator("object.popin_effect", text="Popin Object")
        return

class PopinOperator (bpy.types.Operator):
    bl_label = "Popin Operator"
    bl_idname = 'object.popin_effect'
    bl_description = "Add a customized scale pop-in animation to the 3D object"
    def execute (self, context):
        popin_handler(hide_vec=popin_params['hide_vec'], hide_dir=popin_params['hide_dir'], hide_magnitude=popin_params['hide_magnitude'], scale_frames=popin_params['scale_frames'], rebound_frames=popin_params['rebound_frames'])
        return {'FINISHED'}

def register():
    bpy.utils.register_class(PopinOperator)
    bpy.utils.register_class(PopinPanel)

def unregister():
    bpy.utils.unregister_class(PopinPanel)
    bpy.utils.unregister_class(PopinOperator)

__name__ == '__main__' and register()
