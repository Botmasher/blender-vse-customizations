#!/usr/bin/python
import bpy

## Frames Spacer-Outer
##
## Blender Python VSE script by Joshua R (GitHub user Botmasher)
##
## Lengthen and separate sequences. Ideal for short strips during manual editing.
## NOTE script logic is derived from framesplitter.py.

def gap_push_strip(sequence, gap):
	"""Insert a gap after the strip and push all subsequent strips ahead"""
	bpy.context.scene.frame_current = sequence.frame_start + 1
	bpy.ops.sequencer.gap_insert(frames=gap)
	return sequence

def move_strip(sequence, offset):
	"""Move the strip to a new origin along the x axis"""
	sequence.frame_start = offset
	return sequence

def extend_strip(sequence, x_dir):
	"""Linearly lengthen or shrink a single sequence along the x axis"""
	sequence.frame_offset_end -= x_dir
	return sequence

def space_strips(strips, extension=0, gap=0):
	"""Cut a sequencer strip into uniformly stepped and spaced substrips.

	Arguments:
	strips -- list of sequences in the sequence editor
	extension -- the left or right hand lengthening in frames applied to each strip
	gap -- the empty space in frames to leave between each strip
	"""

	for strip in reverse(strips):
		strip.select = True

		move_strip(strip, bpy.context.scene.frame_current + (extension + gap))
		extend_strip(strip, extension)

        strip.select = False

	return strips

space_strips(bpy.context.scene.sequence_editor.sequences)
