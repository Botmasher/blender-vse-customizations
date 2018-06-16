import bpy

## custom screen layer-outer
## /!\ 
## 	- the Blender API has limited support for performing setup and sizing tasks
## 	- recommended to setup and save a custom screen layout instead
## 	- experiment with this code AS a starting point if you're interested
## /!\

modes = ['VSE', 'ANIM']
mode = modes[0]

if mode == 'VSE':
	# splitting areas for VSE
	bpy.context.window.screen = bpy.data.screens['Video Editing']
	bpy.ops.screen.area_split(direction="VERTICAL", factor=0.2)
	bpy.context.screen.areas[1].type = "TIMELINE"
	bpy.context.screen.areas[2].type = "DOPESHEET_EDITOR"
	bpy.context.screen.areas[3].type = "SEQUENCE_EDITOR"
	bpy.context.screen.use_follow = True
	bpy.context.scene.use_audio_sync = True
	bpy.context.scene.use_frame_drop = True
	bpy.context.scene.use_audio_scrub = True
	bpy.context.screen.areas[3].spaces[0].show_locked_time = True
	bpy.context.screen.areas[2].spaces[0].show_frame_indicator = True
	bpy.context.screen.areas[2].spaces[0].show_locked_time = True

elif mode == 'ANIM':
	# splitting areas for 3D anim
	bpy.context.screen.areas[-1].type = "VIEW_3D"
	bpy.ops.screen.area_split(direction="VERTICAL", factor=0.4, mouse_x=-300, mouse_y=20)
	bpy.ops.screen.area_split(direction="HORIZONTAL", factor=0.5)
	bpy.context.screen.areas[-1].type = "CONSOLE"
	bpy.ops.console.insert(text="bpy.ops.screen.area_split(direction=\"HORIZONTAL\", factor=0.5, mouse_x=0, mouse_y=0)")
	bpy.ops.console.execute()
	bpy.context.screen.areas[-1].type = "TEXT_EDITOR"
	bpy.context.screen.use_follow = True
	bpy.context.screen.areas[2].spaces[0].show_frame_indicator = True

else:
	pass
