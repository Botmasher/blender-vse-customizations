import bpy
from collections import deque

## Popin-Popout Objects Sequentially
##
## Handler for executing popin_object across multiple objects
## and staggering the effects
## Example use: popin multiple image planes one after another

## TODO remove popin_object copy - access op instead
## NOTE popin start_frame removed to avoid keying wrong frames
def keyframe_prop(obj, prop_name='', prop_val=None, frame=None):
    """Keyframe a property on object at this frame"""
    if not obj or not prop_name or not prop_val or frame is None: return
    bpy.context.scene.frame_current = frame
    try:
        setattr(obj, prop_name, prop_val)
    except:
        raise Exception("Unable not set {0} on object {1} to value {2}".format(obj, prop_name, prop_val))
    obj.keyframe_insert(data_path=prop_name, frame=frame)
    fc = obj.animation_data.action.fcurves.find(prop_name)  # actually returns fc with all points for prop_name
    return fc

# /!\ edited inline version used in obj iteration below
def popin(obj, scale_frames=0, rebound_frames=0, overshoot_factor=1.0, tiny_size=(0,0,0), reverse=False):
    """Animate a popin or popout effect on one mesh object"""
    full_size = obj.scale.to_tuple()
    # keyframe initial state
    obj_size = full_size if reverse else tiny_size
    keyframe_prop(obj, prop_name='scale', prop_val=obj_size, frame=bpy.context.scene.frame_current)
    # keyframe overshoot state
    bpy.context.scene.frame_current += rebound_frames if reverse else scale_frames
    keyframe_prop(obj, prop_name='scale', prop_val=[x * overshoot_factor for x in full_size], frame=bpy.context.scene.frame_current)
    # keyframe final state
    bpy.context.scene.frame_current += scale_frames if reverse else rebound_frames
    obj_size = tiny_size if reverse else full_size
    keyframe_prop(obj, prop_name='scale', prop_val=obj_size, frame=bpy.context.scene.frame_current)
    return obj
## end copy

def get_deselect_selected(objs):
    deselected_objs = deque([])
    active_obj = None
    for obj in objs:
        if obj == bpy.context.scene.objects.active:
            active_obj = obj
        elif obj.select:
            obj.select = False
            deselected_objs.append(obj)
        else:
            pass
    active_obj and deselected_objs.appendleft(active_obj)
    return objs

def set_selected(objs):
    for obj in objs:
        obj.select = True
    return objs

def get_selected(scene=bpy.context.scene):
    return [obj for obj in bpy.context.scene.objects if obj.select]

def set_active(obj, scene_objects=bpy.context.scene.objects):
    if not obj or not obj.select or not hasattr(scene_objects, 'active'):
        return
    scene_objects.active = obj
    return obj

def unset_active(scene_objects=bpy.context.scene.objects):
    scene_objects.active = None
    return scene_objects.active

class Playhead:
    def __init__(self, scene=bpy.context.scene):
        if not hasattr(scene, 'frame_current'):
            raise Exception("Unable to find timeline playhead for scene {0}".format(scene))
        self.scene = scene

    def get(self):
        return self.scene.frame_current

    def set(self, frame):
        self.scene.frame_current = frame
        return self.get()

    def forward(self, added_frames):
        self.set(self.scene.frame_current + added_frames)
        return self.get()

    def reverse(self, subtracted_frames):
        self.set(self.scene.frame_current - subtracted_frames)
        return self.get()

def deactivate_all():
    objs = bpy.context.scene.objects
    if not objs or not hasattr(objs[0], 'select'):
        return
    for obj in objs:
        obj.select = False
    bpy.context.scene.objects.active = None
    return True

# TODO: allow control of sequence (or at least check following select order)
def popin_sequential(objs=[], popin_op=None, frame_gap=0):
    if not objs or not popin_op:
        return

    playhead = Playhead()

    deactivate_all()

    for obj in objs:
        set_active(obj)
        #popin_op(obj, scale_frames=4, rebound_frames=2, overshoot_factor=1.1)

        # popin effect
        # values
        reverse = False
        full_size = obj.scale.to_tuple()    # pop large size (popin end, popout start)
        overshoot_factor = 1.1              # pop climax size (mid "pop" size)
        tiny_size = (0, 0, 0)               # pop small size (popin start, popout end)
        scale_frames = 4
        rebound_frames = 2
        # keyframe initial state
        obj_size = full_size if reverse else tiny_size
        keyframe_prop(obj, prop_name='scale', prop_val=obj_size, frame=bpy.context.scene.frame_current)
        # keyframe overshoot state
        bpy.context.scene.frame_current += rebound_frames if reverse else scale_frames
        keyframe_prop(obj, prop_name='scale', prop_val=[x * overshoot_factor for x in full_size], frame=bpy.context.scene.frame_current)
        # keyframe final state
        bpy.context.scene.frame_current += scale_frames if reverse else rebound_frames
        obj_size = tiny_size if reverse else full_size
        keyframe_prop(obj, prop_name='scale', prop_val=obj_size, frame=bpy.context.scene.frame_current)

        unset_active()
        obj != objs[len(objs)-1] and frame_gap and playhead.forward(frame_gap)
    return objs

#selected_objects = get_deselect_selected(get_selected())
selected_objects = [obj for obj in bpy.context.scene.objects if obj.select]

popin_sequential(objs=selected_objects, popin_op=popin, frame_gap=2)
