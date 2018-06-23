#!/usr/bin/python
import bpy

## Frames Spacer-Outer
##
## Blender Python VSE script by Joshua R (GitHub user Botmasher)
##
## Lengthen and separate sequences. Ideal for short strips during manual editing.
## NOTE script logic is derived from framesplitter.py.

def gap_push_strip(sequence, gap=0):
	"""Insert a gap after the strip and push all subsequent strips ahead"""
	bpy.context.scene.frame_current = sequence.frame_start + 1
	bpy.ops.sequencer.gap_insert(frames=gap)
	return sequence

def move_strip(sequence, offset=0):
	"""Move the strip to a new origin along the x axis"""
	sequence.frame_start = offset
	return sequence

def extend_strip(sequence, x_dir):
	"""Linearly lengthen or shrink a single sequence along the x axis"""
	sequence.frame_offset_end -= x_dir
	return sequence

def order_strips(strips):
	"""Reorder a list of sequences by final frame from latest to earliest"""
	strips_by_start_frame = {}
	# map start frames to sequences
	for strip in strips:
		if strip.frame_start not in strips_by_start_frame:
			strips_by_start_frame[strip.frame_start] = []
		strips_by_start_frame[strip.frame_start].append(strip)
	# reorder strips
	reordered_frames = reversed(sorted(strips_by_start_frame.keys()))
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
	strips = order_strips(strips)
	for strip in strips:
		bpy.context.scene.frame_current = strip.frame_start
		strip.select = True
		if strip != strips[0]:
			move_strip(strip, gap=bpy.context.scene.frame_current + (extension + gap))
		extend_strip(strip, extension)
		strip.select = False
	return strips

strips = [strip for strip in bpy.context.scene.sequence_editor.sequences if strip.select]
space_strips(strips, extension=20, gap=10)
