import bpy
from bpy.props import *

# add property volume slider
#bpy.types.SoundSequence.volume_master = bpy.props.FloatProperty(name="Master Volume")
# TODO store prop of "default" vols before tool changes them
original_vols = {}

original_s = bpy.context.scene.sequence_editor.active_strip
adjust_by_x = 0.5

bpy.types.SoundSequence.mass_volume = FloatProperty(name="Multiply Volumes", description="Multiply all volumes")

def set_vol (s, x, calc_type):
    if s.type == 'SOUND' and calc_type == '*':
        s.mass_volume = x
        # set the volume proportionally
        s.volume = s.volume * s.mass_volume
        return True
    elif s.type == 'SOUND' and calc_type == '=':
        s.volume = x
        return True
    else:
        return False

# TODO only adjust subset with a certain name or id

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
    
    vol_base = bpy.props.FloatProperty(name='Set Volumes')
    vol_factor = bpy.props.FloatProperty(name='Multiply Volumes')

    def draw (self, ctx):
        active_s = bpy.context.scene.sequence_editor.active_strip
        if active_s.type == 'SOUND':
            self.layout.row().prop(self, 'vol_base')
            self.layout.row().prop(self, 'vol_factor')
            self.layout.operator('soundsequence.mass_vol').vol_factor = active_s.mass_volume
    
class SetMassVolOp (bpy.types.Operator):
    bl_label = 'Adjust All Audio Strip Volumes'
    bl_idname = 'soundsequence.mass_vol'
    
    vol_base = bpy.props.FloatProperty(name='Set Volumes')
    vol_factor = bpy.props.FloatProperty(name='Multiply Volumes')
    
    def execute (self, ctx):
        if self.vol_factor != bpy.context.scene.sequence_editor.active_strip.mass_volume:
            calc = '*'
        else:
            calc = '='
        for s in bpy.context.scene.sequence_editor.sequences:
            set_vol (s, self.vol_float, calc)
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