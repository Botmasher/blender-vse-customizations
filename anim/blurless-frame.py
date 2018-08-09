import bpy

## Blurless Frame
##
## Toggle and keyframe a blurless stint for vector blur nodes
## example use: jump camera in a single frame without blur during movement

# TODO: config bpy.props to pass blurless_frames and adjust factor

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

def set_blurless_node(node, frames):
    """Keyframe turning vector blurring off then back on later"""
    if not is_vecblur_node(node):
        return False
    blur = node.factor
    blurless_rel_keyframes = ((blur, -1), (0.0, 1), (0.0, frames), (blur, 1))
    for kf in blurless_rel_keyframes:
        key_vecblur(node, kf[0], framejump=kbf[1])
    return True

def handle_blurless_stint(tree=bpy.context.scene.node_tree, blurless_frames=1):
    """Turn off blurring on all vector blur nodes during frames count"""
    if not is_node_tree(tree) or not blurless_frames:
        return
    nodes = get_vecblur_nodes(tree)
    for node in nodes:
        node.type == 'VECBLUR' and print(node)
        set_blurless_node(node, blurless_frames)
    return nodes

# test run
blurless_time = 10  # int prop
handle_blurless_stint(blurless_frames=10)
