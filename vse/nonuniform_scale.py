import bpy
from bpy.props import FloatProperty

## Nonuniform Scale Slider for Transform Strips
##
## Blender Python script by Joshua R (GitHub user Botmasher)

bpy.types.TransformSequence.scale_factor = FloatProperty(
    name="Ratio Scale",
    description="Same ratio nonuniform rescale factor for transform strip",
    default=1.0,
    min=0.0,
    max=10
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

# strip = bpy.context.scene.sequence_editor.active_strip
# scale_transform_strip(strip, factor_x=0.5)

# TODO use custom property driver instead
# - add driver to scale_factor prop
# - set driver target to obj scale (both x and y)
# - calc scale using scale_factor
def setup_driver():
    #area = bpy.context.area.type
    #bpy.context.area.type = 'SEQUENCE_EDITOR'
    strip = bpy.context.scene.sequence_editor.active_strip
    # TODO allow toggling off from panel
    driver_curve = strip.driver_add('scale_start_x')
    driver = driver_curve.driver
    driver_var = driver.variables.new()
    driver_var.name = 'scale_x_driver * 2.0'
    driver_target = driver_var.targets[0]
    driver_target.id_type = 'SCENE'
    driver_target.id = bpy.context.scene
    driver_target.data_path = '{0}.{1}'.format(strip.path_from_id(), 'scale_factor')

    driver.expression = 'scale_x_driver * 2.0'
    driver.use_self = True

    #driver_curve = strip.driver_add('scale_start_y')
    #driver_var = driver_curve.driver.variables.new()
    #driver_var.targets[0].data_path = '{0}.{1}'.format(strip.path_from_id(), 'scale_factor')
    #bpy.context.area.type = area

def panel_scale_slider(self, ctx):
    #user_preferences = ctx.user_preferences
    #addon_preferences = ctx.user_preferences.addons[__package__].preferences
    strip = ctx.scene.sequence_editor.active_strip
    if not is_transform_strip(strip) or strip.use_uniform_scale:
        return
    layout = self.layout
    layout.prop(strip, 'scale_factor', slider=True)

def register():
    if hasattr(bpy.types.SEQUENCER_PT_effect, 'panel_scale_slider'):
        delattr(bpy.types.SEQUENCER_PT_effect, 'panel_scale_slider')
    bpy.types.SEQUENCER_PT_effect.append(panel_scale_slider)

if __name__ == '__main__':
    print(__package__)
    register()
