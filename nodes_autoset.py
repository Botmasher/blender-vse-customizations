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
		if area.type == "NODE_EDITOR": area.spaces.active.tree_type = "CompositorNodeTree"
	return area

def setup_nodes():
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
	calc_vector_node = node_tree.nodes.new(type="CompositorNodeVecBlur")
	output_composite_node = node_tree.nodes.new(type="CompositorNodeComposite")

	# place and link nodes
	input_render_node.location = (-250, 0)
	calc_vector_node.location = (0, 0)
	output_composite_node.location = (250, 0)
	node_tree.links.new(input_render_node.outputs['Image'], calc_vector_node.inputs['Image'])
	node_tree.links.new(input_render_node.outputs['Alpha'], output_composite_node.inputs['Alpha'])
	node_tree.links.new(input_render_node.outputs['Depth'], calc_vector_node.inputs['Z'])
	node_tree.links.new(calc_vector_node.outputs['Image'], output_composite_node.inputs['Image'])

	# set node values
	calc_vector_node.samples = 10
	calc_vector_node.factor = 0.55

	# add speed
	bpy.context.scene.render.layers.active.use_pass_vector = True
	node_tree.links.new(input_render_node.outputs['Vector'], calc_vector_node.inputs['Speed'])

	bpy.context.area.type = starting_area

	return node_tree

setup_nodes()
