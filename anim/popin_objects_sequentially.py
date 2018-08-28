import bpy
from collections import deque
import selection_utils

## Popin-Popout Objects Sequentially
##
## Handler for executing popin_object across multiple objects
## and staggering the effects
## Example use: popin multiple image planes one after another

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

def set_selected(objs=bpy.context.selected_objects):
    for obj in objs:
        obj.select = True
    return objs

def get_selected():
    return bpy.context.selected_objects

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

def popin(obj, tiny_size=(0, 0, 0), overshoot_factor=1.1, scale_frames=4, rebound_frames=2, reverse=False):
    # values
    full_size = obj.scale.to_tuple()    # pop large size (popin end, popout start)
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

# TODO: allow control of sequence (or at least check following select order)
class OrderedSelection:
    ## allow preserving selection order of selected objects
    def __init__(self):
        self.selected = []

    def reset(self):
        self.selected = []

    def set(self, objs):
        self.selected = objs

    def add(self, obj):
        self.selected = [*self.selected, obj]

    def remove(self, obj):
        self.selected = [o for o in self.selected if o != obj]

    def has(self, obj):
        return obj in self.selected

    def get(self):
        return self.selected

selection = OrderedSelection()

# compare proposed ways of getting selection:
# https://blenderartists.org/t/how-to-get-selection-order/635194/8

def popin_sequential(frame_gap=0):

    selection.set(selection_utils.selected)

    objs = selection.get()

    if not objs:
        return

    playhead = Playhead()

    deactivate_all()

    for obj in objs:
        set_active(obj)

        popin(obj)

        unset_active()
        obj != objs[len(objs)-1] and frame_gap and playhead.forward(frame_gap)

    set_selected(objs)

    return objs

popin_sequential(frame_gap=2)
