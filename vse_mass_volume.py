import bpy
from bpy.props import *

# add property volume slider
#bpy.types.SoundSequence.volume_master = bpy.props.FloatProperty(name="Master Volume")
# TODO store prop of "default" vols before tool changes them
original_vols = {}

original_s = bpy.context.scene.sequence_editor.active_strip
adjust_by_x = 0.5

def set_vol (s):
    if s.type=='SOUND':
        # set the volume proportionally
        s.volume = s.volume * s.volume_master
        return True
    else:
        return False

def get_vol (s):
	if s.type == 'SOUND':
		return s.volume
	else:
		return None

# TODO handle keyframes on strips

# TODO - account for 0.0


# add panel and operator classes
class SetMassVolPanel (bpy.types.Panel):
    bl_idname = 'SOUNDSEQUENCE_volume_master'
    bl_label = 'Set master volume'
    bl_space_type = 'SEQUENCE_EDITOR'
    bl_region_type = 'UI'
    
    def draw (self, ctx):
        self.layout.row(text="asdf")
        self.layout.row.operator('soundsequence.volume_master')
    
    
class SetMassVolOp (bpy.types.Operator):
    bl_idname = 'soundsequence.volume_master'
    bl_label = 'Master Volume'
    
    my_float = bpy.props.FloatProperty(name="Master Volume")
    my_k = None
    
    def execute (self, ctx):
        for s in bpy.context.scene.sequence_editor.sequences:
            set_vol (s)
        self.report({'INFO'}, "Input event %s" % (self.my_k))
        return {'FINISHED'}
    
    def invoke (self, ctx, e):
        # pay attention to event keypress/input
        self.k = e.type
        return ctx.window_manager.invoke_props_dialog(self)

def register ():
    bpy.utils.register_class(SetMassVolOp)
    bpy.utils.register_class(SetMassVolPanel)

register()

# TODO add register/unregister/run