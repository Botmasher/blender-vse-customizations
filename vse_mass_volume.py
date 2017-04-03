import bpy
from bpy.props import *

# TODO store prop of "default" vols before tool changes them
original_vols = {}
original_s = bpy.context.scene.sequence_editor.active_strip

# add property volume slider
bpy.types.SoundSequence.vol_mass_mult = FloatProperty(name="Multiply volumes", description="Multiply all volumes")
bpy.types.SoundSequence.vol_mass_base = FloatProperty(name="Set volumes", description="Set all volumes")
bpy.types.SoundSequence.vol_mass_name = StringProperty(name="Name contains", description = "Only set if strip name contains")

def set_vol (s, x, calc_type, substr):
    if s.type == 'SOUND' and calc_type == '*' and substr in s.name:
        # set the volume proportionally
        s.volume = s.volume * x
        return True
    elif s.type == 'SOUND' and calc_type == '=' and substr in s.name:
        s.volume = x
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
    
    #vol_base = bpy.props.FloatProperty(name='Set Volumes')
    #vol_factor = bpy.props.FloatProperty(name='Multiply Volumes')

    def draw (self, ctx):
        active_s = bpy.context.scene.sequence_editor.active_strip
        if active_s.type == 'SOUND':
            # test to see if multiple strips selected
            soundstrips = []
            for s in bpy.context.scene.sequence_editor.sequences:
                if s.select and s.type=='SOUND':
                    soundstrips.append(s)
            soundstrips = True if len(soundstrips) > 1 else False
            print ("soundstrips is %s!" % str(soundstrips))
            self.layout.row().prop(active_s, 'vol_mass_base')
            self.layout.row().prop(active_s, 'vol_mass_mult')
            # input box for name_contains
            self.layout.row().prop(active_s, 'vol_mass_name')
            self.layout.operator('soundsequence.mass_vol').selected_only=soundstrips

class SetMassVolOp (bpy.types.Operator):
    bl_label = 'Adjust All Audio Strip Volumes'
    bl_idname = 'soundsequence.mass_vol'

    selected_only = BoolProperty(name="Set selected strips only")
    
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
        if self.selected_only:
            seqs = []
            for s in bpy.context.scene.sequence_editor.sequences:
                if s.select and s.type == 'SOUND':
                    seqs.append(s)
        else:
            seqs = bpy.context.scene.sequence_editor.sequences
        for s in seqs:
            (s, x, calc, active_s.vol_mass_name)
        return {'FINISHED'}

def register ():
    bpy.utils.register_class(SetMassVolOp)
    bpy.utils.register_class(SetMassVolPanel)

register()