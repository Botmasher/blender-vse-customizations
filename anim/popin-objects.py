import bpy
import bpy.props

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

def popin(obj, start_frame=1, scale_frames=0, rebound_frames=0, overshoot_factor=1.0):
    end_loc = obj.location.to_tuple()
    end_size = obj.scale.to_tuple()
    bpy.context.scene.frame_current = start_frame
    # keyframe initial state
    keyframe_prop(obj, prop_name='location', prop_val=end_loc, frame=bpy.context.scene.frame_current)
    keyframe_prop(obj, prop_name='scale', prop_val=(0, 0, 0), frame=bpy.context.scene.frame_current)
    # keyframe overshoot state
    bpy.context.scene.frame_current += scale_frames
    keyframe_prop(obj, prop_name='location', prop_val=end_loc, frame=bpy.context.scene.frame_current)
    keyframe_prop(obj, prop_name='scale', prop_val=[x * overshoot_factor for x in end_size], frame=bpy.context.scene.frame_current)
    # keyframe final state
    bpy.context.scene.frame_current += rebound_frames
    keyframe_prop(obj, prop_name='location', prop_val=end_loc, frame=bpy.context.scene.frame_current)
    keyframe_prop(obj, prop_name='scale', prop_val=end_size, frame=bpy.context.scene.frame_current)
    return obj

# UI menu properties
def setup_ui_props():
    Obj = bpy.types.Object
    Obj.popin_frames_scale = bpy.props.IntProperty(name="Scale Frames", description="How long it takes object to scale up to popin", default=6)
    Obj.popin_frames_rebound = bpy.props.IntProperty(name="Rebound Frames", description="How long it takes object to settle after popin", default=2)
    Obj.popin_strength = bpy.props.FloatProperty(name="Strength", description="How much to overshoot object scale on popin", default=1.1)
    return

setup_ui_props()

# UI

class PopinPanel (bpy.types.Panel):
    bl_label = "Popin Effect"
    bl_category = "Popin"
    bl_context = "objectmode"
    bl_idname = "object.popin_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    def draw (self, context):
        obj = bpy.context.scene.objects.active
        rows = [self.layout.row() for i in range(4)]
        # config interface
        rows[0].prop(obj, "popin_frames_scale")
        rows[1].prop(obj, "popin_frames_rebound")
        rows[2].prop(obj, "popin_strength")
        props = rows[3].operator("object.popin_effect", text="Popin Object")
        return

class PopinOperator (bpy.types.Operator):
    bl_label = "Popin Operator"
    bl_idname = "object.popin_effect"
    bl_description = "Add a customized scale pop-in animation to the 3D object"

    def execute (self, context):
        obj = bpy.context.scene.objects.active
        frame = bpy.context.scene.frame_current
        if obj.type == 'MESH':
            popin(obj, start_frame=frame, scale_frames=obj.popin_frames_scale, rebound_frames=obj.popin_frames_rebound, overshoot_factor=obj.popin_strength)
            bpy.context.scene.frame_current = frame
        else:
            print("Current object does not support Popin-Popout animations")
        return {'FINISHED'}

def register():
    bpy.utils.register_class(PopinOperator)
    bpy.utils.register_class(PopinPanel)

def unregister():
    bpy.utils.unregister_class(PopinPanel)
    bpy.utils.unregister_class(PopinOperator)

__name__ == '__main__' and register()
