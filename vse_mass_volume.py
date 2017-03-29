import bpy
from bpy.props import *

# add property volume slider
#bpy.types.SoundSequence.volume_master = bpy.props.FloatProperty(name="Master Volume")
# TODO store prop of "default" vols before tool changes them
original_vols = {}

original_s = bpy.context.scene.sequence_editor.active_strip
adjust_by_x = 0.5

bpy.types.SoundSequence.mass_volume = FloatProperty(name="Mass Volume Factor", description="Multiply all strip volumes by this amount")

def set_vol (s, vol_factor):
    if s.type=='SOUND':
        s.mass_volume = vol_factor
        # set the volume proportionally
        s.volume = s.volume * s.mass_volume
        return True
    else:
        return False

def get_vol (s):
	if s.type == 'SOUND':
		return s.volume
	else:
		return None

# TODO handle keyframes on strips

# TODO - account for x <= 0.0

# add panel and operator classes
class SetMassVolPanel (bpy.types.Panel):
    bl_label = 'Set master volume'
    bl_idname = 'soundsequence.massvol_panel'
    bl_space_type = 'SEQUENCE_EDITOR'
    bl_region_type = 'UI'
    
    def draw (self, ctx):
        active_s = bpy.context.scene.sequence_editor.active_strip
        if active_s.type == 'SOUND':
            self.layout.row().prop(active_s, 'mass_volume')
            self.layout.operator('soundsequence.mass_vol').vol_float = active_s.mass_volume
    
class SetMassVolOp (bpy.types.Operator):
    bl_label = 'Adjust All Audio Strip Volumes'
    bl_idname = 'soundsequence.mass_vol'
    
    vol_float = bpy.props.FloatProperty(name="Mass Volume")
    my_k = None
    
    def execute (self, ctx):
        for s in bpy.context.scene.sequence_editor.sequences:
            set_vol (s, self.vol_float)
        self.report({'INFO'}, "Input event %s" % (self.my_k))
        return {'FINISHED'}
    
    #def invoke (self, ctx, e):
    #    # pay attention to event keypress/input
    #    self.k = e.type
    #    return ctx.window_manager.invoke_props_dialog(self)

def register ():
    bpy.utils.register_class(SetMassVolOp)
    bpy.utils.register_class(SetMassVolPanel)

register()

# TODO add register/unregister/run