import bpy
from mathutils import Vector
from defaultanimworld import autoset_attrs

## Automatically set up default anim world
## script by GitHub user Botmasher (Joshua R)
##
## Apply all of my custom world and render settings when starting up a new animation.
## Used for setting up, keyframing and rendering my core animations (my anim.blend files),
## not for cutting rendered sequences (my project.blend files).

# TODO run through and configure the areas and screen panels incl their ratios

# TODO split out adding and deleting objects (it's a separate process)

# TODO handle bpy.data for multiple selected objects (like bpy.data.scenes)

settings = {
	'context': {
		'scene': {
			'objects': {
				'["Camera"]': {
					'location': Vector((0.0, 0.0, 5.0)),
					'rotation_euler': (0.0, 0.0, 0.0)
				},
				'["Lamp"]': {
					'location': Vector((-4.0, 1.5, 6.5)),
					'parent': bpy.context.scene.objects['Camera'],
					'data': {
						'energy': 1.1,
						'distance': 25.0,
						'shadow_ray_samples': 3
					}
				}
			},
			'render': {
				'resolution_x': 1920,
				'resolution_y': 1080,
				'resolution_percentage': 100,
				'antialiasing_samples': "5",
				'alpha_mode': "TRANSPARENT",
				'filepath': "../render/",
				'image_settings': {
					'file_format': "JPEG"
				}
			},
			'frame_start': 1,
			'frame_end': 1500,
			'world': {
				'light_settings': {
					'use_environment_light': True,
					'environment_energy': 0.9,
					'gather_method': "RAYTRACE",
					'distance': 0.01,
					'samples': 4
				}
			}
		},
		'window': {
			'screen': {
				'areas': {
					'[4]': {
						'spaces': {
							'active': {
								'show_manipulator': False
							}
						}
					}
				}
			}
		}
	}
}

autoset_attrs(settings)
