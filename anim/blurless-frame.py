import bpy

## Blurless Frame
##
## quicky toggle and keyframe motion blur
## example use: move object in a single frame into or out of scene without blur

def is_node_tree(tree):
    return tree and hasattr(tree, 'nodes')

def get_vecblur_nodes(tree):
    nodes = []
    for node in tree.nodes:
        node.type == 'VECBLUR' and nodes.append(node)
    return nodes

def move_playhead(frames, scene=bpy.context.scene):
    if frames and scene:
        scene.frame_current += frames
    return scene.frame_current

def key_vecblur(node, factor, framejump):
    move_playhead(framejump)
    node.factor = factor
    node.keyframe_insert('factor')
    return node

def set_blurless_node(node, frames):
    if node.type != 'VECBLUR':
        return False
    blur = node.factor  # TODO hi/lo toggle values
    key_vecblur(node, blur, -1)
    key_vecblur(node, 0.0, 1)
    key_vecblur(node, 0.0, frames)
    key_vecblur(node, blur, 1)
    return True

def blurless_vecblur_stint(tree=None, blurless_frames=1):
    if not is_node_tree(tree) or not frames:
        return
    nodes = get_vecblur_nodes(tree)
    for node in nodes:
        node.type == 'VECBLUR' and print(node)
        # turn blur off and back on later
        set_blurless_node(node, frames)
    return nodes

node_tree = bpy.context.scene.node_tree
blurless_time = 10  # int prop
blurless_vecblur_stint(tree=node_tree, blurless_frames=10)
