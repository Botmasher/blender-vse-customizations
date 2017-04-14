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
            s.vol_mass_base = new_x
        return True
    else:
        return False

def jump_set_keyframe(strip):
    try:
        bpy.ops.screen.keyframe_jump()
        #set_strip_vol(### params needed)
        strip.keyframe_set(strip.volume, -1, current_frame)
        jump_set_keyframe(strip)
    # unable to find more keyframes
    except:
        return {'FINISHED'}

# TODO handle keyframes on strips
def handle_keyframes (strips_list):
    #sequence_timeline = #assign timeline frame range
    # iterate through all frames
    for strip in strips_list:
        ## iterate through all frames in strip
        #for frame in range(strip.frame_start, strip.frame_start+strip.frame_final_duration)
        # find first frame
        frame = strip.frame_start
        # set current frame to first frame
        bpy.context.scene.frame_current = frame
        # jump & set
        ### TODO test to make sure volume is a keyframe
        # force context to vse strip volume
        strip.volume = strip.volume
        jump_set_keyframe(strip)
    # add boolean and toggle to op & panel to decide to run this

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
            # update to match vol - /!\ setting not allowed here
            #active_s.vol_mass_base = active_s.volume
            
            # base and multiplier inputs
            self.layout.row().prop(active_s, 'vol_mass_base')
            self.layout.row().prop(active_s, 'vol_mass_mult')
            # input box for name_contains
            self.layout.row().prop(active_s, 'vol_mass_name')
            self.layout.operator('soundsequence.mass_vol')


# add panel and operator classes
class SetMassVolOp (bpy.types.Operator):
    bl_label = 'Adjust All Audio Strip Volumes'
    bl_idname = 'soundsequence.mass_vol'

    def execute (self, ctx):
        # grab strip
        active_s = bpy.context.scene.sequence_editor.active_strip
        
        # store strips by selected/unselected to allow execute to adjust a subset
        sounds_by_selection = [[],[]]
        for s in bpy.context.scene.sequence_editor.sequences:
            if s.type == 'SOUND' and s.select:
                sounds_by_selection[0].append(s)
            elif s.type == 'SOUND' and not s.select:
                sounds_by_selection[1].append(s)

        # zero out negative values
        if active_s.vol_mass_base < 0:
            active_s.vol_mass_base = 0
        if active_s.vol_mass_mult < 0:
            active_s.vol_mass_mult = 0
        
        # only include selected strips
        if len(sounds_by_selection[0]) > 1:
            seqs = sounds_by_selection[0]
        # include all sound strips
        else:
            seqs = sounds_by_selection[0] + sounds_by_selection [1]

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