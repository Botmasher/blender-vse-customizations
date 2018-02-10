import bpy

## Automatically Set up and Configure my Anim Worlds
## script by GitHub user Botmasher (Joshua R)
## Automatically apply my custom world and render settings when starting up a new animation.
## Used for setting up, keyframing and rendering my core animations (my anim.blend files), not
## for cutting the rendered sequences (my project.blend)

areas = bpy.context.window.screen.areas
initial_area = bpy.context.area.type

# TODO setup the areas / screen panels and their ratios in the window

for area in areas:
	if area.type == "VIEW_3D" and area.spaces[0].type == "VIEW_3D":
		area.spaces.active.show_manipulator = False
		bpy.context.scene.objects['Camera'].location = Vector((0.0, 0.0, 5.0))
		bpy.context.scene.objects['Camera'].rotation = Vector((0.0, 0.0, 90.0))
		bpy.context.scene.objects['Lamp'].location = Vector((-4.0, 1.5, 6.5))
		bpy.context.scene.objects['Lamp'].parent = bpy.context.scene.objects['Camera']
		bpy.context.scene.objects['Lamp'].energy = 1.1
		bpy.context.scene.objects['Lamp'].distance = 25.0
		bpy.context.scene.objects['Lamp'].shadow_ray_samples = 3 	# check against standard settings
		# TODO delete the default cube
		bpy.context.scene.objects['Cube']
	elif area.type == "PROPERTIES":
		bpy.context.scene.render.resolution_x = 1920
		bpy.context.scene.render.resolution_y = 1080
		bpy.context.scene.frame_start = 1
		bpy.context.scene.frame_end = 1500
		bpy.context.scene.render.antialiasing_samples = 5
		bpy.context.scene.render.alpha_mode = "TRANSPARENT"
		try:
			bpy.context.scene.render.filepath = "../render/"
		except:
			pass
		bpy.context.scene.render.image_settings.file_format = "JPG"
		bpy.context.scene.world.light_settings.use_environment_light = True
		bpy.context.scene.world.light_settings.environment_energy = 0.9
		bpy.context.scene.world.light_settings.gather_method = "RAYTRACE"
		bpy.context.scene.world.light_settings.distance = 0.01
		bpy.context.scene.world.light_settings.samples = 4
	else:
		pass