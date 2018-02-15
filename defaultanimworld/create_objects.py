import bpy
from mathutils import Vector

## Create new Blender objects within the current scene

def create_objects(objects_settings={}):
	"""Create and setup Blender objects in scene from an array of settings dicts"""
	added_objects = []
	added_object = None
	for object_config in objects_settings:
		# primitive mesh object
		if 'primitive' in object_config:
			try:
				add_primitive = getattr(bpy.ops.mesh, "primitive_%s_add" % object_config['primitive'])
				add_primitive()
				added_obj = bpy.context.scene.objects.active 	# tested: new primitive now active even when multiple prior objects had been selected
			except:
				continue 		# TODO handle cannot add primitive (incl primitive_x_add method not found)
		# blank object
		else:
			added_obj = bpy.data.objects.new(obj.name, None)
			bpy.context.scene.objects.link(added_obj)
		for attr in object_config['attributes']:
			try:
				setattr(added_obj, attr, object_config['attributes'][attr])
			except:
				continue 		# TODO handle reporting what failed to set
		added_objects.append(added_obj)
	return added_objects

objects_to_add = {
	'data': {
		'objects': [
			{
				'primitive': 'cube',
				'attributes': {
					'name': "Newly Created Cube",
					'location': Vector((0.0, 0.0, 0.0))
				}
			},
			{
				'primitive': 'uv_sphere',
				'attributes': {
					'name': "Newly Created Sphere",
					'location': Vector((1.0, 1.0, 1.0))
				}
			}
		]
	}
}

create_objects(objects_to_add['data']['objects'])
