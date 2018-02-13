import bpy
from mathutils import Vector

## Create new Blender objects within the current scene

objects_to_add = {
	'data': {
		'objects': [
			{
				'name': "Newly Created Object 0"
				'primitive': 'cube',
				'location': Vector(0.0, 0.0, 0.0)
			}
		]
	}
}

# - set up recursive search like autoset_named_attributes
# - add each object to scene
added_object = bpy.data.objects.new(objects_to_add['data']['objects'][0].name, None) 
added_object.location = objects_to_add['data']['objects'][0].location
bpy.context.scene.objects.link(added_object)
