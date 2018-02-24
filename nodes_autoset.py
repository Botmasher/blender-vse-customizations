#!/usr/bin/env python
import bpy

## Automatic Blender Nodes Configuration
## by GitHub user Botmasher (Joshua R)
## 
## Implement my custom node setup in my Blender anim.blend files

# TODO check if script already ran

def setup_nodes_ui(window=0):
	"""Set active node editor areas to display the compositor node tree"""
	for area in bpy.context.window_manager.windows[window].screen.areas:
		if area.type == "NODE_EDITOR":
			area.spaces.active.tree_type = "CompositorNodeTree"
			area.spaces.active.show_backdrop = True
			area.spaces.active.use_auto_render = True
	return area

def setup_nodes(vec_blur=False, dof=False):
	"""Create a render node tree, link nodes and set values"""
	bpy.context.scene.use_nodes = True
	
	starting_area = bpy.context.area.type
	bpy.context.area.type = "NODE_EDITOR"

	setup_nodes_ui()

	# remove any default nodes
	for i in range(len(bpy.context.scene.node_tree.nodes)):
		bpy.context.scene.node_tree.nodes.remove(i)

	node_tree = bpy.context.scene.node_tree

	# add nodes
	input_render_node = node_tree.nodes.new(type="CompositorNodeRLayers")
	output_composite_node = node_tree.nodes.new(type="CompositorNodeComposite")
	output_viewer_node = node_tree.nodes.new(type="CompositorNodeViewer")

	# place and link nodes
	input_render_node.location = (-250, 0)
	output_composite_node.location = (250, 0)
	output_viewer_node.location = (250, -150)
	node_tree.links.new(input_render_node.outputs['Image'], output_composite_node.inputs['Image'])
	node_tree.links.new(input_render_node.outputs['Alpha'], output_composite_node.inputs['Alpha'])
	node_tree.links.new(input_render_node.outputs['Image'], output_viewer_node.inputs['Image'])
	node_tree.links.new(input_render_node.outputs['Alpha'], output_viewer_node.inputs['Alpha'])

	left_nodes = [input_render_node]
	right_nodes = [output_composite_node, output_viewer_node]

	# motion blur
	if vec_blur:
		vector_node = node_tree.nodes.new(type="CompositorNodeVecBlur")
		vector_node.location = (0, 0)
		vector_node.samples = 10
		vector_node.factor = 0.55
		bpy.context.scene.render.layers.active.use_pass_vector = True
		# links
		for left_node in left_nodes:
			node_tree.links.new(left_node.outputs['Image'], vector_node.inputs['Image'])
		node_tree.links.new(input_render_node.outputs['Vector'], vector_node.inputs['Speed'])
		node_tree.links.new(input_render_node.outputs['Depth'], vector_node.inputs['Z'])
		for right_node in right_nodes:
			node_tree.links.new(vector_node.outputs['Image'], right_node.inputs['Image'])
		left_nodes = [vector_node]

	# depth of field
	if dof:
		defocus_node = node_tree.nodes.new(type="CompositorNodeDefocus")
		defocus_node.use_zbuffer = True
		defocus_node.f_stop = 20.0
		defocus_node.blur_max = 15.0
		defocus_node.threshold = 1.4
		# rearrange nodes
		if vec_blur:
			defocus_node.location = (200, 0)
			for node in right_nodes:
				node.location = (node.location[0]+200, node.location[1])
		else:
			defocus_node.location = (0, 0)
		# links
		for left_node in left_nodes:
			node_tree.links.new(left_node.outputs['Image'], defocus_node.inputs['Image'])
		node_tree.links.new(input_render_node.outputs['Depth'], defocus_node.inputs['Z'])
		for right_node in right_nodes:
			node_tree.links.new(defocus_node.outputs['Image'], right_node.inputs['Image'])

		# cam dof
		empty = bpy.data.objects.new("empty-dof", None)
		empty.empty_draw_type = "CUBE"
		bpy.context.scene.objects.link(empty)
		bpy.context.scene.camera.data.dof_object = empty
		left_nodes = [defocus_node]
		
	bpy.context.area.type = starting_area

	return node_tree

setup_nodes(vec_blur=True, dof=True)
