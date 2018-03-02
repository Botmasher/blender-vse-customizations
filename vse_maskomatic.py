import bpy

##	NLE Maskomatic
## by GitHub user Botmasher (Joshua R)
##
## Set up a basic mask for and mask modifier on a single sequence editor strip.
##

# TODO set frames based on total timeline length by default
# TODO allow for other options to be set on mask_strip like inversion
# TODO custom shapes when configuring the mask strip
# TODO custom loc when configuring the mask strip
# TODO automatically load / ask which clip file to be masked over
# 	- should mask-adjusted movie clip data be considered part of the mask model?

def add_mask(strip=bpy.context.scene.sequence_editor.active_strip, first_frame=0, final_frame=0):
	"""Create a mask and mask modifier for one sequence

	Return a mask model mapping to both the mask modifier and the mask strip
	"""

	if strip.type not in ['IMAGE', 'MOVIE']: return None

	mask_name = "mask-test-00"

	# setup mask strip (MovieClip Editor settings)
	if len(bpy.data.movieclips) < 1: return None
	mask_strip = bpy.data.masks.new(mask_name)
	# mask length
	mask_strip.frame_start = first_frame
	mask_strip.frame_end = final_frame

	initial_area = bpy.context.area.type
	bpy.context.area.type = "CLIP_EDITOR"
	# movie clip configuration for cutting and placement of masked strip
	bpy.context.area.spaces.active.clip = bpy.data.movieclips[0]
	bpy.context.area.spaces.active.mode = "MASK"
	bpy.context.area.spaces.active.mask = mask_strip
	bpy.context.area.spaces.active.clip.frame_start = strip.frame_start
	bpy.context.area.spaces.active.clip.frame_offset = strip.animation_offset_start
	# mask geometry
	bpy.ops.mask.primitive_square_add(size=1080, location=(1920 * 0.25, 1080 * 0.5))
	# AFTER geometry points - zeroth layer automatically added with primitive_square_add
	mask_strip.layers[0].invert = False

	# add modifier on the vse strip
	mask_modifier = strip.modifiers.new(mask_name, type="MASK")
	mask_modifier.input_mask_type = "ID"
	mask_modifier.input_mask_id = mask_strip
	strip.blend_type = "ALPHA_OVER"
	strip.blend_alpha = 1.0

	mask = {'modifier': mask_modifier, 'strip': mask_strip}

	return mask

add_mask(first_frame=1, final_frame=250)