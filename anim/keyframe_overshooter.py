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
			raise Exception("Failed trying to set keyframe {0} attribute {1} to {2}".format(kf, attr_name, attr_value))
		return kf

	def interpolate_selected_kfs(self, obj, interpolation_type='BACK'):
		"""Set the interpolation for all selected keyframes on selected object"""
		# NOTE: first select kfs in dopesheet or graph or select them programmatically
		keyframes = self.get_selected_kfs(obj)
		for kf in keyframes:
			self.set_kf_attr(kf, 'interpolation', interpolation_type)
		return keyframes

	def is_number(self, value):
		"""Check if a value is of a number type"""
		value_type = type(value)
		return (value_type is int or value_type is float)

	def calculate_vector_overshoot(self, source_v, target_v, overshoot_percent):
		"""Build a new vector with calculated overshoots based on source-target deltas"""
		if len(source_v) != len(target_v) or not self.is_number(overshoot_percent):
			print ("Unable to compare vectors")
			return
		v = []
		for i in range(len(source_v)):
			diff = target_v[i] - source_v[i]
			overshoot = diff * overshoot_percent
			v.append(overshoot)
		return v

	def calculate_plain_overshoot(self, target_v, overshoot_percent):
		"""Build a new vector with calculated overshoots beyond a target value"""
		if len(target_v) != 3 or not self.is_number(overshoot_percent):
			return
		return [value * overshoot_percent for value in target_v]

	def set_kf(self, obj, attr, value, frame):
		"""Insert a keyframe on an object attribute"""
		bpy.context.scene.frame_current = frame
		obj.keyframe_insert(attr)
		setattr(obj, attr, value)
		obj.keyframe_insert(attr)

	def overshoot_transform(self, obj, attr, target_value, frames=5, overshoot_frames=2, overshoot_percent=1.1):
		"""Give current selected keyframes a dynamic interpolation"""
		if not hasattr(obj, attr):
			return

		# frames to kf
		scene = bpy.context.scene
		start_frame = scene.frame_current
		overshoot_frame = start_frame + frames
		final_frame = overshoot_frame + overshoot_frames

		# initial kf
		start_value = getattr(obj, attr)
		print(start_value)
		self.set_kf(obj, attr, start_value, start_frame)

		# overshoot kf
		overshoot_value = self.calculate_vector_overshoot(start_value, target_value, overshoot_percent)
		self.set_kf(obj, attr, overshoot_value, overshoot_frame)

		# target kf
		self.set_kf(obj, attr, target_value, final_frame)

		# reset playhead
		bpy.context.scene.frame_current = start_frame

		return obj.animation_data.action.fcurves

kfer = KeyframeOvershooter()
kfer.overshoot_transform(bpy.context.scene.objects.active, 'location', (2,0,0), frames=6, overshoot_frames=3)
