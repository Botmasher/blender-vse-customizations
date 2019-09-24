import bpy

# config properties
tastiness = bpy.props.FloatProperty(name="tastiness", default=276.28)
print(tastiness)

# config property class
class TastyProps(bpy.types.PropertyGroup):
    flavor : bpy.props.StringProperty(
        name = "flavor",
        description = "requested flavor of the tasty",
        default = "chocolate",
    )
    colorized : bpy.props.BoolProperty(
        name = "colorized",
        description = "add rainbow colorings for eyeball fun",
        default = True,
    )
    amount : bpy.props.IntProperty(
        name = "amount",
        description = "how much of the tasty you want",
        default = 1,
    )

# panel
class TastyPanel(bpy.types.Panel):
    bl_idname = "scene.tasty_panel"
    bl_label = "Tasty Panel"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    def draw(self, context):
        scene = context.scene
        flavor = scene.flavor
        colorized = scene.colorized
        amount = scene.amount
        layout.prop(flavor, "tasty_props")
        layout.prop(colorized, "tasty_props")
        layout.prop(amount, "tasty_props")

        return

# operator
class TastyOperator(bpy.types.Operator):
    bl_idname = "scene.tasty_operator"
    bl_label = "Make Tasty"
    x = bpy.props.IntProperty()
    y = bpy.props.IntProperty()

    def execute(self, context):
        self.report({'INFO'}, f"pointing to ({self.x}, {self.y})")
        return {'FINISHED'}

    def invoke(self, context, event):
        self.x = event.mouse_x
        self.y = event.mouse_y
        return self.execute(context)

# registration
ui_classes = (TastyProps, TastyPanel, TastyOperator)
def register():
    [bpy.utils.register_class(ui_class) for ui_class in ui_classes]
    bpy.types.Scene.tasty_props = bpy.props.PointerProperty(type=TastyProps)

def unregister():
    [bpy.utils.unregister_class(ui_class) for ui_class in ui_classes]
    del bpy.types.Scene.tasty_props

if __name__ == '__main__':
    register()
