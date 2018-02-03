#!/usr/bin/env python
import bpy

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

def run_npr_autoset():
	scene = get_scene()
	freestyle = turnon_freestyle(scene)

	# custom settings
	remove_default_lineset = True
	default_lineset_name = "LineSet"
	clear_all_linesets = True
	if clear_all_linesets == False and remove_default_lineset and freestyle.linesets[0].name == default_lineset_name:
		freestyle.linesets.active_index = 0
		bpy.ops.scene.freestyle_lineset_remove()
	for lineset in freestyle.linesets:
		if clear_all_linesets:
			bpy.ops.scene.freestyle_lineset_remove()
		else:
			freestyle.linesets[lineset].show_render = False
	bpy.ops.scene.freestyle_lineset_add()
	freestyle.linesets[len(freestyle.linesets)-1].name = "bold"
	bpy.ops.scene.freestyle_lineset_add()
	freestyle.linesets[len(freestyle.linesets)-1].name = "sketchy"

	# TODO custom linestyles

	return {'FINISHED'}

run_npr_autoset()
