import bpy
from bpy.props import *

# add property volume slider
#bpy.types.SoundSequence.volume_master = bpy.props.FloatProperty(name="Master Volume")
# TODO store prop of "default" vols before tool changes them
original_vols = {}

original_s = bpy.context.scene.sequence_editor.active_strip
adjust_by_x = 0.5

def set_vol (s):
	if s.type=='SOUND':
    	# set the volume proportionally
        s.volume = s.volume * s.volume_master
       	return True
    else:
        return False

def get_vol (s):
	if s.type == 'SOUND':
		return s.volume
	else:
		return None

# TODO handle keyframes on strips

# TODO - account for 0.0


# add panel and operator classes
class SetMassVolume (Operator):
	bl_idname = 'SoundSequence.volume_master'
	bl_label = 'Master Volume'
	#bl_region = 'SEQUENCE_EDITOR'

	my_float = bpy.props.FloatProperty(name="Master Volume")

	def execute (self, ctx):
		for s in bpy.context.scene.sequence_editor.sequences:
			set_vol (s)
		return {'FINISHED'}

	def invoke (self, ctx):
		return ctx.window_manager.invoke_props_dialog(self)


def register ():
	bpy.utils.register_class(SetMassVolume)

register()

# TODO add register/unregister/run