#!/usr/bin/python
import bpy
import bpy.props

## NLE Maskomatic
## by GitHub user Botmasher (Joshua R)
##
## Set up a basic mask and mask modifier for a single sequence editor strip.
##

# TODO apply mask to array of selected strips
# TODO more custom shapes (poly?) when configuring the mask strip
# TODO custom loc, scale when configuring the mask strip
# TODO load / ask which clip file will be masked over
# 	- should mask-adjusted movie clip data be considered part of the mask model?

def add_mask(strip, name, start_frame=0, end_frame=0, shape=None, invert=False):
	"""Create a mask and mask modifier for one sequence

	Return a mask model mapping to both the mask modifier and the mask strip
	"""
	if strip.type not in ['IMAGE', 'MOVIE']: return None

	# setup mask strip (MovieClip Editor settings)
	if len(bpy.data.movieclips) < 1: return None
	mask_strip = bpy.data.masks.new(name)
	# mask length
	mask_strip.frame_start = start_frame
	mask_strip.frame_end = end_frame

	initial_area = bpy.context.area.type
	bpy.context.area.type = "CLIP_EDITOR"
	# movie clip configuration for cutting and placement of masked strip
	bpy.context.area.spaces.active.clip = bpy.data.movieclips[0]
	bpy.context.area.spaces.active.mode = "MASK"
	bpy.context.area.spaces.active.mask = mask_strip
	bpy.context.area.spaces.active.clip.frame_start = strip.frame_start
	bpy.context.area.spaces.active.clip.frame_offset = strip.animation_offset_start
	# mask geometry
	if shape == "circle" or shape == "square":
		# TODO set to movie clip height and width
		res_h = bpy.context.scene.render.resolution_x
		res_w = bpy.context.scene.render.resolution_y
		mask_primitive_add = getattr(bpy.ops.mask, "primitive_%s_add" % shape)
		mask_primitive_add(size=res_h, location=(res_w * 0.25, res_h * 0.5))
	else:
		# zeroth layer automatically added above with primitive
		mask_strip.layers.new()
	mask_strip.layers[0].invert = invert

	# add modifier on the vse strip
	mask_modifier = strip.modifiers.new(name, type="MASK")
	mask_modifier.input_mask_type = "ID"
	mask_modifier.input_mask_id = mask_strip
	strip.blend_type = "ALPHA_OVER"
	strip.blend_alpha = 1.0

	mask = {'modifier': mask_modifier, 'strip': mask_strip}

	bpy.context.area.type = initial_area

	return mask

bpy.types.ImageSequence.maskomatic_name = bpy.props.StringProperty (
	name = "Name",
	default = "mask",
	description = "Name to apply to the mask and the mask modifier"
)

bpy.types.ImageSequence.maskomatic_frame_start = bpy.props.IntProperty (
	name = "Start frame", 
	default = bpy.context.scene.frame_start,
	description = "First timeline frame the underlying mask is available"
)

bpy.types.ImageSequence.maskomatic_frame_end = bpy.props.IntProperty (
	name = "End frame", 
	default = bpy.context.scene.frame_end,
	description = "Last timeline frame the underlying mask is available"
)

bpy.types.ImageSequence.maskomatic_invert = bpy.props.BoolProperty (
	name = "Invert Black/White", 
	default = False,
	description = "Reverse the black/white of the underlying mask"
)

bpy.types.ImageSequence.maskomatic_primitive = bpy.props.EnumProperty(
	items = [("square", "Square", "Add square geometry to mask"),
		("circle", "Circle", "Add circle geometry to mask"),
		("blank", "Blank", "Initialize a blank mask (add points manually)")],
	name = "Shape",
	default = "square",
	description = "Initialize mask with some geometry (mask shape)"
)

class MaskomaticPanel(bpy.types.Panel):
	bl_label = "Maskomatic"
	bl_idname = "strip.maskomatic_panel"
	bl_space_type = "SEQUENCE_EDITOR"
	bl_category = "Modifiers"
	bl_region_type = "UI"

	def draw(self, ctx):
		strip = ctx.scene.sequence_editor.active_strip
		self.layout.row().prop(strip, "maskomatic_name")
		self.layout.row().prop(strip, "maskomatic_primitive")
		self.layout.row().prop(strip, "maskomatic_frame_start")
		self.layout.row().prop(strip, "maskomatic_frame_end")
		row = self.layout.row()
		row.prop(strip, "maskomatic_invert")
		self.layout.column().operator("strip.maskomatic_operator", text="Mask this strip")

class MaskomaticOperator(bpy.types.Operator):
	bl_idname = "strip.maskomatic_operator"
	bl_label = "Maskomatic Operator"
	bl_description = "Create mask and add mask modifier to strip"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(c, ctx):
		return ctx.mode == "OBJECT"

	def execute(self, ctx):
		strip = bpy.context.scene.sequence_editor.active_strip
		name = strip.maskomatic_name
		invert = strip.maskomatic_invert
		shape = strip.maskomatic_primitive
		start_frame = strip.maskomatic_frame_start
		end_frame = strip.maskomatic_frame_end
		add_mask(strip, start_frame=start_frame, name=name, end_frame=end_frame, shape=shape, invert=invert)
		return {'FINISHED'}

def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)

if __name__ == "__main__": register()
