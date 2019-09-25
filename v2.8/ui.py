import bpy

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
    # where and how tool appears in interface
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"       
    bl_context_mode = "object"
    bl_category = "Tasty!"

    # NOTE: display UI other places
    # space_types = [
    #   'EMPTY', 'VIEW_3D', 'IMAGE_EDITOR',
    #   'NODE_EDITOR', 'SEQUENCE_EDITOR', 'CLIP_EDITOR',
    #   'DOPESHEET_EDITOR', 'GRAPH_EDITOR', 'NLA_EDITOR',
    #   'TEXT_EDITOR', 'CONSOLE', 'INFO',
    #   'TOPBAR', 'STATUSBAR', 'OUTLINER',
    #   'PROPERTIES', 'FILE_BROWSER', 'PREFERENCES'
    # ]
    #
    # region_types = [
    #   'WINDOW', 'HEADER', 'CHANNELS',
    #   'TEMPORARY', 'UI', 'TOOLS',
    #   'TOOL_PROPS', 'PREVIEW', 'HUD',
    #   'NAVIGATION_BAR', 'EXECUTE', 'FOOTER',
    #   'TOOL_HEADER'
    # ]

    def draw(self, context):
        layout = self.layout
        tasty_props = context.scene.tasty_props
        layout.prop(tasty_props, "flavor")
        layout.prop(tasty_props, "colorized")
        layout.prop(tasty_props, "amount")
        layout.operator(TastyOperator.bl_idname)

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
def do_classes(action=None):
    if action:
        ui_classes = (
            TastyProps,
            TastyPanel,
            TastyOperator
        )
        [action(ui_class) for ui_class in ui_classes]
    return ui_classes

def register():
    do_classes(bpy.utils.register_class)
    bpy.types.Scene.tasty_props = bpy.props.PointerProperty(type=TastyProps)

def unregister():
    do_classes(bpy.utils.unregister_class)
    del bpy.types.Scene.tasty_props

if __name__ == '__main__':
    register()
