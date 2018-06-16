import bpy

## Keyframe Overshooter
## script by Joshua R (GitHub user Botmasher)
##
## Overshoot i% over n frames before settling into a final animated value.
##

# NOTE big overhaul - now goes through selected keyframes in graph/dopesheet

# TODO add visual to dopesheet showing which interpolation used by selected kfs

def is_anim(obj):
	if not obj or not obj.animation_data or not obj.animation_data.action:
		print("No keyframes found - select an animated object")
		return False
	return True

def get_selected_kfs(obj=bpy.context.scene.objects.active):
	if not is_anim(obj): return
	kfs = []
	for curve in obj.animation_data.action.fcurves:
		for kp in curve.keyframe_points:
			if kp.select_control_points:
				kfs.append(kp)
	return kfs

def set_kf_attr(kf, attr_name, attr_value):
	if not is_anim(obj): return
	try:
		setattr(kf, attr_name, attr_value)
	except:
		print("Failed trying to set keyframe {0} attribute {1} to {2}".format(kf, attr_name, attr_value))
		continue
	return kf

def overshoot(obj=bpy.context.scene.objects.active, ctx=bpy.context, interpolation_type='BACK'):
	"""Give current selected keyframes a dynamic interpolation"""
	if not is_anim(obj): return

	# NOTE first select kfs in dopesheet or graph or select them programmatically

	keyframes = get_selected_kfs(obj)
	for kf in keyframes:
		set_kf_attr(kf, 'interpolation', interpolation_type)
	return

overshoot()
