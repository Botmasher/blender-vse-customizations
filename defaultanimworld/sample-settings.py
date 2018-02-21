sample_settings = {
	'data': {
		'scenes': {
			'["Scene"]': {
				'game_settings': {
					'material_mode': "GLSL"
				}
			}
		},
		'objects': {
			'delete()': [
				{
					'name': "Cube"
				}
			],
			'new()': [
				{
					'primitive': 'plane',
					'attributes': {
						'name': "bg",
						'location': Vector((0.0, 0.0, 0.0))
					}
				}
			],
		},
		'materials': {
			'delete()': [
				{
					'name': "Material"
				}
			],
			'new()': [
				{
					'name': "bg-color",
					'diffuse_color': (0.53, 0.583, 0.827),
					'diffuse_intensity': 1.0,
					'specular_intensity': 0.0,
					'use_transparent_shadows': True,
					'preview_render_type': "FLAT"
				},
				{
					'name': "color-black",
					'diffuse_color': (0.0, 0.0, 0.0),
					'diffuse_intensity': 1.0,
					'specular_intensity': 0.0,
					'use_transparent_shadows': True,
					'preview_render_type': "FLAT"
				},
				{
					'name': "color-white",
					'diffuse_color': (1.0, 1.0, 1.0),
					'diffuse_intensity': 1.0,
					'specular_intensity': 0.0,
					'use_transparent_shadows': True,
					'preview_render_type': "FLAT"
				}
			]
		},
		'textures': {
			'new()': [
				{
					'name': "sample-texture",
					'type': "CLOUDS"
				}
			]
		}
	},
	'context': {
		'scene': {
			'objects': {
				'["Camera"]': {
					'rotation_euler': (0.0, 0.0, 0.0),
					'location': Vector((0.0, 0.0, 5.0))
				},
				'["Lamp"]': {
					'location': Vector((-2.9, 2.2, 3.0)),
					'parent': bpy.context.scene.objects['Camera'],
					'data': {
						'energy': 1.1,
						'distance': 25.0,
						'shadow_ray_samples': 3
					}
				},
				'[\'bg\']': {
					'scale': Vector((12.0, 12.0, 12.0)),
					'data': {
						'materials': {
							'[0]': 'bg-color' 		# do not use bpy.data.materials if not yet created
						}
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