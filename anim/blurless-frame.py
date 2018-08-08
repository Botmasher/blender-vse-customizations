import bpy

## Blurless Frame
##
## quicky toggle and keyframe motion blur
## example use: move object in a single frame into or out of scene without blur

def is_node_tree(tree):
    return tree and hasattr(tree, 'nodes')

def get_vecblur_nodes(tree):
    nodes = []
    for node in tree:
        node.type == 'VECBLUR' and nodes.append(node)
    return nodes

def blurless_vecblur_stint(tree=None, frames=1):
    if not tree or not frames or not is_node_tree(tree)
    nodes = get_vecblur_nodes(tree)
    for node in nodes:
        node.type == 'VECBLUR' and print(node)
        # toggle and keyframe
        if node.type == 'VECBLUR':
            blur = node.factor  # TODO hi/lo toggle values
            node.keyframe_insert('factor')
            node.factor = 0.0 #blur if node.factor == 0 else blur
            node.keyframe_insert('factor')
            bpy.context.scene.frame_current += blurless_time
            node.factor = blur
            node.keyframe_insert('factor')
    return nodes

node_tree = bpy.context.scene.node_tree
blurless_time = 10  # int prop
blurless_vecblur_stint(tree=node_tree, frames=10)
