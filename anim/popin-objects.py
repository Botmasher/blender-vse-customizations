import bpy

## Object Pop-in Effect
##
## Blender Python script by Joshua R (GitHub user Botmasher)
##
## Keyframe a pop-in effect on the current object
## 1) translate from outside of view
## 2) resize from tiny to overshoot
## 3) rebound to final size
##

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

# TODO add interface with props
