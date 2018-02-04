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
	return {'FINISHED'}

def run_npr_autoset(linesets={}, clear_all_linesets=False, clear_default_lineset=False, default_lineset_name="Lineset"):
	scene = get_scene()
	freestyle = turnon_freestyle(scene)

	# custom settings
	default_lineset_name = "LineSet"
	if clear_all_linesets == False and clear_default_lineset and freestyle.linesets[0].name == default_lineset_name:
		freestyle.linesets.active_index = 0
		bpy.ops.scene.freestyle_lineset_remove()
	for lineset in freestyle.linesets:
		if clear_all_linesets:
			bpy.ops.scene.freestyle_lineset_remove()
		else:
			freestyle.linesets[lineset].show_render = False
	for lineset_name in linesets:
		# detection settings
		bpy.ops.scene.freestyle_lineset_add()
		added_lineset = freestyle.linesets[len(freestyle.linesets)-1]
		added_lineset.name = lineset_name
		added_lineset.edge_type_negation = "EXCLUSIVE"
		added_lineset.select_silhouette = False
		added_lineset.select_border = False
		added_lineset.select_contour = False
		added_lineset.select_suggestive_contour = True
		added_lineset.select_ridge_valley = True
		added_lineset.select_crease = False
		added_lineset.select_edge_mark = True
		added_lineset.select_external_contour = False
		added_lineset.select_material_boundary = False
		# aesthetic settings
		if lineset_name == 'bold':
			added_lineset.linestyle.name = "%s-linestyle" % lineset_name
			added_lineset.linestyle.color = [0.0, 0.0, 0.0]
			added_lineset.linestyle.use_chaining = True
			added_lineset.linestyle.chaining = "PLAIN"
			added_lineset.linestyle.thickness = 10.0
			# thickness along stroke
			added_lineset.linestyle.thickness_modifiers.new(name="thickness-along-stroke", type="ALONG_STROKE")
			added_lineset.linestyle.thickness_modifiers[-1].mapping = "CURVE"
			added_lineset.linestyle.thickness_modifiers[-1].curve.curves[0].points.new(0.38, 0.74)
			added_lineset.linestyle.thickness_modifiers[-1].curve.curves[0].points[0].location = Vector((0.0, 0.32))
			added_lineset.linestyle.thickness_modifiers[-1].curve.curves[0].points[2].location = Vector((1.0, 0.28))
			added_lineset.linestyle.thickness_modifiers[-1].value_min = added_lineset.linestyle.thickness * 0.1
			added_lineset.linestyle.thickness_modifiers[-1].value_max = added_lineset.linestyle.thickness
			added_lineset.linestyle.thickness_modifiers[-1].influence = 0.98
			# thickness caligraphy
			added_lineset.linestyle.thickness_modifiers.new(name="thickness-calligraphy", type="CALLIGRAPHY")
			added_lineset.linestyle.thickness_modifiers[-1].orientation = 42.0
			added_lineset.linestyle.thickness_modifiers[-1].thickness_min = added_lineset.linestyle.thickness * 0.1
			added_lineset.linestyle.thickness_modifiers[-1].thickness_max = added_lineset.linestyle.thickness
			added_lineset.linestyle.thickness_modifiers[-1].influence = 0.86
			# thickness distance from camera
			added_lineset.linestyle.thickness_modifiers.new(name="thickness-distance-from-camera", type="DISTANCE_FROM_CAMERA")
			added_lineset.linestyle.thickness_modifiers[-1].range_min = 5.0 		# TODO use empty to calibrate range
			added_lineset.linestyle.thickness_modifiers[-1].range_max = 20.0 		# TODO use empty to calibrate range
			added_lineset.linestyle.thickness_modifiers[-1].value_min = added_lineset.linestyle.thickness * 0.2
			added_lineset.linestyle.thickness_modifiers[-1].value_max = added_lineset.linestyle.thickness
			added_lineset.linestyle.thickness_modifiers[-1].invert = True
			added_lineset.linestyle.thickness_modifiers[-1].influence = 1.0
			# alpha along stroke
			added_lineset.linestyle.alpha = 1.0
			added_lineset.linestyle.alpha_modifiers.new(name="alpha-along-stroke", type="DISTANCE_FROM_CAMERA")
			added_lineset.linestyle.alpha_modifiers[-1].mapping = "CURVE"
			added_lineset.linestyle.alpha_modifiers[-1].curve.curves[0].points.new(0.25, 1.0)
			added_lineset.linestyle.alpha_modifiers[-1].curve.curves[0].points[0].location = Vector((0.0, 0.64))
			added_lineset.linestyle.alpha_modifiers[-1].curve.curves[0].points[2].location = Vector((1.0, 0.6))
			added_lineset.linestyle.alpha_modifiers[-1].influence = 0.08
			# geometry backbone stretcher
			added_lineset.linestyle.geometry_modifiers.new(name="backbone-stretcher", type="BACKBONE_STRETCHER")
			added_lineset.linestyle.geometry_modifiers[-1].backbone_length = added_lineset.linestyle.thickness * 0.18
			# geometry sinus displacement
			added_lineset.linestyle.geometry_modifiers.new(name="sinus-displacement", type="SINUS_DISPLACEMENT")
			added_lineset.linestyle.geometry_modifiers[-1].wavelength = 22.5
			added_lineset.linestyle.geometry_modifiers[-1].amplitude = 0.26
			added_lineset.linestyle.geometry_modifiers[-1].phase = 0.264
			# geometry perlin noise 1d
			added_lineset.linestyle.geometry_modifiers.new(name="perlin-noise-1d", type="PERLIN_NOISE_1D")
			added_lineset.linestyle.geometry_modifiers[-1].frequency = 11.0
			added_lineset.linestyle.geometry_modifiers[-1].amplitude = added_lineset.linestyle.thickness * 0.14
			added_lineset.linestyle.geometry_modifiers[-1].seed = random.randint(-999, 999)
			added_lineset.linestyle.geometry_modifiers[-1].octaves = 5
			added_lineset.linestyle.geometry_modifiers[-1].angle = 42.0
		elif lineset_name == 'sketchy':
			added_lineset.linestyle.name = "%s-linestyle" % lineset_name
			added_lineset.linestyle.color = [0.06, 0.06, 0.06]
			added_lineset.linestyle.use_chaining = True
			added_lineset.linestyle.chaining = "SKETCHY"
			added_lineset.linestyle.rounds = 5
			added_lineset.linestyle.thickness = 10.0
			# thickness
			added_lineset.linestyle.thickness = 1.0
			# alpha
			added_lineset.linestyle.alpha = 0.95
			# geometry Backbone Stretcher
			added_lineset.linestyle.geometry_modifiers.new(name="backbone-stretcher", type="BACKBONE_STRETCHER")
			added_lineset.linestyle.geometry_modifiers[-1].backbone_length = 5.5
			# geometry Perlin Noise 2D
			added_lineset.linestyle.geometry_modifiers.new(name="perlin-noise-2d", type="PERLIN_NOISE_2D")
			added_lineset.linestyle.geometry_modifiers[-1].frequency = 9.0
			added_lineset.linestyle.geometry_modifiers[-1].amplitude = 2.1
			added_lineset.linestyle.geometry_modifiers[-1].seed = random.randint(0, 999)
			added_lineset.linestyle.geometry_modifiers[-1].octaves = 4
			added_lineset.linestyle.geometry_modifiers[-1].angle = 28.0

	# TODO select active lineset "bold" when finished

	# TODO script can rerun without crashing

	return {'FINISHED'}

linesets = {'bold': {'chaining': True, }, 'sketchy': {}}
run_npr_autoset(linesets, clear_all_linesets=True, clear_default_lineset=True)
