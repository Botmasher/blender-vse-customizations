#!/usr/bin/env python
import bpy

## Many Material+Textures Cloner
## by GitHub user Botmasher (Joshua R)
## 
## Task: 	Duplicate one material with its associated textures into an array of named materials.
## Use: 	Create many separate objects with the same textures that can independently toggle texes on/off.
## 			(When texes are associated with the same material across objects, setting one to active/inactive
## 			sets for all objects with that material)

def duplicate_material_across_names (names=[], obj=None):
	"""Make as many duplicates of the selected object's active material as there are
	names in passed-in names list"""

	if obj is None: obj = bpy.context.scene.objects.active
	material = obj.active_material

	if material is None:
		raise Exception("Many MatTex Cloner - no active material selected to clone!")
		return

	# for each name in the list
	for name in names:

		# mat_new = obj.data.materials.new(name=name)
		#obj.data.materials.append(mat_new)

		# make a copy of the active material
		mat_new = material.copy()
		mat_new.name = name
		# attach copy to active object - just add it to same object for now
		obj.data.materials.append(mat_new)

	return obj.data.materials

# TODO apply to an array of objects (just all selected objects), one per object

# test
material_names = ['mat-0', 'mat-1', 'mat-2', 'mat-3', 'mat-4']
materials = duplicate_material_across_names(names=material_names)

for mat in materials: print(mat)
