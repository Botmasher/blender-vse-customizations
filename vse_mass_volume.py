import bpy
from bpy.props import *

# TODO store prop of "default" vols before tool changes them
original_vols = {}
original_s = bpy.context.scene.sequence_editor.active_strip

# add property volume slider
bpy.types.SoundSequence.vol_mass_mult = FloatProperty(name="Multiply volumes", description="Multiply all volumes")
bpy.types.SoundSequence.vol_mass_base = FloatProperty(name="Set volumes", description="Set all volumes")
bpy.types.SoundSequence.vol_mass_name = StringProperty(name="Name contains", description = "Only set strips whose name contains this string.")

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
class SetMassVolOp (bpy.types.Operator):
    bl_label = 'Adjust All Audio Strip Volumes'
    bl_idname = 'soundsequence.mass_vol'

    sounds_by_sel = CollectionProperty()
    
    def execute (self, ctx):
        # grab strip
        active_s = bpy.context.scene.sequence_editor.active_strip
        
        # zero out negative values
        if active_s.vol_mass_base < 0:
            active_s.vol_mass_base = 0
        if active_s.vol_mass_mult < 0:
            active_s.vol_mass_mult = 0

        # only include selected strips
        print (self.sounds_by_sel)
        if len(self.sounds_by_sel[1]['value']) > 0:
            seqs = self.sounds_by_sel[0]
        # include all sound strips
        else:
            seqs = [].extend(self.sounds_by_sel[0] + self.sounds_by_sel [1])
        print (seqs)

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
        #active_s.vol_mass_base = active_s.volume

        # draw panel with options and operator
        if active_s.type == 'SOUND':
            # store strips by selected/unselected to allow execute to adjust a subset
            sounds_sel, sounds_unsel = [],[]
            for s in bpy.context.scene.sequence_editor.sequences:
                if s.type == 'SOUND' and s.select:
                    sounds_sel.append(s)
                elif s.type == 'SOUND' and not s.select:
                    sounds_unsel.append(s)
                else:
                    pass
            self.layout.row().prop(active_s, 'vol_mass_base')
            self.layout.row().prop(active_s, 'vol_mass_mult')
            # input box for name_contains
            self.layout.row().prop(active_s, 'vol_mass_name')
            self.layout.operator('soundsequence.mass_vol').sounds_by_sel = [{'name':'', 'value':sounds_sel}, {'name':'', 'value':sounds_unsel}]

def register ():
    bpy.utils.register_class(SetMassVolOp)
    bpy.utils.register_class(SetMassVolPanel)

register()