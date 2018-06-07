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
		return

	def analyze_keyframes(self):
		"""Check if the current selection matches an overshoot"""
		return

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
