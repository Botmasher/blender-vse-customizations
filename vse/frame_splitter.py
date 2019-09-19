#!/usr/bin/python
import bpy
from bpy.props import IntProperty

# Blender Python extension by Joshua (GitHub user Botmasher)
# Input: a single selected sequence strip
# Output: one hard cut and lengthened strip for each framestep in the input

# TODO cases where trail or gap is negative (correctly deal with dominoing start_frames)

# TODO another strip in same channel to the right of active split strip
# 	- note the option to select strips to the L/R in ops

# TODO handle no strip selected

# TODO allow selected set of strips to be uniformly lengthened/shortened
# 	- check they are indeed contiguous in timeline
# 	- run through each back to front if lengthening
# 		- move strip right as required
# 		- select right strip handle
# 		- move strip handle right to lengthen
# 	- run through each front to back if shortening
# 		- move strip left as required (except the first)
# 		- select right handle
# 		- move strip handle left to shorten

def config_frame_splitter_props():
	# set up properties for UI panel
	frame_splitter_props_data = {
		'frame_splitter_step': {
			'name': "Step (frames)",
			'default': 1,
			'description': "Number of source frames to cut into each substrip"
		},
		'frame_splitter_trail': {
			'name': "Trail (frames)",
			'default': 4,
			'description':  "Number of frames to extend each step cut substrip"
		},
		'frame_splitter_gap': {
			'name': "Gap (frames)",
			'default': 4,
			'description': "Number of frames between resulting substrips"
		}
	}
	[
		setattr(bpy.types.ImageSequence, prop_name, IntProperty(
			name = int_prop['name'],
			default = int_prop['default'],
			description = int_prop['description']
		)) for prop_name, int_prop in frame_splitter_props_data.items()
	]
	return frame_splitter_props_data

class FrameSplitter:
	def __init__(self):
		return

	def gap_push_strip(self, sequence, gap):
		"""Insert a gap after the strip and push all subsequent strips ahead"""
		bpy.context.scene.frame_current = sequence.frame_start + 1
		bpy.ops.sequencer.gap_insert(frames=gap)
		return sequence

	def move_strip(self, sequence, offset):
		"""Move the strip to a new origin along the x axis"""
		sequence.frame_start = offset
		return sequence

	def extend_strip(self, sequence, x_dir):
		"""Linearly lengthen or shrink a single sequence along the x axis"""
		sequence.frame_offset_end -= x_dir
		return sequence

	def cut_anim_substrip(self, sequence, step=0):
		"""Cut a duplicated sequence down to step number of frames, step frames after the start frame
		
		Used to make uniform hard cuts when duplicating a sequence
		Arguments:
		sequence -- a single strip from the sequence editor
		step -- the number of frames to cut from the original and to leave standing in this duplicate
		"""
		sequence.animation_offset_start += step
		sequence.animation_offset_end -= step
		sequence.frame_final_duration = step
		return sequence

	def subcut_strip(self, s, step=0, trail=0, gap=0):
		"""Cut a sequencer strip into uniformly stepped and spaced substrips.

		Arguments:
		s -- a single sequence in the sequence editor
		step -- the number of frames counted between hard cuts
		trail -- the left or right hand lengthening in frames applied to each substrip
		gap -- the empty space in frames to leave between each substrip
		"""
		# remember starting playhead position
		playhead_frame = bpy.context.scene.frame_current

		# store bounding strip frames
		start_frame = s.frame_start
		end_frame = start_frame + s.frame_final_duration

		# store and set playhead position
		bpy.context.scene.frame_current = start_frame

		# select only the active strip
		for sequence in bpy.context.scene.sequence_editor.sequences_all: sequence.select = False
		s.select = True

		# calculate how many strips will be produced (proportional to number of cuts)
		frames = range(start_frame+1, end_frame)
		cuts_count = 0 if not step else len(list(frames)) / step
		
		# avoid processing one-cut strip - send back as its own cut
		if cuts_count <= 0.0:
			print("Too few strips to cut")
			return [s]
		# account for range and separate handling of first strip
		else:
			cuts_count = int(cuts_count) + 1

		# cut into substrips and create list of subcut strips
		resulting_strips = []
		current_strip = s

		# make planned cuts following step and stretch values
		for cut in range(cuts_count):
			current_strip.select = True
			last_strip = current_strip

			# shrink original strip
			if cut == 0:
				s.animation_offset_end += s.frame_final_duration - step
			# cut subsequent strips
			else:
				bpy.context.scene.frame_current += step
				bpy.ops.sequencer.duplicate()
				current_strip = bpy.context.scene.sequence_editor.active_strip
				self.move_strip(current_strip, bpy.context.scene.frame_current + ((trail + gap) * cut))
				self.cut_anim_substrip(current_strip, step)

			self.extend_strip(current_strip, trail)

			resulting_strips.append(current_strip)

			last_strip.select = False

		# return playhead to original frame
		bpy.context.scene.frame_current = playhead_frame

		# list of cut strips
		return resulting_strips

class FrameSplitterPanel(bpy.types.Panel):
	bl_label = "Frame Splitter"
	bl_idname = "strip.frame_splitter_panel"
	bl_space_type = "SEQUENCE_EDITOR"
	bl_region_type = "UI"

	def draw(self, context):
		strip = bpy.context.scene.sequence_editor.active_strip
		if not strip:
			return
		self.layout.row().prop(strip, "frame_splitter_step")
		self.layout.row().prop(strip, "frame_splitter_trail")
		self.layout.row().prop(strip, "frame_splitter_gap")
		self.layout.row().operator("strip.frame_splitter", text="Subcut Strip")

class FrameSplitterOperator(bpy.types.Operator):
	bl_idname = "strip.frame_splitter"
	bl_label = "Frame Splitter Button"
	bl_description = "Split sequence frames into new substrips"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return context.mode == "OBJECT"

	def execute(self, context):
		scene = bpy.context.scene
		strip = scene.sequence_editor.active_strip
		step = strip.frame_splitter_step
		trail = strip.frame_splitter_trail
		gap = strip.frame_splitter_gap
		scene.sequence_editor.frame_splitter.subcut_strip(strip, step, trail, gap)
		return {'FINISHED'}

def register():
	config_frame_splitter_props()
	bpy.types.SequenceEditor.frame_splitter = FrameSplitter()
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)
	del bpy.types.SequenceEditor.frame_splitter

if __name__ == "__main__":
	register()
