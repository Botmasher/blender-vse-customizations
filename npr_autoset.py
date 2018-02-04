#!/usr/bin/env python
import bpy
import random
from mathutils import Vector

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
		if clear_all_linesets:
			bpy.ops.scene.freestyle_lineset_remove()
		else:
			freestyle_settings.linesets[lineset].show_render = False
	return True

def create_lineset(scene, freestyle_settings):
	freestyle_settings.linesets.new("")
	lineset = freestyle_settings.linesets[len(freestyle_settings.linesets)-1]
	return lineset

def configure_lineset(lineset, lineset_data):
	print(lineset_data)
	lineset.name = lineset_data['name']
	lineset.edge_type_negation = "EXCLUSIVE"
	lineset.select_silhouette = False
	lineset.select_border = False
	lineset.select_contour = False
	lineset.select_suggestive_contour = True
	lineset.select_ridge_valley = True
	lineset.select_crease = False
	lineset.select_edge_mark = True
	lineset.select_external_contour = False
	lineset.select_material_boundary = False
	return lineset

def configure_linestyle_bold(linestyle):
	linestyle.name = "bold-linestyle"
	linestyle.color = [0.0, 0.0, 0.0]
	linestyle.use_chaining = True
	linestyle.chaining = "PLAIN"
	linestyle.thickness = 10.0
	# thickness along stroke
	linestyle.thickness_modifiers.new(name="thickness-along-stroke", type="ALONG_STROKE")
	linestyle.thickness_modifiers[-1].mapping = "CURVE"
	linestyle.thickness_modifiers[-1].curve.curves[0].points.new(0.38, 0.74)
	linestyle.thickness_modifiers[-1].curve.curves[0].points[0].location = Vector((0.0, 0.32))
	linestyle.thickness_modifiers[-1].curve.curves[0].points[2].location = Vector((1.0, 0.28))
	linestyle.thickness_modifiers[-1].value_min = linestyle.thickness * 0.1
	linestyle.thickness_modifiers[-1].value_max = linestyle.thickness
	linestyle.thickness_modifiers[-1].influence = 0.98
	# thickness caligraphy
	linestyle.thickness_modifiers.new(name="thickness-calligraphy", type="CALLIGRAPHY")
	linestyle.thickness_modifiers[-1].orientation = 42.0
	linestyle.thickness_modifiers[-1].thickness_min = linestyle.thickness * 0.1
	linestyle.thickness_modifiers[-1].thickness_max = linestyle.thickness
	linestyle.thickness_modifiers[-1].influence = 0.86
	# thickness distance from camera
	linestyle.thickness_modifiers.new(name="thickness-distance-from-camera", type="DISTANCE_FROM_CAMERA")
	linestyle.thickness_modifiers[-1].range_min = 5.0 		# TODO use empty to calibrate range
	linestyle.thickness_modifiers[-1].range_max = 20.0 		# TODO use empty to calibrate range
	linestyle.thickness_modifiers[-1].value_min = linestyle.thickness * 0.2
	linestyle.thickness_modifiers[-1].value_max = linestyle.thickness
	linestyle.thickness_modifiers[-1].invert = True
	linestyle.thickness_modifiers[-1].influence = 1.0
	# alpha along stroke
	linestyle.alpha = 1.0
	linestyle.alpha_modifiers.new(name="alpha-along-stroke", type="DISTANCE_FROM_CAMERA")
	linestyle.alpha_modifiers[-1].mapping = "CURVE"
	linestyle.alpha_modifiers[-1].curve.curves[0].points.new(0.25, 1.0)
	linestyle.alpha_modifiers[-1].curve.curves[0].points[0].location = Vector((0.0, 0.64))
	linestyle.alpha_modifiers[-1].curve.curves[0].points[2].location = Vector((1.0, 0.6))
	linestyle.alpha_modifiers[-1].influence = 0.08
	# geometry backbone stretcher
	linestyle.geometry_modifiers.new(name="backbone-stretcher", type="BACKBONE_STRETCHER")
	linestyle.geometry_modifiers[-1].backbone_length = linestyle.thickness * 0.18
	# geometry sinus displacement
	linestyle.geometry_modifiers.new(name="sinus-displacement", type="SINUS_DISPLACEMENT")
	linestyle.geometry_modifiers[-1].wavelength = 22.5
	linestyle.geometry_modifiers[-1].amplitude = 0.26
	linestyle.geometry_modifiers[-1].phase = 0.264
	# geometry perlin noise 1d
	linestyle.geometry_modifiers.new(name="perlin-noise-1d", type="PERLIN_NOISE_1D")
	linestyle.geometry_modifiers[-1].frequency = 11.0
	linestyle.geometry_modifiers[-1].amplitude = linestyle.thickness * 0.14
	linestyle.geometry_modifiers[-1].seed = random.randint(-999, 999)
	linestyle.geometry_modifiers[-1].octaves = 5
	linestyle.geometry_modifiers[-1].angle = 42.0
	return linestyle

def configure_linestyle_sketchy(linestyle):
	linestyle.name = "sketchy-linestyle"
	linestyle.color = [0.06, 0.06, 0.06]
	linestyle.use_chaining = True
	linestyle.chaining = "SKETCHY"
	linestyle.rounds = 5
	linestyle.thickness = 10.0
	# thickness
	linestyle.thickness = 1.0
	# alpha
	linestyle.alpha = 0.95
	# geometry Backbone Stretcher
	linestyle.geometry_modifiers.new(name="backbone-stretcher", type="BACKBONE_STRETCHER")
	linestyle.geometry_modifiers[-1].backbone_length = 5.5
	# geometry Perlin Noise 2D
	linestyle.geometry_modifiers.new(name="perlin-noise-2d", type="PERLIN_NOISE_2D")
	linestyle.geometry_modifiers[-1].frequency = 9.0
	linestyle.geometry_modifiers[-1].amplitude = 2.1
	linestyle.geometry_modifiers[-1].seed = random.randint(0, 999)
	linestyle.geometry_modifiers[-1].octaves = 4
	linestyle.geometry_modifiers[-1].angle = 28.0
	return linestyle

def run_npr_autoset(linesets={}, clear_all_linesets=False, clear_default_lineset=False):
	scene = get_scene()
	freestyle = turnon_freestyle(scene)
	clear_linesets(freestyle, clear_all=clear_all_linesets, clear_default=clear_default_lineset)
	# custom settings
	for lineset_name in linesets:
		# create
		lineset = create_lineset(scene, freestyle)
		# detection settings
		configure_lineset(lineset, linesets[lineset_name])
		# aesthetic settings
		if lineset_name == 'bold':
			configure_linestyle_bold(lineset.linestyle)
		elif lineset_name == 'sketchy':
			configure_linestyle_sketchy(lineset.linestyle)

	# TODO select active lineset "bold" when finished

	# TODO script rerun without crashing

	return {'FINISHED'}

# TODO pass in dictionary to adjust settings
linesets = {'bold': {'name': 'bold', 'edge': {'negation': "EXCLUSIVE"}, 'chaining': True}, 'sketchy': {'name': 'sketchy'}}
run_npr_autoset(linesets, clear_all_linesets=True, clear_default_lineset=True)
