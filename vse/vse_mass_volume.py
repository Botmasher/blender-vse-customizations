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
    selecting = BoolProperty(name="Only Set Selected")
    set_base = BoolProperty(name="Set Base Volumes")
    def define_defaults(self):
        self.base = self.volume
        self.name = ''
        self.mult = 1.0
        self.keyframing = False
        self.selected = False
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

class SetMassVolPanel (bpy.types.Panel):
    bl_label = 'Set master volume'
    bl_idname = 'soundsequence.massvol_panel'
    bl_space_type = 'SEQUENCE_EDITOR'
    bl_region_type = 'UI'

    def draw (self, ctx):
        # grab strip
        active_s = bpy.context.scene.sequence_editor.active_strip
        testbool = False

        # draw panel with options and operator
        if active_s.type == 'SOUND':
            # base and multiplier inputs
            self.layout.row().prop(active_s.massvol_props, 'mult')
            if active_s.massvol_props.set_base:
                self.layout.row().prop(active_s.massvol_props, 'base')
            self.layout.row().prop(active_s.massvol_props, 'set_base')
            self.layout.row().prop(active_s.massvol_props, 'selecting')
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
        
        # zero out negative values
        if active_s.massvol_props.base < 0:
            active_s.massvol_props.base = 0
        if active_s.massvol_props.mult < 0:
            active_s.massvol_props.mult = 0
        
        # store new vol multiplicand
        new_vol = None
        if active_s.massvol_props.set_base:
            new_vol = active_s.massvol_props.base
        
        # set sound strip volumes
        for s in bpy.context.scene.sequence_editor.sequences:
            # compare bools to filter all or just selected
            if active_s.massvol_props.selecting - s.select <= 0:
                set_strip_vol (s, active_s.massvol_props.name, s.massvol_props.mult, new_vol)
        
        # reset multiplier to 1.0
        active_s.massvol_props.mult = 1.0
        active_s.massvol_props.base = active_s.volume

        return {'FINISHED'}


def register ():
    bpy.utils.register_class(SetMassVolOp)
    bpy.utils.register_class(SetMassVolPanel)

register()