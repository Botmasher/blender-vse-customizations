import bpy
from bpy.props import *

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

# NOTE following this path must change transform on loc/rot/scale change
def print_automagic_transform():
    print(bpy.context.scene.object.automagic_transform)
    return

bpy.types.Object.automagic_transform = FloatVectorProperty(
    name="Updated Transform",
    description="Loc/rot/scale being updated",
    subtype='TRANSLATION',
    size=3,
    update=print_automagic_transform
)

bpy.types.Object.automagic_frames = IntProperty(
    name="Total frames",
    description="Frames count for automagic transform anim",
    default=5
)

# TODO adjust anim length based on int prop OR (if boolean) change magnitude
keyframe_transform(bpy.context.scene.objects.active, 'location', 10)

# Watch for changes to object's existing property
# adapted from https://blender.stackexchange.com/questions/19668/execute-a-python-function-whenever-the-user-interacts-with-the-program
def on_change_observer(obj, prop, cb):
    # attempt deep copy of property if method available
    old_value, new_value = (None, None)
    try:
        old_value = getattr(obj, prop).copy()
        new_value = getattr(obj, prop).copy()
    except AttributeError:
        old_value = getattr(obj, prop)
        new_value = getattr(obj, prop)
    def update():
        try:
            old_value = new_value.copy()    # ERROR new_value referenced before assignment
            new_value = getattr(obj, prop).copy()
        except AttributeError:
            old_value = new_value
            new_value = getattr(obj, prop)
        if old_value != new_value:
            return cb(obj, old_value, new_value)
    return update

# task called on update
def on_change_loc(obj, old_loc, new_loc):
    print("from loc {0} to loc {1}".format(old_loc, new_loc))
    return

# instantiate observer
automagic_observer_update = on_change_observer(bpy.context.scene.objects.active, 'location', on_change_loc)

# handler
def observe(scene):
    global automagic_observer_update
    automagic_observer_update()
    return

# add to app handlers
scene_update_handlers = bpy.app.handlers.scene_update_post
observe not in scene_update_handlers and scene_update_handlers.append(observe)
