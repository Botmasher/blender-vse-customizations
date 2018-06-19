#!/usr/bin/env python
import bpy

## Custom Blender Nodes Setup
## by GitHub user Botmasher (Joshua R)
##
## Implement a custom node configuration for my Blender anim.blend files

# TODO error handling

class Custom_Nodes:

	setup_ran_once = False

	def __init__(self, vec_blur=False, dof=False, node_tree=bpy.context.scene.node_tree):
		self.vec_blur = vec_blur
		self.dof = dof
		self.node_tree = node_tree
		return None

	def link_socket(self, o_node, i_node, o_socket, i_socket=None):
		"""Connect an output node socket to an input node socket"""
		if i_socket is None: i_socket = o_socket
		return self.node_tree.links.new(o_node.outputs[o_socket], i_node.inputs[i_socket])

	def link_sockets(self, o=[], i=[], o_sockets=[], i_sockets=None):
		"""Link listed sockets of one node to or from multiple other nodes in the node tree

		Expects either input or output to be a single node.
		o_nodes 		single node or list of nodes to use as socket output
		i_nodes			single node or list of nodes to use as socket input
		o_sockets		list of socket names to connect from
		i_sockets 	same-length list of socket names to connect to (if different from o_sockets)
		"""

		# do not require duplicate arguments when sockets have same name
		if i_sockets is None: i_sockets = o_sockets

		# Convert lone socket type names to avoid requiring one-string lists
		o_sockets = [o_sockets] if type(o_sockets) is str else o_sockets
		o_sockets = [i_sockets] if type(i_sockets) is str else i_sockets

		# mismatch between io sockets
		if len(o_sockets) != len(i_sockets):
			raise Exception("Linking nodes - the count of input socket types does not match the number of outputs")

		# identify list vs fixed node and direction for iteration
		from_fixed = None
		fixed_node = None
		iter_nodes = []
		if type(o) is list and type(i) == type(self.node_tree.nodes[0]):
			from_fixed = False
			fixed_node = i
			iter_nodes = o
		elif type(o) == type(self.node_tree.nodes[0]) and type(i) is list:
			from_fixed = True
			fixed_node = o
			iter_nodes = i
		else:
			raise Exception("Linking nodes - received too many nodes; expected one base node and any number of branch nodes")

		# link nodes
		links = []
		for iter_node in iter_nodes:
			o_node = fixed_node if from_fixed else iter_node
			i_node = iter_node if from_fixed else fixed_node
			for n in range(len(o_sockets)):
				o_socket = o_sockets[n]
				i_socket = i_sockets[n]
				link = self.link_socket(o_node, i_node, o_socket, i_socket)
				links.append(link)

		return links

	def create_nodes(self, node_types=[]):
		"""Create nodes on the node tree, one new node per listed node type"""
		new_nodes = []
		for node_type in node_types:
			print(node_type)
			node = self.node_tree.nodes.new(type=node_type)
			new_nodes.append(node)
		return new_nodes

	def clear_nodes(self):
		"""Remove all nodes from the node tree"""
		if len(self.node_tree.nodes) < 1: return
		for i in range(len(self.node_tree.nodes)-1):
			self.node_tree.nodes.remove(self.node_tree.nodes[i])
		return self.node_tree.nodes

	def setup_ui(self, window=0):
		"""Set active node editor areas to display the compositor node tree"""
		for area in bpy.context.window_manager.windows[window].screen.areas:
			if area.type == "NODE_EDITOR":
				area.spaces.active.tree_type = "CompositorNodeTree"
				area.spaces.active.show_backdrop = True
				area.spaces.active.use_auto_render = True
		return area

	def setup_nodes(self, run_again=False, vec_blur=True):
		"""Create, link and set values for nodes"""

		if self.setup_ran_once:
			print("Nodes already customized. To force a rerun, call setup_nodes with run_again=True.")
			return None

		bpy.context.scene.use_nodes = True

		# remove any default nodes
		self.clear_nodes()

		# add nodes
		new_node_types = ["CompositorNodeRLayers", "CompositorNodeComposite", "CompositorNodeViewer"]
		input_render_node, output_composite_node, output_viewer_node = self.create_nodes(new_node_types)

		# place and link nodes
		input_render_node.location = (-250, 0)
		output_composite_node.location = (250, 0)
		output_viewer_node.location = (250, -150)
		self.link_sockets(input_render_node, [output_composite_node, output_viewer_node], ['Image', 'Alpha'])

		left_nodes = [input_render_node]
		right_nodes = [output_composite_node, output_viewer_node]

		# motion blur
		if vec_blur:
			vector_node = self.create_nodes(["CompositorNodeVecBlur"])[0]
			vector_node.location = (0, 0)
			vector_node.samples = 10
			vector_node.factor = 0.55
			bpy.context.scene.render.layers.active.use_pass_vector = True
			# links
			self.link_sockets(left_nodes, vector_node, 'Image')
			self.link_sockets(input_render_node, vector_node, ['Vector', 'Depth'], ['Speed', 'Z'])
			self.link_sockets(vector_node, right_nodes, 'Image')
			left_nodes = [vector_node]

		# depth of field
		if dof:
			defocus_node = self.create_nodes(["CompositorNodeDefocus"])[0]
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
			self.link_sockets(left_nodes, defocus_node, 'Image')
			self.link_socket(input_render_node, defocus_node, 'Depth', 'Z')
			self.link_sockets(defocus_node, right_nodes, 'Image')

			# cam dof
			empty = bpy.data.objects.new("empty-dof", None)
			empty.empty_draw_type = "CUBE"
			bpy.context.scene.objects.link(empty)
			bpy.context.scene.camera.data.dof_object = empty
			left_nodes = [defocus_node]

		return self.node_tree

# test run
c_node = Custom_Nodes(vec_blur=True, dof=True)
c_node.setup_ui()
c_node.setup_nodes()
