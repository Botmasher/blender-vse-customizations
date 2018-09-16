import bpy
import random

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

## take txt input and turn it into single-letter text objects
def string_to_letters(txt=""):
    origin = [0, 0, 0]
    offset_x = 0
    spacing = 0.5
    letter_objs = []
    for l in txt:
        if l != " ":
            letter = bpy.data.curves.new(name="\"{0}\"-letter-{1}".format(txt, l), type="FONT")
            letter.body = l
            letter_obj = bpy.data.objects.new(letter.name, letter)
            bpy.context.scene.objects.link(letter_obj)
            letter_obj.location = [offset_x, *origin[1:]]
            letter_objs.append(letter_obj)
        offset_x += spacing
    return letter_objs

# temp method for constructing fx
def do_fx (font_obj, frame_start, frame_length=5, fx="slide_in_R"):

    if type(font_obj) is not 'FONT':
        return

    if fx == "slide_in_R":
        # TODO keyframe location over frame_length frames

    return font_obj

def anim_txt(txt="", time_offset=0, randomize=False):

    if not (txt and type(txt) is str):
        return

    letters = string_to_letters(txt)

    offsets = [i * time_offset for i in range(len(letters))]
    randomize and random.shuffle(offsets)
    start_frame = bpy.context.scene.frame_current

    # TODO think through tricky cases where fx have:
    # - staggered starts but ending at the same frame
    # - logarithmic staggered starts or ends
    # - randomizing or complex animations
    # - ...

    # keyframe effect for each letter
    for i in range(len(letters)):
        letter = letters[i]
        frame = start_frame + offsets[i]
        bpy.context.scene.frame_current = frame
        # TODO run specific fx
        do_fx(letter, frame)

    bpy.context.scene.frame_current = start_frame

    return letters

anim_txt("asdf yeah!")
