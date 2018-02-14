import bpy
from mathutils import Vector

## Create new Blender objects within the current scene

def create_objects(obj_settings={}):
	"""Create and setup Blender objects in scene from an array of settings dicts"""
	added_objects = []
	for obj in obj_settings:
		added_obj = bpy.data.objects.new(obj.name, None)
		for attr in obj['attributes']:
			setattr(obj, attr, obj['attributes'][attr])
		bpy.context.scene.objects.link(added_obj)
		added_objects.push(added_obj)
	return added_objects

objects_to_add = {
	'data': {
		'objects': [
			{
				'name': "Newly Created Object 0"
				'primitive': 'cube',
				'attributes': {
					'location': Vector(0.0, 0.0, 0.0)
				}
			},
			{
				'name': "Newly Created Object 1"
				'primitive': 'cube',
				'attributes': {
					'location': Vector(1.0, 1.0, 1.0)
				}
			}
		]
	}
}

create_objects(objects_to_add['data']['objects'])
