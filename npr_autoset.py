#!/usr/bin/env python
import bpy
import random
from mathutils import Vector

# TODO
# - documentation incl info here
# 	- document each method
# - Errors and better error handling
# - run with new untested properties added to the test object
# - separate out the dict
# - separate this out into its own subproject (Addon)
# - generate dicts from settings
# - see all TODO below

def get_scene():
	return bpy.context.scene

def using_freestyle(scene):
	return scene.render.use_freestyle

def toggle_freestyle(scene):
	scene.render.use_freestyle = not scene.render.use_freestyle
	return using_freestyle(scene)

def turnon_freestyle(scene, render_layer="RenderLayer"):
	scene.render.layers[render_layer].use_freestyle = True
	scene.render.use_freestyle = True
	return scene.render.layers[render_layer].freestyle_settings

def turnoff_freestyle(scene):
	scene.render.use_freestyle = False
	return scene.render.use_freestyle

def clear_linesets(freestyle_settings, clear_all=True, clear_default=True, default_name="Lineset"):
	if clear_all == False and clear_default and freestyle_settings.linesets[0].name == default_name:
		freestyle_settings.linesets.active_index = 0
		bpy.ops.scene.freestyle_lineset_remove()
	for lineset in freestyle_settings.linesets:
		if clear_all:
			bpy.ops.scene.freestyle_lineset_remove()
		else:
			freestyle_settings.linesets[lineset].show_render = False
	return True

def create_lineset(freestyle_settings):
	freestyle_settings.linesets.new("")
	lineset = freestyle_settings.linesets[len(freestyle_settings.linesets)-1]
	return lineset

def set_line_attribute(line, attribute_name, attribute_value):
	"""Set a value on a lineset or linestyle's dot notation property
	line_setting 			freestyle .lineset or .lineset.linestyle to configure
	attribute_name 		property name within the lineset or lineset.linesetyle
	attribute_value 	new value to assign to the property					
	"""
	try:
		setattr(line, attribute_name, attribute_value)
	except:
		return False	# TODO create Exception here
	return line

def create_modifier(linestyle, modifiers_set, modifier_name, modifier_type):
	try:
		modifiers = getattr(linestyle, modifiers_set)
		modifiers.new(name=modifier_name, type=modifier_type)
	except:
		return False	# TODO create Exception here - could not create modifier; does not exist
	return modifiers[-1]

def configure_lineset(lineset, lineset_data):
	lineset.name = lineset_data['name']
	for attribute in lineset_data['lineset']:
		set_line_attribute(lineset, attribute, lineset_data['lineset'][attribute])
	return lineset

def create_configure_modifier(linestyle, modifiers_set, modifier_dict):
	# shape of modifier dict (peeled off from within modifiers array in the lineset dict)
	# {
	#		name: '',
	# 	type: '',
	# 	attributes: {
	#			attr_0: 0
	# 		...
	# 		attr_n: 0
	# 	}
	# }
	#
	# Call create_modifier to add new modifier to the appropriate modifiers and get the returned modifier
	modifier = create_modifier(linestyle, modifiers_set, modifier_dict['name'], modifier_dict['type'])
	# TODO check and fix iterate through modifier attributes
	for attribute in modifier_dict['attributes']:
		# TODO check and fix special case handling curves
		if attribute == 'curve':
			point_left_coords, point_mid_coords, point_right_coords = modifier_dict['attributes'][attribute]
			modifier.curve.curves[0].points.new(point_mid_coords[0], point_mid_coords[1])
			modifier.curve.curves[0].points[0].location = Vector(point_left_coords)
			modifier.curve.curves[0].points[2].location = Vector(point_right_coords)
		else:
			set_line_attribute(modifier, attribute, modifier_dict['attributes'][attribute])
	return modifier

def configure_linestyle(lineset, line_dict):
	"""Use a line configuration dictionary to configure the line's lineset.linestyle"""

	# basic settings for linestyle properties
	linestyle = lineset.linestyle
	for linestyle_attribute in line_dict['linestyle']:
		set_line_attribute(linestyle, linestyle_attribute, line_dict['linestyle'][linestyle_attribute])

	# linestyle modifiers
	for modifiers_set in line_dict['modifiers']: 	# nested dict e.g. line_dict['modifiers']['alpha_modifiers'] 
		modifiers_list = line_dict['modifiers'][modifiers_set] 
		for modifier_dict in modifiers_list:
			create_configure_modifier(linestyle, modifiers_set, modifier_dict)

	return linestyle

def setup_line(freestyle, line_dict):
	"""
	Use a line configuration dictionary to implement one Freestyle lineset with an associated linestyle
	freestyle 	freestyle line settings for the render layer
	line_dict 	line configuration dictionary
	
	expected shape of line_dict:
	{
		'name': "",
		'lineset': {}, 	 	# lineset settings, e.g. 'select_crease': False
		'linestyle': {}, 	# linestyle settings, e.g. 'alpha': 1.0
		'modifiers': {} 	# modifier sets, e.g. 'alpha_modifiers': {'name': "", 'type': "ALONG_STROKE", 'attributes': {'influence': 1.0}}
	}
	"""
	print("\n-- Creating %s lineset --" % line_dict['name'])
	try:
		lineset = create_lineset(freestyle)
		print(" - created lineset!")
		configure_lineset(lineset, line_dict) 			# update method to parse dict
		print(" - configured lineset!")
		configure_linestyle(lineset, line_dict)			# new method
		print(" - configured linestyle!")
		return True
	except:
		print("Failed to create styled linesets.")
		return False 	# TODO create Exception here

def setup_lines(freestyle, lines_dict):
	for line_name in lines_dict:
		setup_line(freestyle, lines_dict[line_name])
	return True

# TODO use above INSTEAD OF the code in npr_autoset below
# 	- what npr_autoset should do:
#		1) activate_freestyle(scene)
# 	2) clear_linesets(freestyle, ...)
# 	3) setup_lines(lines_dict)
# 	4) return {'FINISHED'}

def run_npr_autoset(lines_dict={}, clear_all_linesets=False, clear_default_lineset=False):
	scene = get_scene()
	freestyle = turnon_freestyle(scene)
	clear_linesets(freestyle, clear_all=clear_all_linesets, clear_default=clear_default_lineset)
	# create and configure
	setup_lines(freestyle, lines_dict)

	# TODO select active lineset "bold" when finished

	# TODO script rerun without crashing

	return {'FINISHED'}

# TODO pass in dictionary to adjust settings
lines = {
	'bold': {
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
			'select_material_boundary': False,
		},
		'linestyle': {
			'name': "bold-linestyle",
			'use_chaining': True,
			'chaining': "PLAIN",
			'rounds': None,
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
	'sketchy': {
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
}

# TODO output objects like above from Freestyle settings after they are set through Blender UI

run_npr_autoset(lines, clear_all_linesets=True, clear_default_lineset=True)
