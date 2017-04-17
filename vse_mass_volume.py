import bpy
from bpy.props import *

# TODO store prop of "default" vols before tool changes them
original_vols = {}
original_s = bpy.context.scene.sequence_editor.active_strip

# add property volume slider
class MassVolProperties (bpy.types.PropertyGroup):
    mult = FloatProperty(name="Multiply volumes", description="Multiply all volumes")
    base = FloatProperty(name="Set volumes", description="Set all volumes")
    name = StringProperty(name="Contains", description = "Only set strips whose name contains this string.")
    keyframing = BoolProperty(name="Set keyframes")
    def define_defaults(self):
        self.base = 1.0
        self.name = ''
        self.mult = 1.0
        self.keyframing = False
        return None

bpy.utils.register_class(MassVolProperties)
bpy.types.SoundSequence.massvol_props = PointerProperty(type=MassVolProperties)

# volume fade in/out (probably a separate transitions thing)

def set_strip_vol (s, substr, mult_x, new_x):
    if s.type == 'SOUND' and substr in s.name:
        # set the volume proportionally
        s.volume = s.volume * mult_x
        # set the volume
        if new_x == None:
            s.volume = s.massvol_props.base
        else:
            s.volume = new_x
            s.massvol_props.base = new_x
        return True
    else:
        return False

def jump_set_keyframe(strip, mult_x):
    try:
        bpy.ops.screen.keyframe_jump()
        strip.volume = strip.volume * mult_x
        strip.keyframe_set(strip.volume, -1, bpy.context.scene.frame_current)
        jump_set_keyframe(strip)
    # unable to find more keyframes
    except:
        return {'FINISHED'}

# TODO handle keyframes on strips
def handle_keyframes (strip, mult_x):
    #sequence_timeline = #assign timeline frame range
    ## iterate through all frames in strip
    #for frame in range(strip.frame_start, strip.frame_start+strip.frame_final_duration)
    # find first frame
    frame = strip.frame_start
    # set current frame to first frame
    bpy.context.scene.frame_current = frame
    ### TODO test to make sure volume is a keyframe
    # force context to vse strip volume
    strip.volume = strip.volume
    # jump between keyframes and set volumes
    jump_set_keyframe(strip, mult_x)
    return None

class SetMassVolPanel (bpy.types.Panel):
    bl_label = 'Set master volume'
    bl_idname = 'soundsequence.massvol_panel'
    bl_space_type = 'SEQUENCE_EDITOR'
    bl_region_type = 'UI'

    def draw (self, ctx):
        # grab strip
        active_s = bpy.context.scene.sequence_editor.active_strip

        # draw panel with options and operator
        if active_s.type == 'SOUND':
            # base and multiplier inputs
            self.layout.row().prop(active_s.massvol_props, 'base')
            self.layout.row().prop(active_s.massvol_props, 'mult')
            self.layout.row().prop(active_s.massvol_props, 'keyframing')
            # input box for name_contains
            self.layout.row().prop(active_s.massvol_props, 'name')
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
        if active_s.massvol_props.base < 0:
            active_s.massvol_props.base = 0
        if active_s.massvol_props.mult < 0:
            active_s.massvol_props.mult = 0
        
        # only include selected strips
        if len(sounds_by_selection[0]) > 1:
            seqs = sounds_by_selection[0]
        # include all sound strips
        else:
            seqs = sounds_by_selection[0] + sounds_by_selection [1]

        # store new vol multiplicand
        new_vol = None
        if active_s.massvol_props.base != active_s.volume:
            new_vol = active_s.massvol_props.base
        
        # set sound strip volumes
        for s in seqs:
            set_strip_vol (s, active_s.massvol_props.name, s.massvol_props.mult, new_vol)
            # also try to set every single keyframe
            if active_s.massvol_props.keyframing and active_s.massvol_props.name in s.name:
                handle_keyframes (s, active_s.massvol_props.mult)

        # reset multiplier to 1.0
        active_s.massvol_props.mult = 1.0
        active_s.massvol_props.base = active_s.volume

        return {'FINISHED'}


def register ():
    bpy.utils.register_class(SetMassVolOp)
    bpy.utils.register_class(SetMassVolPanel)

register()