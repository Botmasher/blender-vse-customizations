import bpy

## Automagical Location/Rotation/Scale Keyframer
##
## author:  Joshua R (Botmasher on GitHub)
## intent:  keyframe a full animation when user changes object transform values

def get_transform(obj, property):
    if type(obj) != 'MESH' or not hasattr(obj, property):
        print("Unrecognized transform property {0} on object {1}".format(property, obj))
        return
    #location = obj.location
    #rotation = obj.rotation_euler
    #scale = obj.scale
    #transforms = {'location': location, 'rotation': rotation, 'scale': scale}
    return getattr(obj, property)

def playhead(scene=bpy.context.scene, frames=0):
    scene.frame_current += frames
    return scene.frame_current

def keyframe_transform(obj, property, length):
    if not hasattr(obj, keyframe_insert):
        print("Cannot keyframe object {0}".format(obj))
        return
    transform = get_transform(obj, property)
    frame = playhead()

    # TODO hold onto transform, wait for input, transform between values
    #   - only run this method on input change?
    #   - where to store base, in instance?

    new_transform = get_transform(obj, property)
    new_frame = playhead(frames=length)
    kf_start = obj.keyframe_insert(property, transform, frame)
    kf_end = obj.keyframe_insert(property, new_transform, new_frame)
    return [kf_start, kf_end]

# TODO adjust anim length based on int prop OR (if boolean) change magnitude
keyframe_transform(bpy.context.scene.objects.active, 'location', 10)
