import bpy

## Keyframe Overshooter
## script by Joshua R (GitHub user Botmasher)
##
## Overshoot i% over n frames before settling into a final animated value.
##

def overshoot():
	"""Give current selected keyframes a dynamic interpolation"""
	obj = bpy.context.scene.objects.active
	areas = bpy.context.screen.areas
	if not obj.animation_data or not obj.animation_data.action:
		print("No keyframes found - select an object")
		return None
	for area in areas:
		if area.type == 'DOPESHEET_EDITOR':
			for fcurve in area.spaces[0].action.fcurves:
				if fcurve.select:
					print(fcurve)
					# TODO set curve interpolation to dynamic
					# area = bpy.context.area.type
					# bpy.context.area.type = 'GRAPH_EDITOR'
					# bpy.ops.graph.interpolation_type(type='BACK')
					# bpy.context.area.type = area
	return

overshoot()
