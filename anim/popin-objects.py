import bpy

## Object Pop-in Effect
##
## Blender Python script by Joshua R (GitHub user Botmasher)
##
## Keyframe a pop-in effect on the current object
## 1) translate from outside of view
## 2) size from tiny to overshoot
## 3) rebound to final size
##

def keyframe_prop(frame, obj, prop_name, prop_val):
    """Keyframe a property on an object at this frame"""
    bpy.context.scene.frame_current = frame
    try:
        setattr(obj, prop_name, prop_val)
    except:
        raise Exception("Unable not set {0} on object {1} to value {2}".format(obj, prop_name, prop_val))
    obj.keyframe_insert(data_path=prop_name)
    fc = obj.animation_data.action.fcurves.find(prop_name)  # actually returns fc with all points for prop_name
    return fc

def popin(obj=bpy.context.scene.objects.active, start_frame=bpy.context.scene.frame_current, hide_vec=(0,0,-1), scale_frames=0, rebound_frames=0):
    end_loc = obj.location
    end_size = obj.scale
    bpy.context.scene.frame_current = start_frame
    # keyframe initial state
    obj.location = end_loc
    obj.scale = (0.0, 0.0, 0.0)
    # keyframe hidden state
    bpy.context.scene.frame_current -= 1
    obj.location = hide_vec
    obj.scale = (0.0, 0.0, 0.0)
    # keyframe overshoot state
    bpy.context.scene.frame_current += (scale_frames + 1)
    obj.location = end_loc
    obj.scale = (1.1, 1.1, 1.1)     # TODO percentage over end_size
    # keyframe final state
    bpy.context.scene.frame_current += (rebound_frames)
    obj.location = end_loc
    obj.scale = end_size
    return obj

def popin_handler(hide_vec=[0,0,0], hide_dir=2, hide_magnitude=0):
    hide_vec[hide_dir] = hide_magnitude
    return popin(hide_vec=hide_vec, scale_frames=scaleup_frames, rebound_frames=rebound_frames)

popin_handler(hide_magnitude=-5, scaleup_frames=6, rebound_frames=3)
