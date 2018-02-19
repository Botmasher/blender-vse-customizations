import bpy
import re
from mathutils import Vector

# adjust settings and create and delete objects, materials, textures from a single config dict
# example config dict and instantiation at bottom

# TODO handle new and deleted materials, textures, ...
# TODO delete based on any attribute

class Autoconfig_Anim:
	def __init__(self, create_method_name='new()', delete_method_name='delete()'):
		# nested keys for special setup handling of create and delete
		self.create_method_name = create_method_name
		self.delete_method_name = delete_method_name
		return None

	def try_key_or_index(self, attr_string, attr_chain):
		"""Translate an attribute string surrounded by brackets to a real key or index and access its element"""
		is_bracketed_str = re.match("\[[\"\'](.+)[\"\']\]", attr_string)
		is_bracketed_int = False if is_bracketed_str else re.match("\[(.+)\]", attr_string)
		if not is_bracketed_str and not is_bracketed_int:
			return None
		# treat as name string (key among set of Blender objects)
		# helps convert e.g. {'collection': {'["Name"]': {'attribute': "value"}}} to collection["Name"].attribute = "value"
		if is_bracketed_str:
			try:
				name = attr_string[2:-2]
				return attr_chain[name]
			except:
				raise Exception("Setting attributes - failed to access %s at ['%s']. Scene may be missing an object with this name." % (attr_chain, name))
		# treat as integer (index in Blender list)
		# helps convert e.g. {'arr': {'[1]': {'attr': "value"}}} to arr[1].attr = "value"
		elif is_bracketed_int:
			try:
				i = int(attr_string[1:-1])
				return attr_chain[i]
			except:
				raise Exception("Setting attributes - failed to access %s at [%s]. Index may be out of range for scene objects collection." % (attr_chain, i))
		return None

	def create_objects(self, objects_settings):
		"""Create and setup objects in scene from an array of settings dicts"""
		added_objects = []
		added_object = None
		for object_config in objects_settings:
			# primitive mesh object
			if 'primitive' in object_config:
				try:
					add_primitive = getattr(bpy.ops.mesh, "primitive_%s_add" % object_config['primitive'])
					add_primitive()
					added_obj = bpy.context.scene.objects.active 	# tested: new primitive now active even when multiple prior objects had been selected
				except:
					continue 		# TODO handle cannot add primitive (incl primitive_x_add method not found)
			# blank object
			else:
				added_obj = bpy.data.objects.new(obj.name, None)
				bpy.context.scene.objects.link(added_obj)
			for attr in object_config['attributes']:
				try:
					setattr(added_obj, attr, object_config['attributes'][attr])
				except:
					continue 		# TODO handle reporting what failed to set
			added_objects.append(added_obj)
		return added_objects

	def delete_objects(self, object_names):
		"""Delete existing objects from scene where object name matches a name in the list"""
		# convert names dict to list
		object_names = [obj['name'] for obj in object_names] if type(object_names[0]) == dict else object_names
		try:
			getattr(object_names, "append")
		except:
			return False
		bpy.ops.object.select_all(action="DESELECT")
		for name in object_names:
			try:
				bpy.context.scene.objects[name].select = True
			except:
				pass
			bpy.ops.object.delete()
		return True

	def create_materials(self, materials_settings):
		"""Create and setup data for new materials"""
		added_materials = []
		for material in materials_settings:
			new_material = bpy.data.materials.new(material['name'])
			for attribute in material:
				if attribute != 'name':
					try:
						setattr(new_material, attribute, material[attribute])
					except:
						continue
			added_materials.append(new_material)
		return added_materials

	def delete_materials(self, material_names):
		"""Delete existing materials where material name matches a name in the lsit"""
		# convert names dict to list
		material_names = [mat['name'] for mat in material_names] if type(material_names[0]) == dict else material_names
		try:
			getattr(material_names, "append")
		except:
			return False
		for name in material_names:
			try:
				bpy.data.materials[name].user_clear() 	# set data block user count to 0
			except:
				pass
		return True

	def autoset_attributes(self, v, k=None, attr_chain=bpy):
		"""Iterate through subdictionaries to configure find and set Blender attributes
		
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
		# base case: node is an attribute=value settings pair
		if type(v) is not dict or k in [self.create_method_name, self.delete_method_name]:
			# reached leaf - set attribute value
			if k not in [self.create_method_name, self.delete_method_name]:
				attr_chain = setattr(attr_chain, k, v)
				print("Setting attribute %s to value: %s" % (k, v))
			return attr_chain
		# node is a nested dict: chain the attr and look for subattr values
		if k is not None:
			is_bracketed = self.try_key_or_index(k, attr_chain)		
			if is_bracketed is not None:
				attr_chain = is_bracketed 		# TODO brainstorm counterexamples (any?) where [i]/['k'] directly associated with a value
			else:
				try:
					attr_chain = getattr(attr_chain, k)
				except:
					raise Exception("Unable to get attribute %s on %s" % (k, attr_chain))
		# search node for nested subattributes
		for attribute, value in v.items():
			print("Getting attribute %s to chain onto %s" % (k, attr_chain))
			self.autoset_attributes(value, attribute, attr_chain)

	def set_config(self, config_dict):
		if type(config_dict) is dict:
			self.config = config_dict
			return True
		else:
			return False

	def get_config(self):
		return self.config

	def setup(self, config_dict=None):
		if config_dict is not None:
			self.set_config(config_dict)
		# delete objects based on array under key 'delete()'
		try:
			objects_to_delete = config_dict['data']['objects'][self.delete_method_name]
			self.delete_objects(objects_to_delete)
		except:
			pass
		# create objects based on array under key 'new()'
		try:
			objects_to_create = config_dict['data']['objects'][self.create_method_name]
			self.create_objects(objects_to_create)
		except:
			pass
		# delete materials
		try:
			materials_to_delete = config_dict['data']['materials'][self.delete_method_name]
			self.delete_materials(materials_to_delete)
		except:
			pass
		# create materials
		try:
			materials_to_create = config_dict['data']['materials'][self.create_method_name]
			self.create_materials(materials_to_create)
		except:
			pass
		# main setup
		self.autoset_attributes(self.config)

example_settings = {
	'data': {
		'objects': {
			'delete()': [
				{
					'name': "Cube"
				}
			],
			'new()': [
				{
					'primitive': 'plane',
					'attributes': {
						'name': "bg",
						'location': Vector((0.0, 0.0, 0.0))
					}
				}
			],
		},
		'materials': {
			'delete()': [
				{
					'name': "Material"
				}
			],
			'new()': [
				{
					'name': "bg-color",
					'diffuse_color': (0.53, 0.583, 0.827),
					'diffuse_intensity': 1.0,
					'specular_intensity': 0.0,
					'use_transparent_shadows': True,
					'preview_render_type': "FLAT"
				},
				{
					'name': "color-black",
					'diffuse_color': (0.0, 0.0, 0.0),
					'diffuse_intensity': 1.0,
					'specular_intensity': 0.0,
					'use_transparent_shadows': True,
					'preview_render_type': "FLAT"
				},
				{
					'name': "color-white",
					'diffuse_color': (1.0, 1.0, 1.0),
					'diffuse_intensity': 1.0,
					'specular_intensity': 0.0,
					'use_transparent_shadows': True,
					'preview_render_type': "FLAT"
				}
			]
		}
	},
	'context': {
		'scene': {
			'objects': {
				'["Camera"]': {
					'rotation_euler': (0.0, 0.0, 0.0),
					'location': Vector((0.0, 0.0, 5.0))
				},
				'["Lamp"]': {
					'location': Vector((-2.9, 2.2, 3.0)),
					'parent': bpy.context.scene.objects['Camera'],
					'data': {
						'energy': 1.1,
						'distance': 25.0,
						'shadow_ray_samples': 3
					}
				},
				'[\'bg\']': {
					'scale': Vector((12.0, 12.0, 12.0)),
					'data': {
						'materials': {
							'[0]': bpy.data.materials['bg-color'] 	# Error: not yet created
						}
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

anim_config = Autoconfig_Anim()
anim_config.setup(example_settings)
