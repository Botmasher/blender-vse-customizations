import bpy

## Keyframe Overshooter
## script by Joshua R (GitHub user Botmasher)
##
## Overshoot i% over n frames before settling into a final animated value.
##

# NOTE big overhaul - now goes through selected keyframes in graph/dopesheet

# TODO add visual to dopesheet showing which interpolation used by selected kfs

class KeyframeOvershooter():
	def __init__(self):
		return

	def is_animated(self, obj):
		if not obj or not obj.animation_data or not obj.animation_data.action:
			print("No keyframes found - select an animated object")
			return False
		return True

	def get_selected_kfs(self, obj=bpy.context.scene.objects.active):
		if not self.is_animated(obj):
			return
		kfs = []
		for curve in obj.animation_data.action.fcurves:
			for kp in curve.keyframe_points:
				if kp.select_control_points:
					kfs.append(kp)
		return kfs

	def set_kf_attr(self, kf, attr_name, attr_value):
		if not self.is_animated(obj):
			return
		try:
			self.setattr(kf, attr_name, attr_value)
		except:
			print("Failed trying to set keyframe {0} attribute {1} to {2}".format(kf, attr_name, attr_value))
			continue
		return kf

	def interpolate_selected_kfs(self, obj, interpolation_type='BACK'):
		"""Set the interpolation for all selected keyframes on selected object"""
		# NOTE: first select kfs in dopesheet or graph or select them programmatically
		keyframes = self.get_selected_kfs(obj)
		for kf in keyframes:
			self.set_kf_attr(kf, 'interpolation', interpolation_type)
		return keyframes

	def overshoot(self, obj, attr, value, frames=5, overshoot_frames=2, overshoot_percent=1.1):
		"""Give current selected keyframes a dynamic interpolation"""
		if not hasattr(obj, attr):
			return

		start_frame = bpy.context.scene.frame_current
		obj.keyframe_insert(attr)
		bpy.context.scene.frame_current += frames
		obj.keyframe_insert(attr)
		setattr(obj, attr, value * overshoot_percent)
		obj.keyframe_insert(attr)
		bpy.context.scene.frame_current += overshoot_frames
		obj.keyframe_insert(attr)
		setattr(obj, attr, value)
		obj.keyframe_insert(attr)
		bpy.context.scene.frame_current = start_frame

		return obj.animation_data.action.fcurves

kfer = KeyframeOvershooter()
kfer.overshoot(bpy.context.scene.objects.active, 'location', (2,0,0), frames=6, overshoot_frames=3)
