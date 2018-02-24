#!/usr/bin/env python
import bpy

## Automatic Blender Nodes Configuration
## by GitHub user Botmasher (Joshua R)
## 
## Implement my custom node setup in my Blender anim.blend files

def setup_nodes_ui(window=0):
	for area in bpy.context.window_manager.windows[window].screen.areas:
		if area.type == "NODE_EDITOR":
			area.spaces.active.tree_type = "CompositorNodeTree"
		#bpy.context.space_data.tree_type = "CompositorNodeTree"
	# TODO set window default when opening a new NODE_EDITOR
	return area

def setup_nodes(scene):
	scene.use_nodes = True
	
	#scene.node_tree.type = "COMPOSITING"

	starting_area = bpy.context.area.type
	bpy.context.area.type = "NODE_EDITOR"

	setup_nodes_ui()

	# remove any default nodes
	for i in range(len(bpy.context.scene.node_tree.nodes)):
		bpy.context.scene.node_tree.nodes.remove(i)

	# add nodes
	bpy.ops.node.add_node(type="CompositorNodeRLayers", use_transform=True)
	bpy.context.scene.node_tree.nodes.active.location = (-250, 0)
	bpy.ops.node.add_node(type="CompositorNodeVecBlur", use_transform=True)
	bpy.context.scene.node_tree.nodes.active.location = (0, 0)
	bpy.ops.node.add_node(type="CompositorNodeComposite", use_transform=True)
	bpy.context.scene.node_tree.nodes.active.location = (250, 0)

	# TODO link node sockets

	bpy.context.area.type = starting_area

	#node_r_layers = node_group.nodes.new(type="CompositorNodeRLayers")
	#node_vector_blur = node_group.nodes.new(type="CompositorNodeVectorBlur")
	#node_composite = node_group.nodes.new(type="CompositorNodeComposite")

	return 

setup_nodes(bpy.context.scene)
