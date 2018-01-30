import bpy

# Input: a single selected sequence strip
# Output: one hard cut and lengthened strip for each frame in the input

def get_strip():
	return bpy.context.scene.sequence_editor.active_strip

def chop_strip(step=1, trail=10):
	print("\nSTARTING SCRIPT frame-splitter") 

	# find the input strip
	s = get_strip()
	start_frame = s.frame_start
	end_frame = start_frame + s.frame_final_duration
	bpy.context.scene.frame_current = end_frame

	# deselect all strips
	for strip in bpy.context.scene.sequence_editor.sequences_all: strip.select = False
	# select only active
	s.select = True

	#print(bpy.context.scene.sequence_editor.active_strip)
	#bpy.context.scene.frame_current -= 1
	#bpy.ops.sequencer.cut(frame=bpy.context.scene.frame_current, type="HARD", side="RIGHT")
	#bpy.ops.transform.transform(mode="TRANSLATION", value=(step, 0.0, 0.0, 0.0), axis=(1.0, 0.0, 0.0))
	#print(bpy.context.scene.sequence_editor.active_strip)

	#run_area = bpy.context.area.type
	#bpy.context.area.type = "SEQUENCE_EDITOR"

	# go to the end of the strip and cut back to the beginning
	for f in reversed(range(start_frame+1, end_frame)):
		frames_remaining = f - start_frame
		s.select = True
		# move one frame back
		bpy.context.scene.frame_current -= step
		# hard cut
		bpy.ops.sequencer.cut(frame=bpy.context.scene.frame_current, type="HARD", side="RIGHT")
		bpy.ops.transform.transform(mode="TRANSLATION", value=(trail, 0.0, 0.0, 0.0), axis=(1.0, 0.0, 0.0))
		# contxt: 	3 frame strip starting on timeline frame 0
		# params: 	step 1, trail 10, (cutframes=1, freezes=0)
		# back to front iteration:
			# - set current frame to frame - step
			# - cut
		#latest_strip = sequences[0]
		#print(latest_strip)

		#latest_strip.animation_offset_end -= trail

		#bpy.ops.sequencer.select_handles(side="RIGHT")
		
		# set context to sequence editor
		# set context to code
		# move new substrip forward by offset
		# 	- if doesn't select, later iterate thru strips sharing base strip name (formatted strip_name.index)
		# 	- for each strip check if it's got the name and 
		# stretch out the new one-frame substrip by frame_duration*my_offset-1 frames
		# (onto next frame)

	#bpy.context.area.type = run_area

	# extra - allow selected set of strips to be uniformly lengthened/shortened
	 	# check they are indeed contiguous in timeline
	 	# run through each back to front if lengthening
	 		# move strip right as required
	 		# select right strip handle
	 		# move strip handle right to lengthen
	 	# run through each front to back if shortening
	 		# move strip left as required (except the first)
	 		# select right handle
	 		# move strip handle left to shorten

	chopped_sequences = [seq for seq in bpy.context.scene.sequence_editor.sequences_all if seq.select]

	for seq in chopped_sequences: seq.select = False

	chopped_sequences.append(s)

	for seq in chopped_sequences:
		seq.select = True
		seq.select_right_handle = True
		bpy.ops.transform.transform(mode="TRANSLATION", value=(trail, 0.0, 0.0, 0.0), axis=(1.0, 0.0, 0.0))
		seq.select_right_handle = False
		seq.select = False

	# Issues
	#   - another strip in same channel to the right of active split strip
	#       - note the option to select strips to the L/R in ops
	#   - handle no strip selected

	# Registration
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
		chop_strip()
		return {'FINISHED'}

def register() :
	bpy.utils.register_module(__name__)

def unregister() :
	bpy.utils.unregister_module(__name__)
	del bpy.types.Scene.chop_strip_frames

if __name__ == "__main__":
	register()
