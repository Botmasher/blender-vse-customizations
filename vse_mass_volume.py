import bpy
from bpy.props import *

# add property volume slider
#bpy.types.SoundSequence.volume_master = bpy.props.FloatProperty(name="Master Volume")
# TODO store prop of "default" vols before tool changes them
original_vols = {}

original_s = bpy.context.scene.sequence_editor.active_strip
adjust_by_x = 0.5

bpy.types.SoundSequence.vol_mass_mult = FloatProperty(name="Multiply volumes", description="Multiply all volumes")
bpy.types.SoundSequence.vol_mass_base = FloatProperty(name="Set volumes", description="Set all volumes")

def set_vol (s, x, calc_type):
    if s.type == 'SOUND' and calc_type == '*':
        # set the volume proportionally
        s.volume = s.volume * x
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
    
    #vol_base = bpy.props.FloatProperty(name='Set Volumes')
    #vol_factor = bpy.props.FloatProperty(name='Multiply Volumes')

    def draw (self, ctx):
        active_s = bpy.context.scene.sequence_editor.active_strip
        if active_s.type == 'SOUND':
            
            # checkbox for selected_only
            # OR test to see if multiple strips selected
            
            # input box for name_contains
            
            self.layout.row().prop(active_s, 'vol_mass_base')
            self.layout.row().prop(active_s, 'vol_mass_mult')
            self.layout.operator('soundsequence.mass_vol')
    
class SetMassVolOp (bpy.types.Operator):
    bl_label = 'Adjust All Audio Strip Volumes'
    bl_idname = 'soundsequence.mass_vol'
    
    def execute (self, ctx):
        active_s = bpy.context.scene.sequence_editor.active_strip
        # user set new volume
        if active_s.vol_mass_base != active_s.volume:
            calc = '='
            x = active_s.vol_mass_base
        # user multiplied volume
        else:
            calc = '*'
            x = active_s.vol_mass_mult
        for s in bpy.context.scene.sequence_editor.sequences:
            set_vol (s, x, calc)
        return {'FINISHED'}
    
    #def invoke (self, ctx, e):
    #    # pay attention to event keypress/input
    #    self.k = e.type
    #    return ctx.window_manager.invoke_props_dialog(self)

def register ():
    bpy.utils.register_class(SetMassVolOp)
    bpy.utils.register_class(SetMassVolPanel)

register()