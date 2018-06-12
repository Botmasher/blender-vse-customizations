import bpy

## Keyframe Overshooter
## script by Joshua R (GitHub user Botmasher)
##
## Overshoot i% over n frames before settling into a final animated value.
##

class KeyframeOvershooter:
	def __init__(self):
		# NOTE add settings params
		#self.overshoot_frames = 3 # unnecessary?
		self.overshoot_strength = 0.2
		self.rebound_frames = 2
		self.rebound_bounce = True
		self.rebound_fraction = 0.4
		# TODO add extra rebound bounces getting recursively smaller and switching polarity
		return

	def get_object_attribute(self, obj, attr_name):
		"""Return the value for an object's named property"""
		return getattr(obj, attr_name, None)

	def check_rebounds(self, keyframe_values, full_value, bounce=1):
		"""Check that rebounds get smaller each time"""
		if bounce-1 > len(keyframe_values):
			return True
		elif keyframe_values[bounce-1] != (self.rebound_fraction ** bounce) * full_value:
			return False
		return self.check_rebounds(keyframe_values, full_value, bounce=bounce+1)

	# TODO test and implement
	def analyze_keyframes(self, keyframes, obj, attr):
		"""Check if the current selection matches an overshoot"""
		expected_kf_count = 2 + self.rebound_bounce 	# overshot + rebound + target
		is_overshoot = False
		# TODO update all getattr to read val at exact kf
		base_attr = getattr(obj, attr)
		if len(keyframes) != expected_kf_count:
			return is_overshoot
		for kf in len(keyframes):
			if kf == 1 and getattr(obj,attr) == base_attr * self.overshoot_strength:
				return True
			elif kf > 2:
				# TODO check that rebounds get smaller each time
			else:
				continue
		return is_overshoot

	def overshoot(self, kf_origin, kf_destination):
		"""Turn current selected keyframes into an overshoot-rebound-settle animation"""
		# NOTE attempt using fcurve dynamics instead
		for fcurve in bpy.context.scene.objects.active.animation_data.action.fcurves:
			print(fcurve)
			if fcurve.select:
				# TODO set curve interpolation to dynamic
				area = bpy.context.area.type
				bpy.context.area.type = 'GRAPH_EDITOR'
				bpy.ops.graph.interpolation_type(type='BACK')
				bpy.context.area.type = area
		# Original Steps:
		# - calculate magnitude from origin to destination
		# - store type of change ("channels") from origin to destination
		# - calculate overshoot
		# - move settle frame rebound_frames later
		# - change this keyframe value to overshoot value
		# - add secondary rebound if self.rebound_bounce

		# NOTE decide whether to store both initial and final kfs through tool
		# 	- setting up all keyframes through tool before running overshoot
		# 	- allows capturig values without having to guess which keyframes to read
		return
