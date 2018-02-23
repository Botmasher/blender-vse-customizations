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
	# TODO set window default when opening a new NODE_EDITOR
	return area

def setup_nodes(scene):
	scene.use_nodes = True
	
	#scene.node_tree.type = "COMPOSITING"
	setup_nodes_ui()

	# TODO first check if default compositor node and renderlayer node already exist
	node_group = bpy.data.node_groups.new(name="New Node Group", type="CompositorNodeTree")

	node_r_layers = node_group.nodes.new(type="CompositorNodeRLayers")
	node_vector_blur = node_group.nodes.new(type="CompositorNodeVectorBlur")
	node_composite = node_group.nodes.new(type="CompositorNodeComposite")

	return node_group

setup_nodes(bpy.context.scene)
