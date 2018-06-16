import bpy

## Untransparent Alpha Tex
##
## a Blender Python script by Joshua R (GitHub user Botmasher)
## 
## Configure material+texture with transparent image to have a custom background color
##

# Basic steps:
# - get current material
# - get current tex
# - switch current tex alpha to 0.0
# - switch current material alpha to on (verify)
# - set current material alpha to 1.0

def untransparent_texture(material=bpy.context.active_object.active_material, toggle=False, color=None, set_all=False):
	"""Configure a material and its image textures to show a diffuse background behind transparent images"""
	if not material: return
	texture = mat.active_texture
	if not texture or not texture.type == 'IMAGE': return

	# remove alpha from tex render
	texture.use_preview_alpha = False
	texture.use_map_alpha = False

	# adjust alpha for opaque mat render
	material.preview_render_type = 'FLAT'
	material.use_transparency = True
	material.transparency_method = 'Z_TRANSPARENCY'
	material.alpha = 1.0

	# TODO correctly add color to mat to appear as tex img bg
	material.diffuse_color = color

	# TODO set all textures for this material (since material-wide alpha settings are changing)
	for texture in material.texture_slots:
		continue

	return (material, texture)
