import bpy
from mathutils import Vector

def list_object_names(objects):
	return map(lambda o: o.name, objects)

def remove_objects(object_names, map_names=False):
	"""Delete existing objects from scene where object name matches a name in the list"""
	object_names = list_object_names(object_names) if map_names else object_names
	bpy.ops.object.select_all(action="DESELECT")
	for name in object_names:
		try:
			bpy.context.scene.objects[name].select = True
		except:
			pass 	# TODO handle exception: still selected but no longer exists
		bpy.ops.object.delete()
		#bpy.context.scene.objects[name].select = False

objects_to_remove = {
	'data': {
		'objects': [
			{
				'name': "Cube"
			}
		]
	}
}
