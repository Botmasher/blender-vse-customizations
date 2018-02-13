import bpy
import re

## Automatically set named Blender attributes from a custom dict
## script by GitHub user Botmasher (Joshua R)
## 
## Can update objects but not add new ones or delete existing ones 
## See example settings below the function definition

# TODO manage cases where a context object's attribute should be set to a dict (example?)
# TODO better error handling

def autoset_attribs(v, k=None, attr_chain=bpy):
	"""Iterate through subdictionaries to find and set attribute leaves on a Blender object
	
	Current setup supports chaining (sub)attributes to either indices or attributes,
	but only assigning values to attributes.

	k -- key in a single {key: value} pair within a dict, representing an attribute
	v -- value in a single {key: value} pair, representing an attribute value or nested attributes
	attr_chain -- dot notation object for setting attribute values or getting further attributes
	"""
	try:
		v
	except NameError:
		raise Exception("Tried to set attribute(s) on %s, but an attribute value was not passed in" % attr_chain)
	# base case - node is an attribute=value pair
	if type(v) is not dict:
		attr_chain = setattr(attr_chain, k, v)
		print("Setting attribute %s to value: %s" % (k, v))
		return attr_chain
	# node is a nested dict - chain the attr and look for subattr values
	if k is not None:
		is_bracketed_str = re.match("\[[\"\'](.+)[\"\']\]", k)
		is_bracketed_int = False if is_bracketed_str else re.match("\[(.+)\]", k)
		# treat as name string (key among set of Blender objects)
		# helps convert e.g. {'collection': {'["Name"]': {'attribute': "value"}}} to collection["Name"].attribute = "value"
		if is_bracketed_str:
			try:
				name = k[2:-2]
				attr_chain = attr_chain[name]
			except:
				raise Exception("Setting attributes - failed to access %s at ['%s']" % (attr_chain, i))
		# treat as integer (index in Blender list)
		# helps convert e.g. {'arr': {'[1]': {'attr': "value"}}} to arr[1].attr = "value"
		elif is_bracketed_int:
			try:
				i = int(k[1:-1])
				attr_chain = attr_chain[i]
			except:
				raise Exception("Setting attributes - failed to access %s at [%s]" % (attr_chain, i))
		else:
			attr_chain = getattr(attr_chain, k)
	# search node for nested subattributes
	for attribute, value in v.items():
		print("Getting attribute %s to chain onto %s" % (k, attr_chain))
		set_named_attributes(value, attribute, attr_chain)

example_settings = {
	'context': {
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
				'resolution_percentage': 100,
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
}