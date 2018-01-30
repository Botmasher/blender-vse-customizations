import bpy

# Input: a single selected sequence strip
# Output: one hard cut and lengthened strip for each frame in the input

def get_strip():
	strip = bpy.context.scene.sequence_editor.active_strip
	return strip

def extend_strips(sequences, trail):
	"""Uniformly lengthen substrips

	Arguments:
	sequences -- array of strips to extend
	trail -- the left (neg) or right (pos) lengthening applied to each strip
	"""
	for sequence in bpy.context.scene.sequence_editor.sequences_all: sequence.select = False

	first_sequence = sequences.pop()

	for sequence in sequences:
		sequence.select = True
		#trail < 0 and bpy.ops.transform.transform(mode="TRANSLATION", value=(-trail, 0.0, 0.0, 0.0), axis=(1.0, 0.0, 0.0))
		sequence.select_right_handle = True if trail > 0 else False
		sequence.select_left_handle = True if trail < 0 else False
		bpy.ops.transform.transform(mode="TRANSLATION", value=(trail, 0.0, 0.0, 0.0), axis=(1.0, 0.0, 0.0))
		sequence.select_right_handle = False
		sequence.select_left_handle = False
		sequence.select = False

	# # remove first strip to avoid negative
	# if trail < 0:
	# 	first_sequence.select = True
	# 	first_sequence.select_left_handle = True
	# 	bpy.ops.transform.transform(mode="TRANSLATION", value=(trail, 0.0, 0.0, 0.0), axis=(1.0, 0.0, 0.0))
	# 	first_sequence.select_left_handle = False
	# 	first_sequence.select = False
	# else:
	# 	first_sequence.select = True
	# 	first_sequence.select_right_handle = True
	# 	bpy.ops.transform.transform(mode="TRANSLATION", value=(trail, 0.0, 0.0, 0.0), axis=(1.0, 0.0, 0.0))
	# 	first_sequence.select_right_handle = False
	# 	first_sequence.select = False

	return {'FINISHED'}

def subcut_strip(s, step, trail):
	# calculate key strip frames
	start_frame = s.frame_start
	end_frame = start_frame + s.frame_final_duration
	bpy.context.scene.frame_current = end_frame

	# select only the active strip
	for sequence in bpy.context.scene.sequence_editor.sequences_all: sequence.select = False
	s.select = True

	# go to end of active strip and cut back to start
	strip_count = int( len(list(reversed(range(start_frame+1, end_frame)))) / step )
	for f in reversed(range(start_frame+1, end_frame)):
		s.select = True
		# playhead one frame back
		bpy.context.scene.frame_current -= step
		# hard cut and move
		bpy.ops.sequencer.cut(frame=bpy.context.scene.frame_current, type="HARD", side="RIGHT")
		# TODO each seq must move not just trail but trail * remaining strips to place
		if trail < 0:
			bpy.ops.transform.transform(mode="TRANSLATION", value=(abs(trail * 2) - step, 0.0, 0.0, 0.0), axis=(1.0, 0.0, 0.0))
		else:
			bpy.ops.transform.transform(mode="TRANSLATION", value=(trail, 0.0, 0.0, 0.0), axis=(1.0, 0.0, 0.0))
		strip_count -= 1

	# TODO move initial strip if trail is negative (above does not deal with start_frame)
	# TODO correctly calculate and move strips along x
		# - currently they're just auto nudging over as each chop is set step units before prev
		# - leads to negative trail case when initial frame also handled: each strip is trail units too far right
	
	# list out all resulting strips
	chopped_sequences = [seq for seq in bpy.context.scene.sequence_editor.sequences_all if seq.select]
	chopped_sequences.append(s)

	return chopped_sequences

def chop_strip(step=1, trail=0):
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
		chopped_strips = subcut_strip(s, step, trail)
		extend_strips(chopped_strips, trail)

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
	
	return {'FINISHED'}

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
		chop_strip(trail=20)
		return {'FINISHED'}

def register() :
	bpy.utils.register_module(__name__)

def unregister() :
	bpy.utils.unregister_module(__name__)
	del bpy.types.Scene.chop_strip_frames

if __name__ == "__main__":
	register()
