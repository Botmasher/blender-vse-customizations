import bpy

# Input: a single selected sequence strip
# Output: one hard cut and lengthened strip for each frame in the input

# TODO adjust params through interface
# TODO cases where trail or gap is negative (correctly deal with dominoing start_frames)
# TODO the first strip 

def get_strip():
	strip = bpy.context.scene.sequence_editor.active_strip
	return strip

def extend_strip(sequence, x_dir):
	"""Linearly lengthen or shrink a single sequence along the x axis"""
	sequence.select = True
	#trail < 0 and bpy.ops.transform.transform(mode="TRANSLATION", value=(-trail, 0.0, 0.0, 0.0), axis=(1.0, 0.0, 0.0))
	sequence.select_right_handle = True if x_dir > 0 else False
	sequence.select_left_handle = True if x_dir < 0 else False
	bpy.ops.transform.transform(mode="TRANSLATION", value=(x_dir, 0.0, 0.0, 0.0), axis=(1.0, 0.0, 0.0))
	sequence.select_right_handle = False
	sequence.select_left_handle = False
	sequence.select = False
	return sequence

def gap_strip(sequence, gap):
	"""Insert a gap after the strip and push all subsequent strips ahead"""
	bpy.context.scene.frame_current = sequence.frame_start + 1
	bpy.ops.sequencer.gap_insert(frames=gap)
	return sequence

def move_strip(sequence, offset):
	"""Move the strip to a new origin along the x axis"""
	sequence.frame_start += offset
	return sequence

def extend_strips(sequences, trail, gap):
	"""Uniformly lengthen substrips

	Arguments:
	sequences -- array of strips to extend
	trail -- the left (neg) or right (pos) lengthening applied to each strip
	"""
	for sequence in bpy.context.scene.sequence_editor.sequences_all: sequence.select = False

	#first_sequence = sequences.pop()
	adjusted_sequences = []

	for i in reversed(range(len(sequences))):
		sequence = sequences[i]
		# move to the right by gap amount
		print("Moving strip %s ahead %s frames..." % (sequence.name, str(gap*i)))
		if i > 0: move_strip(sequence, (gap * i))
		# scale strip by handle
		#extend_strip(sequence, trail)
	
	# set first strip separately to avoid negative
	#extend_strip(first_sequence, trail)

	return sequences

def subcut_strip(s, step, trail, gap):
	# calculate key strip frames
	start_frame = s.frame_start
	end_frame = start_frame + s.frame_final_duration
	bpy.context.scene.frame_current = start_frame

	# select only the active strip
	for sequence in bpy.context.scene.sequence_editor.sequences_all: sequence.select = False
	s.select = True

	# go to end of active strip and cut back to start
	frames = reversed(range(start_frame+1, end_frame))
	
	# calculate how many strips will be produced (proportional to number of cuts)
	split_strip_count = len(list(frames)) / step
	if split_strip_count <= 1.0:
		return [s]
	else:
		# account for range from 0 and separate handling of first strip
		cuts_count = int(split_strip_count) + 1

	# build list of cut strips
	chopped_sequences = []

	current_strip = s

	for cut in range(cuts_count):

		current_strip.select = True
		
		if cut == 0:
			s.animation_offset_end += s.frame_final_duration - step 	# (cuts_count * step)
		else:
			# playhead to cut spot
			bpy.context.scene.frame_current += step
			bpy.ops.sequencer.duplicate()
			current_strip = bpy.context.scene.sequence_editor.active_strip
			current_strip.frame_start = bpy.context.scene.frame_current + ((trail + gap) * cut)
			print(current_strip.frame_start)
			current_strip.animation_offset_start += step
			current_strip.animation_offset_end -= step
			current_strip.frame_final_duration = step
			print(bpy.context.scene.sequence_editor.active_strip)

		current_strip.frame_offset_end -= trail

		chopped_sequences.append(current_strip)

		for sequence in bpy.context.scene.sequence_editor.sequences_all: sequence.select = False

	chopped_sequences.append(s)

	return chopped_sequences

def chop_strip(step=1, trail=0, gap=0):
	"""Chop a sequencer strip into substrips.

	Arguments:
	step -- the number of frames counted between hard cuts (default 1)
	trail -- the left or right hand lengthening applied to each substrip (default 0)
	"""
	
	print("\nSTARTING SCRIPT frame-splitter") 

	# find the input strip
	s = get_strip()

	if s is not None:
		# store and set context
		initial_area = bpy.context.area.type
		bpy.context.area.type = "SEQUENCE_EDITOR"
		
		# chop and stretch
		chopped_strips = subcut_strip(s, step, trail, gap)
		#extend_strips(chopped_strips, trail, gap)

		# reset context
		bpy.context.area.type = initial_area

	# Issues
	#   - another strip in same channel to the right of active split strip
	#       - note the option to select strips to the L/R in ops
	#   - handle no strip selected

	# Extras
	# - allow selected set of strips to be uniformly lengthened/shortened
	 	# check they are indeed contiguous in timeline
	 	# run through each back to front if lengthening
	 		# move strip right as required
	 		# select right strip handle
	 		# move strip handle right to lengthen
	 	# run through each front to back if shortening
	 		# move strip left as required (except the first)
	 		# select right handle
	 		# move strip handle left to shorten
	
	return True

class ChopStripPanel(bpy.types.Panel):
	#bl_context = "objectmode"
	bl_label = "Chop up Strip"
	bl_idname = "strip.chop_strip_panel"
	bl_space_type = "SEQUENCE_EDITOR"
	bl_region_type = "UI"

	def draw(self, context):
		column = self.layout.column(align=True)
		column.operator("strip.chop_strip", text="Chop up strip")
		#self.layout.operator('strip.chop_strip', text="Chop up strip")

class ChopStrip(bpy.types.Operator):
	bl_idname = "strip.chop_strip"
	bl_label = "Chop Strip Frames"
	bl_descriptions = "Chop up sequence frames into new substrips"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return context.mode == "OBJECT"

	def execute(self, context):
		chop_strip(step=-1, trail=4, gap=4)
		return {'FINISHED'}

def register() :
	bpy.utils.register_module(__name__)

def unregister() :
	bpy.utils.unregister_module(__name__)
	del bpy.types.Scene.chop_strip_frames

if __name__ == "__main__":
	register()
