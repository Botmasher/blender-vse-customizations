import bpy

## Keyframe Overshooter
## script by Joshua R (GitHub user Botmasher)
##
## Overshoot i% over n frames before settling into a final animated value.
##

def overshoot(obj=bpy.context.scene.objects.active, ctx=bpy.context, interpolation_type='BACK'):
	"""Give current selected keyframes a dynamic interpolation"""
	if not obj or not obj.animation_data or not obj.animation_data.action:
		print("No keyframes found - select an animated object")
		return None
	area = ctx.area.type
	ctx.area.type = 'GRAPH_EDITOR'
	for curve in obj.animation_data.action.fcurves:
		
		# TODO check for current keyframe - above will set all curves for active obj
		
		if curve.select:
			for kp in curve.keyframe_points:
				kp.interpolation = interpolation_type
		# curve.select and bpy.ops.graph.interpolation_type(type='BACK')

	ctx.area.type = area
	return

overshoot()
