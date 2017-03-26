import bpy
from bpy.props import *

# TODO add property volume slider to panel

original_s = bpy.context.scene.sequence_editor.active_strip

adjust_by_x = 0.5
# TODO store prop of "default" vols before tool changes them
original_vols = {}

for s in bpy.context.scene.sequence_editor.sequences:
    if s.type=='SOUND':
        # set the volume proportionally
        s.volume = s.volume * adjust_by_x
    else:
        pass

# handle keyframes on strips
# - account for 0.0

# TODO add panel and operator classes

# TODO add register/unregister/run