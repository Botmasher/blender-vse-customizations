#!/usr/bin/python
import bpy
import re

##
## Find and display relevant media sequence strips from the Blender VSE
##
## Built to catalog assets and display them for copyright/fair use documentation.
##
## Author: Joshua R (GitHub user Botmasher)
##
## 	1) build a list of text to ignore while searching through names
## 	2) build a list of strip types to search for (SOUND, IMAGE, MOVIE)
## 	3) call build_ignored_namestrings_re to turn the ignored text into a regular expression
##	4) call find_sequence_names to search through sequences
## 		- check that the scene has a sequence_editor (VSE) before calling
## 		- pass ignore_copies=False to list duplicates as well (e.g. myaudio.001, myaudio.002)
## 	5) call print_sequence_names to output the names to console (shell if running Blender through prompt)
## 	6) run this script in Blender
##

# TODO dict to ignore text per sequence type, e.g. ignore sound files with "audio-" in the name but not movies
ignored_names = ["audio-0", "-cut-"]
sequence_types = ["SOUND"]

def build_ignored_namestrings_re(namestrings, ignored_res_list=[]):
	if len(namestrings) < 1:
		if ignored_res_list == []:
			return None
		ignored_re = "|".join(regex.pattern for regex in ignored_res_list)
		print(ignored_re)
		return ignored_re
	ignored_namestring = namestrings.pop()
	ignored_res_list.append(re.compile(".*%s.*" % re.escape(ignored_namestring)))
	return build_ignored_namestrings_re(namestrings, ignored_res_list)

def find_sequence_names(sequencer=bpy.context.scene.sequence_editor, sequence_types=["SOUND", "MOVIE", "IMAGE"], ignored_re=None, ignore_copies=True):
	if sequencer is None:
		print("Error finding sequence names: SEQUENCE_EDITOR not found")
		return None
	found_sequences = {}
	for sequence in sequencer.sequences:
		if ignore_copies == False or re.match(r".+(\.\d{3})", sequence.name) is None:
			if sequence.type in sequence_types and (ignored_re is None or re.match(ignored_re, sequence.name) is None):
				if sequence.type not in found_sequences: found_sequences[sequence.type] = []
				found_sequences[sequence.type].append(sequence)
	return found_sequences

def print_sequence_names(sequences_by_type):
	print("""Found Sequences""")
	for sequence_type in sequences_by_type:
		for sequence in sequences_by_type[sequence_type]:
			print("%s sequence: %s" % (sequence.type, sequence.name))
	return {'FINISHED'}

ignored_re = build_ignored_namestrings_re(ignored_names)
sequences = find_sequence_names(ignored_re=ignored_re, sequence_types=sequence_types)
print_sequence_names(sequences)
