import bpy
from bpy.props import FloatProperty

## Nonuniform Scale Slider for Transform Strips
##
## Blender Python script by Joshua R (GitHub user Botmasher)

bpy.types.TransformSequence.scale_factor = FloatProperty(
    name="Ratio Scale",
    description="Same ratio nonuniform rescale factor for transform strip",
    default=1.0
)

def is_transform_strip(strip):
    if strip.type == 'TRANSFORM' and type(strip.bl_rna) == bpy.types.TransformSequence:
        return True
    return False

def scale_transform_strip(strip, factor_x=1.0, factor_y=1.0, uniform=False):
    if not is_transform_strip(strip):
        return
    strip.scale_start_x *= factor_x
    if not uniform:
        strip.scale_start_y *= factor_x
    else:
        strip.scale_start_y *= factor_y
    return strip

strip = bpy.context.scene.sequence_editor.active_strip
scale_transform_strip(strip, factor_x=0.5)

# TODO get props and ui right (add to existing?)
#   - only show if not .use_uniform_scale
