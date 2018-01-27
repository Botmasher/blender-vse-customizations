import bpy

# Input: a single selected sequence strip
# Output: one hard cut and lengthened strip for each frame in the input

# find the input strip
def get_strip():
	return bpy.context.scene.sequence_editor.sequences.active_strip

s = get_strip()
frame_start = s.frame_start
end_frame = s.frame_start + s.frame_final_duration

# go to the end of the strip and cut back to the beginning
for f in reversed(range(frame_start, end_frame):
	# move one frame back
	# set context to sequence editor
	# hard cut
	# set context to code
	# move new substrip forward its current frame_duration * your own offset
	# 	- if doesn't select, later iterate thru strips sharing base strip name (formatted strip_name.index)
	# 	- for each strip check if it's got the name and 
	# stretch out the new one-frame substrip by frame_duration*my_offset-1 frames
	# (onto next frame)

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

# Panel

# Operator

# Registration
