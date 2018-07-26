import bpy

def is_text(obj):
    return obj and hasattr(obj, 'type') and obj.type == 'FONT'

def text_fx(txt_obj):
    if not is_text(txt_obj):
        return
    txt_src = txt_obj.data.body
    for letter in txt_src:
        print(letter)

    # TODO: understand how to split letters within FONT obj and animate separately
    # - text segment approach: https://gitlab.com/bkurdali/blender-addon-experiments/blob/master/text_fx.py
    # - perhaps need to approach different fx from a variety of methods
    # - rot constraints can be applied to every single letter
    #   https://blender.stackexchange.com/questions/36908/letter-by-letter-animation
    # - wiggle achievable with curve
    #   http://www.blenderdiplom.com/en/tutorials/all-tutorials/620-tutorial-animation-nodes-wiggle-explained.html

    return
