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
		# TODO add extra rebound bounces getting recursively smaller and switching polarity
		return

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
		# Steps:
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
