import bpy
import bpy.props

## Blurless Frames
##
## Toggle and keyframe a blurless stint for vector blur nodes
## example use: jump camera in a single frame without blur during movement

def define_blurless_props(types=bpy.types):
    """Create properties for adjusting blurless vec blur length and strength"""
    types.Scene.blurless_frames = bpy.props.IntProperty(name="Blurless length", description="Frame count of blurless vec blur stints", default=1)
    types.Scene.blurless_factor = bpy.props.FloatProperty(name="Blurless factor", description="How low to set vec blur during blurless frames", default=0.0)
    return

def is_node_tree(obj):
    """Check if the object is a node tree"""
    return obj and hasattr(obj, 'nodes')

def is_vecblur_node(obj):
    """Check if the object is a vector blur node"""
    return obj and obj.type == 'VECBLUR'

def move_playhead(frames, scene=bpy.context.scene):
    """Move the scene timeline playhead relative to its current frame position"""
    if frames and scene:
        scene.frame_current += frames
        return scene.frame_current

def get_vecblur_nodes(tree):
    """Return a list of all vector blur nodes in the node tree"""
    nodes = []
    for node in tree.nodes:
        node.type == 'VECBLUR' and nodes.append(node)
    return nodes

def key_vecblur(node, factor, framejump=0):
    """Keyframe the blur factor for one vector blur node framejump frames from current frame"""
    if not is_vecblur_node(node):
        return False
    move_playhead(framejump)
    node.factor = factor
    node.keyframe_insert('factor')
    return node

def set_blurless_node(node, frames, factor):
    """Keyframe turning vector blurring off then back on later"""
    if not is_vecblur_node(node):
        return False
    blur = node.factor
    blurless_rel_keyframes = ((blur, -1), (factor, 1), (factor, frames), (blur, 1))
    for kf in blurless_rel_keyframes:
        key_vecblur(node, kf[0], framejump=kf[1])
    return True

def handle_blurless_stint(tree=bpy.context.scene.node_tree, blurless_frames=1, blurless_factor=0.0):
    """Turn off blurring on all vector blur nodes during frames count"""
    if not is_node_tree(tree) or not blurless_frames:
        return
    nodes = get_vecblur_nodes(tree)
    for node in nodes:
        node.type == 'VECBLUR' and print(node)
        set_blurless_node(node, blurless_frames, blurless_factor)
    return nodes

class BlurlessPanel(bpy.types.Panel):
    bl_label = "Blurless"
    bl_idname = 'scene.blurless_panel'
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Blurless"

    def draw(self, ctx):
        scene = bpy.context.scene
        layout = self.layout
        col = layout.column(align=True)
        col.label("Config blurless:")
        col.row().prop(scene, "blurless_frames")
        col.row().prop(scene, "blurless_factor")
        col.label("Run blurless:")
        row = col.row(align=True)
        row.operator('scene.blurless_op', text="blurless stint")
        return

class BlurlessOperator(bpy.types.Operator):
    bl_label = "Blurless Frames"
    bl_idname = 'scene.blurless_op'
    bl_description = "Keyframe blurless vec blur frames"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(c, ctx):
        return ctx.mode == "OBJECT"

    def execute(self, context):
        frames = bpy.context.scene.blurless_frames
        factor = bpy.context.scene.blurless_factor
        # TODO fix blurless frames not setting when frames > 1
        handle_blurless_stint(blurless_frames=frames, blurless_factor=factor)
        return {'FINISHED'}

def register():
    define_blurless_props()
    bpy.utils.register_class(BlurlessPanel)
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_class(BlurlessPanel)
    bpy.utils.unregister_module(__name__)

__name__ == "__main__" and register()
