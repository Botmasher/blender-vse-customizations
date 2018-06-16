#!/usr/bin/env python
import bpy
import random
from mathutils import Vector

## NPR Autoset Freestyle Line Configuration for Blender
## by GitHub user Botmasher (Joshua R)
##
## Use:
## Simply include a well-formatted line configuration data list, then call
## the run_npr_autoset() function passing in that configuration data.
##
## Other options, settings and the expected shape of that data are documented
## in the comments for specific functions.
## 
## See example line configuration below. Compare to Blender interface settings
## to find further attribute strings and values for adjusting more properties.
##

# TODO
# - better documentation
# - finer-grained error raising
# - run with new untested properties added to the test object
# - create __init__.py and separate out lines data
# - separate this out into its own subproject (Addon)
# - generate dicts from settings
# - rerun script without crashing

class NprAutosetException(Exception):
	"""Custom error handling for this tool"""
	def __init__(self, message, error):
		exception_message = "%s – %s" % (message, error)
		super(Exception, self).__init__(exception_message)
		self.message = exception_message

def activate_freestyle(scene, render_layer="RenderLayer"):
	"""Turn on freestyle in both the render and layer settings"""
	scene.render.layers[render_layer].use_freestyle = True
	scene.render.use_freestyle = True
	return scene.render.layers[render_layer].freestyle_settings

def clear_linesets(freestyle_settings, clear_all=True, clear_default=True, default_name="Lineset"):
	"""Remove linesets from freestyle settings, either just the default startup lineset or all linesets"""
	if clear_all == False and clear_default and freestyle_settings.linesets[0].name == default_name:
		freestyle_settings.linesets.active_index = 0
		bpy.ops.scene.freestyle_lineset_remove()
	for lineset in freestyle_settings.linesets:
		if clear_all:
			bpy.ops.scene.freestyle_lineset_remove()
	return True

def set_line_attribute(line, attribute_name, attribute_value):
	"""Set a value on a lineset or linestyle's dot notation property

	line_setting 			freestyle .lineset or .lineset.linestyle to configure
	attribute_name 		property name within the lineset or lineset.linesetyle
	attribute_value 	new value to assign to the property					
	"""
	try:
		setattr(line, attribute_name, attribute_value)
	except Exception as e:
		raise NprAutosetException("Unable to set line attribute \"%s\" to value %s" % (attribute_name, attribute_value), e)
	return line

def create_lineset(freestyle_settings, lineset_name=""):
	"""Add one new freestyle lineset"""
	freestyle_settings.linesets.new("")
	lineset = freestyle_settings.linesets[len(freestyle_settings.linesets)-1]
	lineset.name = lineset_name
	return lineset

def configure_lineset(lineset, lineset_data):
	"""Set the value for each of this lineset's attributes"""
	for attribute in lineset_data:
		set_line_attribute(lineset, attribute, lineset_data[attribute])
	return lineset

def create_modifier(linestyle, modifiers_set, modifier_type, modifier_name=""):
	"""Add one new modifier from a specific modifiers set to the linestyle

	linestyle 				the linestyle for a single freestyle settings lineset
	modifiers_set 		set of modifiers within the linestyle that this modifier will belong to
	modifier_type 		type of modifier to pass when creating the new modifier
	modifier_name 		optional string name to give this modifier
	"""
	try:
		modifiers = getattr(linestyle, modifiers_set)
		modifiers.new(name=modifier_name, type=modifier_type)
	except Exception as e:
		raise NprAutosetException("Unable to create \"%s\" modifier \"%s\"" % (modifiers_set, modifier_type), e)
	return modifiers[-1] 		# latest modifier in the modifiers set

def create_configure_modifier(linestyle, modifiers_set, modifier_dict):
	"""Add and configure one modifier for this linestyle
	
	linestyle 				the linestyle for a single freestyle settings lineset
	modifiers_set 		set of modifiers within the linestyle that this modifier will belong to
	modifier_dict 		dictionary containing the name, type and attribute settings for this modifier

	Expected shape of modifier_dict:
	{
		'name': "",
		'type': "",
		'attributes': {
			'attribute_0': 0,
			...
		}
	}
	"""
	modifier = create_modifier(linestyle, modifiers_set, modifier_dict['type'], modifier_dict['name'])
	for attribute in modifier_dict['attributes']:
		# handle mapping a curve
		if attribute == 'curve':
			point_left_coords, point_mid_coords, point_right_coords = modifier_dict['attributes'][attribute]
			modifier.curve.curves[0].points.new(point_mid_coords[0], point_mid_coords[1])
			modifier.curve.curves[0].points[0].location = Vector(point_left_coords)
			modifier.curve.curves[0].points[2].location = Vector(point_right_coords)
		# simply set the attribute's value
		else:
			set_line_attribute(modifier, attribute, modifier_dict['attributes'][attribute])
	return modifier

def setup_modifiers(linestyle, modifiers_dict):
	"""Create and configure modifiers on a single freestyle linestyle

	lineset  				one freestyle settings lineset
	modifiers_dict 	dictionary of configuration data for a lineset's linestyle modifiers

	Expected shape of modifiers_dict:
	{
		'modifiers_set': [
			{
				'name': "custom-modifier-name",
				'type': "MODIFIER_TYPE",
				'attributes': {
					'attribute_0': 0,
					...
				}
			},
			...
		],
		...
	}
	"""
	for modifiers_set in modifiers_dict: 
		modifiers_list = modifiers_dict[modifiers_set] 
		for modifier_dict in modifiers_list:
			create_configure_modifier(linestyle, modifiers_set, modifier_dict)
	return linestyle

def configure_linestyle(linestyle, linestyle_dict):
	"""Configure properties of a single freestyle linestyle

	lineset  				one freestyle settings lineset
	linestyle_dict 	dictionary of configuration data for a lineset's linestyle properties
	
	Expected shape of linestyle_dict:
	{
		'attribute_0': 0,
		...
	}
	"""
	for linestyle_attribute in linestyle_dict:
		set_line_attribute(linestyle, linestyle_attribute, linestyle_dict[linestyle_attribute])
	return linestyle

def setup_line(freestyle, line_dict):
	"""Use a line configuration dictionary to implement one freestyle lineset with an associated linestyle
	
	freestyle 	freestyle settings for the render layer
	line_dict 	line configuration dictionary
	
	Expected shape of line_dict:
	{
		'name': "",
		'lineset': {}, 	 	# lineset settings
		'linestyle': {}, 	# linestyle settings
		'modifiers': {} 	# modifier sets nested with specific modifiers
	}
	"""
	try:
		lineset = create_lineset(freestyle, line_dict['name'])
		configure_lineset(lineset, line_dict['lineset'])
		configure_linestyle(lineset.linestyle, line_dict['linestyle'])
		setup_modifiers(lineset.linestyle, line_dict['modifiers'])
		print ("Created and configured `%s` line" % line_dict['name'])
		return lineset
	except Exception as e:
		raise NprAutosetException("Failed run setup_line() on \"%s\" line" % line_dict['name'], e)
		return e

def setup_lines(freestyle, lines_list):
	"""Iterate through lines data and perform a setup for each"""
	for line_dict in lines_list:
		setup_line(freestyle, line_dict)
	return True

def run_npr_autoset(scene=bpy.context.scene, lines_list=[], clear_all_linesets=False, clear_default_lineset=False):
	"""Turn on freestyle settings and set up linesets and linestyles from the list of line configuration data

	scene									Blender scene to activate render and layer freestyle settings
	lines_list 						list of line configuration data dictionaries
	clear_all_linesets 		boolean to remove all existing freestyle linesets
	clear_default_lineset	boolean to remove the default freestlye lineset "Lineset"

	Expected shape of lines_list:
	[
		{
			'name': "",
			'lineset': {}, 	 	# lineset settings, e.g. 'select_crease': False
			'linestyle': {}, 	# linestyle settings, e.g. 'alpha': 1.0
			'modifiers': {} 	# modifier sets, e.g. 'alpha_modifiers': {'name': "", 'type': "ALONG_STROKE", 'attributes': {'influence': 1.0}}
		},
		...
	]
	"""
	freestyle = activate_freestyle(scene)
	# cleanup existing linesets
	clear_linesets(freestyle, clear_all=clear_all_linesets, clear_default=clear_default_lineset)
	setup_lines(freestyle, lines_list)
	# select the first line
	freestyle.linesets.active_index = 0
	return {'FINISHED'}

# Example state (copied from my typical settings)
lines = [
	{
		'name': "bold",
		'lineset': {
			'edge_type_negation': "EXCLUSIVE",
			'select_silhouette': False,
			'select_border': False,
			'select_contour': False,
			'select_suggestive_contour': True,
			'select_ridge_valley': True,
			'select_crease': False,
			'select_edge_mark': True,
			'select_external_contour': False,
			'select_material_boundary': False
		},
		'linestyle': {
			'name': "bold-linestyle",
			'use_chaining': True,
			'chaining': "PLAIN",
			'color': [0.0, 0.0, 0.0],
			'alpha': 1.0,
			'thickness': 10.0
		},
		'modifiers': {
			'alpha_modifiers': [
				{
					'name': "alpha-along-stroke",
					'type': "ALONG_STROKE",
					'attributes': {
						'mapping': "CURVE",
						'curve': [(0.25, 1.0), (0.0, 0.64), (1.0, 0.6)],
						'influence': 0.08
					}
				}
			],
			'thickness_modifiers': [
				{
					'name': "thickness-along-stroke",
					'type': "ALONG_STROKE",
					'attributes': {
						'mapping': "CURVE",
						'curve': [(0.0, 0.32), (0.38, 0.74), (1.0, 0.28)],
						'value_min': 1.0,			# thickness * 0.1
						'value_max': 10.0,
						'influence': 0.98
					}
				},
				{
					'name': "thickness-calligraphy",
					'type': "CALLIGRAPHY",
					'attributes': {
						'orientation': 42.0,
						'thickness_min': 1.0,			# thickness * 0.1
						'thickness_max': 10.0,
						'influence': 0.86
					}
				},
				{
					'name': "thickness-distance-camera",
					'type': "DISTANCE_FROM_CAMERA",
					'attributes': {
						'invert': True,
						'range_min': 5.0, 		# TODO use empty to calibrate range
						'range_max': 20.0,
						'value_min': 2.0,			# thickness * 0.2
						'value_max': 10.0,
						'influence': 1.0
					}
				}
			],
			'geometry_modifiers': [
				{
					'name': "backbone-stretcher",
					'type': "BACKBONE_STRETCHER",
			 		'attributes': {
						'backbone_length': 0.18 	 # thickness * 0.18
					}
				},
				{
					'name': "sinus-displacement",
					'type': "SINUS_DISPLACEMENT",
					'attributes': {
						'wavelength': 22.5,
						'amplitude': 0.26,
						'phase': 0.264
					}
				},
				{
					'name': "perlin-noise-1d",
					'type': "PERLIN_NOISE_1D",
					'attributes': {
						'frequency': 11.0,
						'amplitude': 0.14,	 	# thickness * 0.14
						'seed': random.randint(-999, 999),
						'octaves': 5,
						'angle': 42.0
					}
				}
			]
		}
	},
	{
		'name': "sketchy",
		'lineset': {
			'edge_type_negation': "EXCLUSIVE",
			'select_silhouette': False,
			'select_border': False,
			'select_contour': False,
			'select_suggestive_contour': True,
			'select_ridge_valley': True,
			'select_crease': False,
			'select_edge_mark': True,
			'select_external_contour': False,
			'select_material_boundary': False,
		},
		'linestyle': {
			'name': "sketchy-linestyle",
			'use_chaining': True,
			'chaining': "SKETCHY",
			'rounds': 5,
			'color': [0.06, 0.06, 0.06],
			'alpha': 0.95,
			'thickness': 1.2
		},
		'modifiers': {
			'geometry_modifiers': [
				{
					'name': "backbone-stretcher",
					'type': "BACKBONE_STRETCHER",
					'attributes': {
						'backbone_length': 5.5
					}
				},
				{
					'name': "perlin-noise-2d",
					'type': "PERLIN_NOISE_2D",
					'attributes': {
						'frequency': 9.0,
						'amplitude': 2.1,
						'seed': random.randint(0, 999),
						'octaves': 4,
						'angle': 28.0
					}
				}
			]
		}
	}
]

run_npr_autoset(lines_list=lines, clear_all_linesets=True, clear_default_lineset=True)
