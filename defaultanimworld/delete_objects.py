import bpy

def remove_objects(object_names):
	"""Delete existing objects from scene where object name matches a name in the list"""
	object_names = [obj['name'] for obj in object_names] if type(object_names[0]) == dict else object_names
	try:
		getattr(object_names, "append")
	except:
		return False 		# TODO handle type error
	bpy.ops.object.select_all(action="DESELECT")
	for name in object_names:
		try:
			bpy.context.scene.objects[name].select = True
		except:
			pass 	# TODO handle exception: still selected but no longer exists
		bpy.ops.object.delete()
	return True

objects_to_remove = {
	'data': {
		'objects': [
			{
				'name': "Cube"
			},
			{
				'name': "Lamp"
			},
		]
	}
}

# string list works
obj_names_remove = ["Cube", "Lamp"]

remove_objects(objects_to_remove['data']['objects'])
