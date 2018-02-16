import bpy
import re

# adjust settings and create and delete objects, materials, textures from a single config dict
# example config dict and instantiation at bottom

class Autoconfig_Anim:
	def __init__(self, create_method_name='new()', delete_method_name='delete()'):
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
				raise Exception("Setting attributes - failed to access %s at ['%s']" % (attr_chain, name))
		# treat as integer (index in Blender list)
		# helps convert e.g. {'arr': {'[1]': {'attr': "value"}}} to arr[1].attr = "value"
		elif is_bracketed_int:
			try:
				i = int(attr_string[1:-1])
				return attr_chain[i]
			except:
				raise Exception("Setting attributes - failed to access %s at [%s]" % (attr_chain, i))
		return None

	def create_objects(self, objects_settings={}):
		"""Create and setup Blender objects in scene from an array of settings dicts"""
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

	def autoset_attrs(self, v, k=None, attr_chain=bpy):
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
		# 'new()' or 'delete()' keys with arrays of objects to create or delete
		if k == self.create_method_name: return self.create_objects(v)
		if k == self.delete_method_name: return self.delete_objects(v) 	# accepts dict!
		# TODO handle new and deleted materials, textures, ...

		# base case: node is an attribute=value settings pair
		if type(v) is not dict:
			# reached leaf - set attribute value
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
			self.autoset_attrs(value, attribute, attr_chain)

example_settings = {
	'context': {
		'scene': {
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
							'name': "Background",
							'location': Vector((0.0, 0.0, 0.0))
						}
					}
				],
				'["Camera"]': {
					'rotation_euler': (0.0, 0.0, 0.0)
				},
				'[\'Lamp\']': {
					'parent': bpy.context.scene.objects['Camera'],
					'data': {
						'energy': 0.5
					}
				},
				'[0]': {
					'name': "Name set by autoset_named_attributes script!"
				}
			},
			'render': {
				'resolution_percentage': 100
			},
			'frame_start': 2,
			'frame_end': 20,
			'world': {
				'light_settings': {
					'use_environment_light': True
				}
			}
		}
	}
}

anim_config = Autoconfig_Anim()
anim_config.
