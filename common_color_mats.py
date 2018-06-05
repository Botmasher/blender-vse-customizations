import bpy

## Create Materials from Common Color Names
## script by Joshua R (GitHub user Botmasher)

class CommonColor:
    color_map = {
        'red': (1.0, 0.0, 0.0),
        'green': (0.0, 1.0, 0.0),
        'blue': (0.0, 0.0, 1.0),
        'yellow': (1.0, 1.0, 0.0),
        'magenta': (1.0, 0.0, 1.0),
        'cyan': (0.0, 1.0, 1.0),
        'white': (1.0, 1.0, 1.0),
        'black': (0.0, 0.0, 0.0)
    }

    def __init__(self, name_base=""):
        """Set name to prefix to color materials"""
        self.material_name_base = name_base
        return

    def assign_color(self, material, color_name):
        """Set the diffuse color of a basic material"""
        if color_name not in self.color_map: return
        material.diffuse_color = self.color_map[color_name]
        # TODO set attr using passed-in settings dict
        material.specular_intensity = 0.0
        material.hardness = 120
        material.use_transparent_shadows = True
        return

    def color_object_material(self, obj=bpy.context.scene.objects.active, color_name=None, existing_material=False):
        """Give selected object a material with a named color"""
        if color_name not in self.color_map: return False
        if existing_material:
            material = obj.active_material
        else:
            material = bpy.data.materials.new(name="{0}{1}".format(self.material_name_base, color_name))
            obj.data.materials.append(material)
        # NOTE select active material here either way?
        self.assign_color(material, color_name)
        return True
