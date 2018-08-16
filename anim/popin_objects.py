import bpy
import bpy.props

## Object Popin-Popout Effect
##
## Blender Python script by Joshua R (GitHub user Botmasher)
##
## Keyframe a pop-in effect on the current object
## 1) translate from outside of view
## 2) resize from tiny to overshoot
## 3) rebound to final size
## An option for reversing this sequence allows you to make a popout animation.
##

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

def popin(obj, start_frame=1, scale_frames=0, rebound_frames=0, overshoot_factor=1.0, tiny_size=(0,0,0), reverse=False):
    """Animate a popin or popout effect on one mesh object"""
    full_size = obj.scale.to_tuple()
    bpy.context.scene.frame_current = start_frame
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

# UI menu properties
def setup_ui_props():
    Scene = bpy.types.Scene
    Scene.popin_frames_scale = bpy.props.IntProperty(name="Scale Frames", description="How long it takes object to scale up to popin", default=6)
    Scene.popin_frames_rebound = bpy.props.IntProperty(name="Rebound Frames", description="How long it takes object to settle after popin", default=2)
    Scene.popin_strength = bpy.props.FloatProperty(name="Strength", description="How much to overshoot object scale on popin", default=1.1)
    Scene.popin_reverse = bpy.props.BoolProperty(name="Reverse", description="Keyframe as scale-down popout instead", default=0)
    return

setup_ui_props()

# UI

class PopinPanel (bpy.types.Panel):
    bl_label = "Popin-Popout Effect"
    bl_category = "Popin-Popout"
    bl_context = "objectmode"
    bl_idname = "object.popin_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    def draw (self, context):
        scene = bpy.context.scene
        rows = [self.layout.row() for i in range(5)]
        # config interface
        rows[0].prop(scene, "popin_frames_scale")
        rows[1].prop(scene, "popin_frames_rebound")
        rows[2].prop(scene, "popin_strength")
        rows[3].prop(scene, "popin_reverse")
        props = rows[4].operator("object.popin_effect", text="Popin Object")
        return

class PopinOperator (bpy.types.Operator):
    bl_label = "Popin-Popout Operator"
    bl_idname = "object.popin_effect"
    bl_description = "Add a customized scale pop-in animation to the 3D object"

    def execute (self, context):
        scene = bpy.context.scene
        obj = bpy.context.scene.objects.active
        frame = bpy.context.scene.frame_current
        if hasattr(obj, 'scale') and hasattr(obj, 'animation_data'):
            popin(obj, start_frame=frame, scale_frames=scene.popin_frames_scale, rebound_frames=scene.popin_frames_rebound, overshoot_factor=scene.popin_strength, reverse=scene.popin_reverse)
            bpy.context.scene.frame_current = frame
        #else:
        #    print("Current object does not support Popin-Popout animations")
        return {'FINISHED'}

def register():
    bpy.utils.register_class(PopinOperator)
    bpy.utils.register_class(PopinPanel)

def unregister():
    bpy.utils.unregister_class(PopinPanel)
    bpy.utils.unregister_class(PopinOperator)

__name__ == '__main__' and register()
