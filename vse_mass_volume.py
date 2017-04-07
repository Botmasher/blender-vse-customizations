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

def set_strip_vol (s, substr, x):
    if s.type == 'SOUND' and substr in s.name:
        # set the volume proportionally
        s.volume = s.volume * s.vol_mass_mult
        # set the volume
        if x == None:
            s.volume = s.vol_mass_base
        else:
            s.volume = x
        return True
    else:
        return False

# TODO handle keyframes on strips
def set_keyframes (strip_vol_path, new_vol):
    adjusted_keyframes = {}
    # for f in bpy.context.scene.animation_data.actions.fcurves:
    #     # new_volume = volume to calculate
    #     if f.data_path in strip_vol_paths:
    #         # adjust the volume at this point
    #         curve = bpy.context.scene.animation_data.actions.fcurves.new(s.path_from_id("volume"))
    #         key = f.keyframe_points.insert(f.keyframe_points.co[0], new_volume)
    #         key.interpolation = 'LINEAR'
    #         # store curve point and location
    #         adjusted_keyframes[f.data_path] = f.keyframe_points.co[0] 
    #     else:
    #         pass
    try:
        f = bpy.context.scene.animation_data.action.fcurves.find(strip_vol_path)
        #new_f = bpy.context.scene.animation_data.action.fcurves.new(s.path_from_id("volume"))
        key = f.keyframe_points.insert(f.keyframe_points.co[0], new_vol)
        key.interpolation = 'LINEAR'
        return True
    except:
        return False

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
            soundstrips = []
            for s in bpy.context.scene.sequence_editor.sequences:
                if s.select and s.type=='SOUND':
                    soundstrips.append(s)
            soundstrips = True if len(soundstrips) > 1 else False
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
        # grab strip
        active_s = bpy.context.scene.sequence_editor.active_strip
        
        # zero out negative values
        if active_s.vol_mass_base < 0:
            active_s.vol_mass_base = 0
        if active_s.vol_mass_mult < 0:
            active_s.vol_mass_mult = 0

        # only include selected strips
        if self.selected_only:
            seqs = [ s for s in bpy.context.scene.sequence_editor.sequences if s.select and s.type == 'SOUND' ]
        # include all sound strips
        else:
            seqs = bpy.context.scene.sequence_editor.sequences

        # store new vol multiplicand
        x = None
        if active_s.vol_mass_base != active_s.volume:
            x = active_s.vol_mass_base
        
        # set sound strip volumes
        for s in seqs:
            ## IF s.volume has no animation data:
                set_strip_vol (s, active_s.vol_mass_name, x)
            ## else:
                strip_paths = set(( s.path_from_id("volume") ))
                set_keyframes (strip_paths)

        # reset multiplier to 1.0
        active_s.vol_mass_mult = 1.0

        return {'FINISHED'}

def register ():
    bpy.utils.register_class(SetMassVolOp)
    bpy.utils.register_class(SetMassVolPanel)

register()