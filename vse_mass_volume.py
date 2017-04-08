import bpy
from bpy.props import *

# TODO store prop of "default" vols before tool changes them
original_vols = {}
original_s = bpy.context.scene.sequence_editor.active_strip

# add property volume slider
bpy.types.SoundSequence.vol_mass_mult = FloatProperty(name="Multiply volumes", description="Multiply all volumes")
bpy.types.SoundSequence.vol_mass_base = FloatProperty(name="Set volumes", description="Set all volumes")
bpy.types.SoundSequence.vol_mass_name = StringProperty(name="Name contains", description = "Only set if strip name contains")

# volume fade in/out (probably a separate transitions thing)

def set_strip_vol (s, substr, mult_x, new_x):
    if s.type == 'SOUND' and substr in s.name:
        # set the volume proportionally
        s.volume = s.volume * mult_x
        # set the volume
        if new_x == None:
            s.volume = s.vol_mass_base
        else:
            s.volume = new_x
        return True
    else:
        return False

# TODO handle keyframes on strips

# add panel and operator classes
class SetMassVolPanel (bpy.types.Panel):
    bl_label = 'Set master volume'
    bl_idname = 'soundsequence.massvol_panel'
    bl_space_type = 'SEQUENCE_EDITOR'
    bl_region_type = 'UI'
    
    #vol_base = bpy.props.FloatProperty(name='Set Volumes')
    #vol_factor = bpy.props.FloatProperty(name='Multiply Volumes')

    def draw (self, ctx):
        # grab strip and adjust target base volume based on strip volume
        active_s = bpy.context.scene.sequence_editor.active_strip
        active_s.vol_mass_base = active_s.volume

        # draw panel with options and operator
        if active_s.type == 'SOUND':
            # test to see if multiple strips selected
            soundstrips = [ s for s in ]
            for s in bpy.context.scene.sequence_editor.sequences:
                if s.select and s.type=='SOUND':
                    soundstrips.append(s)
            soundstrips = True if len(soundstrips) > 1 else False
            self.layout.row().prop(active_s, 'vol_mass_base')
            self.layout.row().prop(active_s, 'vol_mass_mult')
            # input box for name_contains
            self.layout.row().prop(active_s, 'vol_mass_name')
            self.layout.operator('soundsequence.mass_vol')

class SetMassVolOp (bpy.types.Operator):
    bl_label = 'Adjust All Audio Strip Volumes'
    bl_idname = 'soundsequence.mass_vol'
    
    def execute (self, ctx):
        # grab strip
        active_s = bpy.context.scene.sequence_editor.active_strip
        
        # zero out negative values
        if active_s.vol_mass_base < 0:
            active_s.vol_mass_base = 0
        if active_s.vol_mass_mult < 0:
            active_s.vol_mass_mult = 0

        # build dict of sounds to adjust by selection
        soundstrips_by_sel = {}
        for s in bpy.context.scene.sequence_editor.sequences:
            if s.type == 'SOUND':
                soundstrips_by_sel[str(s.select)] = s
        
        # only include selected strips
        if len(soundstrips_by_sel['True']) > 0:
            seqs = soundstrips_by_sel['True']
        # include all sound strips
        else:
            seqs = [].extend(soundstrips_by_sel['True'], soundstrips_by_sel ['False'])

        # store new vol multiplicand
        new_vol = None
        if active_s.vol_mass_base != active_s.volume:
            new_vol = active_s.vol_mass_base
        
        # set sound strip volumes
        for s in seqs:
            set_strip_vol (s, active_s.vol_mass_name, s.vol_mass_mult, new_vol)

        # reset multiplier to 1.0
        active_s.vol_mass_mult = 1.0

        return {'FINISHED'}

def register ():
    bpy.utils.register_class(SetMassVolOp)
    bpy.utils.register_class(SetMassVolPanel)

register()