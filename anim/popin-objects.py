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

hide_dir = 2    # one value from (0,1,2) representing x,y,z
hide_magnitude = -5.0
scaleup_frames = 6
rebound_frames = 3

def pop_in(obj=bpy.context.scene.objects.active, start_frame=bpy.context.scene.frame_current, hide_vec=(0,0,-1), scale_frames=0, rebound_frames=0):
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

hide_vec = [0,0,0]
hide_vec[hide_dir] = hide_magnitude
pop_in(hide_vec=hide_vec, scale_frames=scaleup_frames, rebound_frames=rebound_frames)
