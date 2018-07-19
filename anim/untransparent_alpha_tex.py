import bpy

## Untransparent Alpha Tex
##
## a Blender Python script by Joshua R (GitHub user Botmasher)
##
## Configure material+texture with transparent image to have a custom background color
##

def set_untransparent(texture_slot, is_transparent=False):
	"""Adjust alpha on rendered texture"""
	texture_slot.texture.use_preview_alpha = is_transparent
	texture_slot.use_map_alpha = is_transparent
	return texture_slot

def untransparent_texture(material=bpy.context.active_object.active_material, toggle=False, color=None, set_all=True):
	"""Configure a material and its image textures to show a diffuse background behind transparent images"""

	# verify reference to material and texture (including slot)
	if not material: return

	texture = material.active_texture

	if not texture or not texture.type == 'IMAGE': return

	texture_slot = material.texture_slots[material.active_texture_index]

	# remove alpha from texture render
	set_untransparent(texture_slot, is_transparent=toggle)

	# adjust opaque material render
	material.preview_render_type = 'FLAT'
	material.use_transparency = not toggle
	material.transparency_method = 'Z_TRANSPARENCY'
	material.alpha = 1.0 if not toggle else 0.0
	material.diffuse_color = color

	# set all textures for this material (since material-wide alpha settings are changing)
	if set_all:
		for texture_slot in material.texture_slots:
			texture_slot and set_untransparent(texture_slot, is_transparent=toggle)

	return (material, texture)

# test call
untransparent_texture(color=(1.0, 1.0, 1.0))
