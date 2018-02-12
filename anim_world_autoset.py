import bpy
from mathutils import Vector

## Automatically Set up and Configure my Anim Worlds
## script by GitHub user Botmasher (Joshua R)
## Automatically apply my custom world and render settings when starting up a new animation.
## Used for setting up, keyframing and rendering my core animations (my anim.blend files), not
## for cutting the rendered sequences (my project.blend)

# TODO work for any settings across an entire blender project

# TODO setup the areas / screen panels and their ratios in the window

# TODO split out deleting objects (it's a separate process)

# TODO base settings on a contexts dictionary
# contexts_setup_dict = {
# 	'areas': { 			# or ['window']['areas'] ??
#			{
#				'area_type': {
#					'property_0': {
#						'property_': "value"
#				},
#				...
#				'property_n': "value_n"
#			}
#		},
# 	'area': {}, 		# configure active area
# 	'scenes': {},		# configure specific scenes
# 	'scene': {}, 		# configure 
# 	...
# }

# TODO functions configure a project using contexts_setup_dict
# - read through each key and treat it as an attribute of bpy
# 	- bpy.context for single active objects (bpy.context.area)
#		- bpy.context.window for areas (like bpy.context.window.areas)
# 		- or consistency: expect this from the setup dictionary
# 	- bpy.data for multiple active objects (like bpy.data.scenes)
# - read through each dot notation property until getting to values
# - traverse dictionary depth-first through dictionaries until reaching leaf kvs
# 	- get attribute if the value is another dictionary
# 	- set attribute to value if it's anything else
# 	- catch getting and setting exceptions

# TODO manage cases where a context object's attribute should be set to a dict (example?)

# TODO handle square bracket selection of objects by key/index
# 	- convert {'objects': {'[1]': {'attribute': "value"}}} to objects[1].attribute = "value"
# 	- convert {'objects': {'["Name"]': {'attribute': "value"}}} to objects["Name"].attribute = "value"

def set_named_attributes(v, k=None, attr_chain=bpy):
	"""
	k 					key in a single {key: value} pair within a dict, representing an attribute
	v 					value in a single {key: value} pair, representing an attribute value or nested attributes
	attr_chain 	object onto which attributes are added starting from bpy.context
	"""
	# no kv pairs:
	try:
		v
	except NameError:
		raise Exception("Tried to set attribute(s) on %s, but an attribute value was not passed in" % attr_chain)
	# base case - set the attr value
	if type(v) is not dict:
		attr_chain = setattr(attr_chain, k, v)
		print("Setting attribute %s to value: %s" % (k, v))
		return attr_chain
	# v is a nested dict - chain the attr and look for subattr values
	if k is not None:
		attr_chain = getattr(attr_chain, k)
	# search node for children to get nested subattributes
	for attribute, value in v.items():
		print("Getting attribute %s to chain onto %s" % (k, attr_chain))
		set_named_attributes(value, attribute, attr_chain)

test_attrs_dict = {
	'context': {
		'scene': {
			'render': {
				'resolution_x': 512,
				'resolution_y': 512,
			},
			'frame_start': 2,
			'frame_end': 5,
			'world': {
				'light_settings': {
					'use_environment_light': True,
					'environment_energy': 0.9,
					'gather_method': "RAYTRACE",
					'distance': 0.01,
					'samples': 4
				}
			}
		}
	}
}

set_named_attributes(test_attrs_dict)

setup_dict = {
	'scene': {
		'objects': {
			'["Camera"]': {
				'location': Vector((0.0, 0.0, 5.0)),
				'rotation_euler': (0.0, 0.0, 0.0)
			},
			'["Lamp"]': {
				'location': Vector((-4.0, 1.5, 6.5)),
				'parent': bpy.context.scene.objects['Camera'],
				'data': {
					'energy': 1.1,
					'distance': 25.0,
					'shadow_ray_samples': 3
				}
			}
		},
		'render': {
			'resolution_x': 1920,
			'resolution_y': 1080,
			'antialiasing_samples': "5",
			'alpha_mode': "TRANSPARENT",
			'filepath': "../render/",
			'image_settings': {
				'file_format': "JPEG"
			}
		},
		'frame_start': 1,
		'frame_end': 1500,
		'world': {
			'light_settings': {
				'use_environment_light': True,
				'environment_energy': 0.9,
				'gather_method': "RAYTRACE",
				'distance': 0.01,
				'samples': 4
			}
		}
	},
	'window': {
		'screen': {
			'areas': {
				'[4]': {
					'spaces': {
						'active': {
							'show_manipulator': False
						}
					}
				}
			}
		}
	}
}

# run through areas and adjust custom settings ad hoc
# areas = bpy.context.window.screen.areas
# initial_area = bpy.context.area.type

# for area in areas:
# 	if area.type == "VIEW_3D" and area.spaces[0].type == "VIEW_3D":
# 		area.spaces.active.show_manipulator = False
# 		bpy.context.scene.objects['Lamp'].location = Vector((-2.7, 2.0, 2.5))
# 		bpy.context.scene.objects['Lamp'].parent = bpy.context.scene.objects['Camera']
# 		bpy.context.scene.objects['Lamp'].data.energy = 1.1
# 		bpy.context.scene.objects['Lamp'].data.distance = 25.0
# 		bpy.context.scene.objects['Lamp'].data.shadow_ray_samples = 3 			# check against standard settings
# 		bpy.context.scene.objects['Camera'].location = Vector((0.0, 0.0, 5.0))
# 		bpy.context.scene.objects['Camera'].rotation_euler = (0.0, 0.0, 0.0)
# 		# delete default Cube
# 		bpy.ops.object.select_all(action="DESELECT")
# 		try:
# 			bpy.context.scene.objects['Cube'].select = True
# 		except:
# 			#raise Exception("'Cube' object deleted but no longer exists in bpy.data.objects")
# 			pass 	# TODO handle exception: 'Cube' still selected but no longer exists
# 		bpy.ops.object.delete()
# 		# TODO add plane c standard colors
# 	elif area.type == "PROPERTIES":
# 		bpy.context.scene.render.resolution_x = 1920
# 		bpy.context.scene.render.resolution_y = 1080
# 		bpy.context.scene.frame_start = 1
# 		bpy.context.scene.frame_end = 1500
# 		bpy.context.scene.render.antialiasing_samples = "5"
# 		bpy.context.scene.render.alpha_mode = "TRANSPARENT"
# 		try:
# 			bpy.context.scene.render.filepath = "../render/"
# 		except:
# 			pass
# 		bpy.context.scene.render.image_settings.file_format = "JPEG"
# 		bpy.context.scene.world.light_settings.use_environment_light = True
# 		bpy.context.scene.world.light_settings.environment_energy = 0.9 		# check against standard settings
# 		bpy.context.scene.world.light_settings.gather_method = "RAYTRACE"
# 		bpy.context.scene.world.light_settings.distance = 0.01 							# check against standard settings
# 		bpy.context.scene.world.light_settings.samples = 4 									# check against standard settings
# 	else:
# 		pass
