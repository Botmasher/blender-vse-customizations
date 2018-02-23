import bpy
import re
from mathutils import Vector

# Autoconfigure project from dict
# by GitHub user Botmasher (Joshua R) 
#
# Adjust settings and create and delete elements based on a single config dictionary.
#
# This class script bundles and adds to operations found in separate modules within this
# same project.
#
# Setup requires a well-formatted dict:
# - dicts that do not follow the example formatting will produce exceptions
# - dicts that do follow the example formatting may still produce exceptions
# - see sample settings dictionary file within this same project
#
# Creating and deleting currently works for a useful but cherry-picked set of elements
# (scene objects, textures and materials).

# TODO better handling of materials and textures
# TODO delete based on any attribute
# TODO pass values to function attributes

class Autoconfig_Anim:
	def __init__(self, create_method_name='new()', delete_method_name='delete()'):
		# nested keys for special setup handling of create and delete
		self.create_method_name = create_method_name
		self.delete_method_name = delete_method_name
		return None

	def is_string_bracketed_key(self, attribute_string):
		"""Test if a string is formatted like a bracketed dictionary key"""
		return re.match("\[[\"\'](.+)[\"\']\]", attribute_string)

	def is_string_bracketed_index(self, attribute_string):
		"""Test if a string is formatted like a bracketed index"""
		return re.match("\[(.+)\]", attribute_string)

	def try_key_or_index(self, attr_string, attr_chain, value_to_append=None):
		"""Translate an attribute string surrounded by brackets to an element's key or index"""
		is_bracketed_str = self.is_string_bracketed_key(attr_string)
		is_bracketed_i = False if is_bracketed_str else self.is_string_bracketed_index(attr_string)
		if not is_bracketed_str and not is_bracketed_i:
			return None
		# treat as dictionary key string
		# helps convert e.g. {'collection': {'["Name"]': {'attribute': "value"}}} to collection["Name"].attribute = "value"
		if is_bracketed_str:
			try:
				name = attr_string[2:-2]
				return name
			except:
				raise Exception("Setting attributes - failed to access %s at ['%s']. Scene may be missing an object with this name." % (attr_chain, name))
		# treat as integer index in list
		# helps convert e.g. {'arr': {'[1]': {'attr': "value"}}} to arr[1].attr = "value"
		elif is_bracketed_i:
			i = -1
			try:
				# return the index
				i = int(attr_string[1:-1])
				attr_chain[i]
			except:
				# index out of range
				pass
				#	raise Exception("Setting attributes - failed to access %s index [%s]." % (attr_chain, i))
			return i
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
		"""Delete existing materials where material name matches a name in the list"""
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

	def create_textures(self, textures_settings):
		"""Create and setup data for new textures"""
		added_textures = []
		for texture in textures_settings:
			new_texture = bpy.data.textures.new(name=texture['name'], type=texture['type'])
			for attribute in texture:
				if attribute != 'name' and attribute != 'type':
					try:
						setattr(new_texture, attribute, texture[attribute])
					except:
						continue
			added_textures.append(new_texture)
		return added_textures

	def delete_data_block(self, element_names, data_path):
		"""Delete existing elements of a type where element name matches a name in the list"""
		element_names = [el['name'] for el in element_names] if type(element_names[0]) == dict else element_names
		try:
			getattr(element_names, "append")
		except:
			return False
		for name in element_names:
			try:
				data_path[name].user_clear() 	# set data block user count to 0
			except:
				pass
		return True

	def delete_textures(self, texture_names):
		"""Delete existing textures where texture name matches a name in the lsit"""
		texture_names = [tex['name'] for tex in texture_names] if type(texture_names[0]) == dict else texture_names
		try:
			getattr(texture_names, "append")
		except:
			return False
		for name in texture_names:
			try:
				bpy.data.textures[name].user_clear() 	# set data block user count to 0
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
				bracketed = self.try_key_or_index(k, attr_chain)
				if bracketed is not None:
					# add material to an object by material name (avoid new/deleted materials dict errors)
					if attr_chain.path_from_id() == "materials" and type(v) == type(""):
						# bpy.context.scene.objects['name'].data.materials[i] = bpy.data.materials['material_name']
						v = bpy.data.materials[v]
					try:
						attr_chain[bracketed] = v
					except:
						try:
							attr_chain.append(v)
						except:
							pass 	# unable to set accessed element to value, e.g. element doesn't exist, string when expected int, ...
				else:
					try:
						attr_chain = setattr(attr_chain, k, v)
					except:
						raise Exception("Unable to set attribute %s on %s" % (k, attr_chain))
				print("Setting attribute %s to value: %s" % (k, v))
			return attr_chain
		# node is a nested dict: chain the attr and look for subattr values
		if k is not None:
			bracketed = self.try_key_or_index(k, attr_chain)		
			if bracketed is not None:
				attr_chain = attr_chain[bracketed]
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
		"""Configure a project using a well-formatted dictionary"""
		if config_dict is not None:
			self.set_config(config_dict)
		# new and deleted objects
		try:
			objects_to_delete = config_dict['data']['objects'][self.delete_method_name]
			self.delete_objects(objects_to_delete)
		except:
			pass
		try:
			objects_to_create = config_dict['data']['objects'][self.create_method_name]
			self.create_objects(objects_to_create)
		except:
			pass
		# new and deleted materials
		try:
			materials_to_delete = config_dict['data']['materials'][self.delete_method_name]
			self.delete_elements(materials_to_delete, bpy.data.materials)
		except:
			pass
		try:
			materials_to_create = config_dict['data']['materials'][self.create_method_name]
			self.create_materials(materials_to_create)
		except:
			pass
		# new and deleted textures
		try:
			textures_to_delete = config_dict['data']['textures'][self.delete_method_name]
			self.delete_elements(textures_to_delete, bpy.data.textures)
		except:
			pass
		try:
			textures_to_create = config_dict['data']['textures'][self.create_method_name]
			self.create_textures(textures_to_create)
		except:
			pass
		# main setup
		self.autoset_attributes(self.config)