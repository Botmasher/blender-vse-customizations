import bpy
from mathutils import Vector

## Delete existing Blender objects from the current scene

objects_to_remove = {
	'data': {
		'objects': [
			{
				'name': "Cube"
			}
		]
	}
}


bpy.ops.object.select_all(action="DESELECT")
try:
	bpy.context.scene.objects[objects_to_remove['data']['objects'][0]['name']].select = True
except:
	#raise Exception("object deleted but no longer exists in bpy.data.objects")
	pass 	# TODO handle exception: still selected but no longer exists
bpy.ops.object.delete()
