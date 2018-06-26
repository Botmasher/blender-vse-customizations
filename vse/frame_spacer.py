#!/usr/bin/python
import bpy

## Frames Spacer-Outer
##
## Blender Python VSE script by Joshua R (GitHub user Botmasher)
##
## Lengthen and separate sequences. Ideal for short strips during manual editing.
## NOTE script logic is derived from framesplitter.py.

def move_strip(sequence, offset=0):
	"""Move the strip to a new origin along the x axis"""
	if sequence and offset:
		sequence.frame_start += offset
	return sequence

def extend_strip(sequence, x_dir):
	"""Linearly lengthen or shrink a single sequence along the x axis"""
	if sequence and x_dir:
		sequence.frame_offset_end -= x_dir
	return sequence

def order_strips_by_time(strips, reverse=False):
	"""Reorder a list of sequences by final frame from latest to earliest"""
	strips_by_start_frame = {}
	# map start frames to sequences
	for strip in strips:
		if strip.frame_start not in strips_by_start_frame:
			strips_by_start_frame[strip.frame_start] = []
		strips_by_start_frame[strip.frame_start].append(strip)
	# reorder strips
	reverse: reordered_frames = reversed(sorted(strips_by_start_frame.keys()))
	reordered_strips = []
	for frame in reordered_frames:
		for strip in strips_by_start_frame[frame]:
			reordered_strips.append(strip)
	return reordered_strips

def space_strips(strips, extension=0, gap=0):
	"""Cut a sequencer strip into uniformly stepped and spaced substrips.
	Arguments:
	strips -- list of sequences in the sequence editor
	extension -- the left or right hand lengthening in frames applied to each strip
	gap -- the empty space in frames to leave between each strip
	"""
	if not strips or len(strips) < 1: return strips
	strips = order_strips_by_time(strips, reverse=True)
	for i in range(len(strips)):
		# move sequence accounting for how many previous strips will also move
		strip = strips[i]
		count_remaining_strips = (len(strips) - 1) - i
		strip.select = True
		offset = (gap + extension) * count_remaining_strips
		move_strip(strip, offset=offset)
		# lengthen sequence
		extend_strip(strip, extension)
		strip.select = False
	return strips

strips = [strip for strip in bpy.context.scene.sequence_editor.sequences if strip.select]
for strip in strips:
	print(strip.name)
space_strips(strips, extension=20, gap=10)
