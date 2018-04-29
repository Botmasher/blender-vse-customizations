#!/usr/bin/python
import bpy
import re
import time

##
## Find and display relevant media sequence strips from the Blender VSE
##
## Built to catalog assets and display them for copyright/fair use documentation.
##
## Author: Joshua R (GitHub user Botmasher)
##
##	0) locate the run function at the bottom
## 	1) build the dictionary of text to ignore while searching through names
## 	2) build the list of strip types to search for (SOUND, IMAGE, MOVIE)
## 	3) call build_ignored_names_re to turn the ignored text into a regular expression
## 		- optionally pass array of regular expressions to avoid
## 		- I currently separate out calls from the for loop to pass specific regexes for each sequence type
##	4) call find_sequence_names to search through sequences
## 		- check that the scene has a sequence_editor (VSE) before calling
## 		- pass ignore_copies=False to list duplicates as well (e.g. myaudio.001, myaudio.002)
## 	5) call print_sequence_names to output the names to console (shell if running Blender through prompt)
## 	6) run this script in Blender
##

# TODO ignore copies by presence of dups not just by name typology
	# - cases exist where stripname.nnn is the only copy left in the project

def build_ignored_names_re(namestrings, ignored_res_list):
	if namestrings is None or len(namestrings) < 1:
		if ignored_res_list == []: return None
		ignored_re = "|".join(regex.pattern for regex in ignored_res_list)
		return ignored_re
	ignored_namestring = namestrings.pop()
	ignored_res_list.append(re.compile(".*%s.*" % re.escape(ignored_namestring)))
	return build_ignored_names_re(namestrings, ignored_res_list)

def find_sequence_names(sequencer=bpy.context.scene.sequence_editor, sequence_types=["SOUND", "MOVIE", "IMAGE"], ignored_res_dict={}):
	print(ignored_res_dict)
	if sequencer is None:
		print("Error finding sequence names: SEQUENCE_EDITOR not found")
		return None
	found_sequences = {sequence_type: [] for sequence_type in sequence_types}
	for sequence in sequencer.sequences:
		if sequence.type in sequence_types and (ignored_res_dict[sequence.type] is None or re.match(ignored_res_dict[sequence.type], sequence.name) is None):
			found_sequences[sequence.type].append(sequence)
	return found_sequences

def print_sequence_names(sequences_by_type, ignore_copies=True):
	print("\nFound Sequences")
	if ignore_copies:
		split_names = []
		for sequence_type in sequences_by_type:
			for sequence in sequences_by_type[sequence_type]:
				split_name = re.split(r".+(\.\d{3})+", sequence.name)[0]
				split_name != "" and split_names.append(split_name)
		for name in split_names: print(name)
	else:
		for sequence_type in sequences_by_type:
			for sequence in sequences_by_type[sequence_type]:
				print("%s sequence: %s" % (sequence.type, sequence.name))
	return {'FINISHED'}

def run_strip_finder():
	ignored_names = {'SOUND': ["audio-", ".wav"], 'MOVIE': [], 'IMAGE': []}
	sequence_types = ["SOUND", "IMAGE"]
	# build regexes of names to ignore
	for sequence_type in sequence_types:
		ignored_names[sequence_type] = build_ignored_names_re(ignored_names[sequence_type], [])
	# find sequences
	sequences = find_sequence_names(ignored_res_dict=ignored_names, sequence_types=sequence_types)
	# display names
	print_sequence_names(sequences)

run_strip_finder()
