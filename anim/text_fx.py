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
def do_fx (font_obj, fx={}):
    """Keyframe an effect on a letter based on an fx dict

    fx = {
        'name': 'NAME',     # like 'SLIDE'
        'attr': obj.attr,   # attribute to set on obj
        'to': [x, y, z],
        'from': [x, y, z],
        'length': 0,        # frames
        'return': False,    # for fx like 'WIGGLE'
        'sub': {            # additional fx layering
            'type': 'NAME',
            ...
        }
    }
    """

    if not fx or not hasattr(font_obj, fx['attr']):
        return

    if not hasattr(font_obj, 'type') or font_obj.type != 'FONT' or not from_values or not to_values:
        return

    # TODO keyframe location over frame_length frames
    getattr(font_obj, fx['attr']) = fx['from']
    font_obj.keyframe_insert(data_path=fx['attr'])
    bpy.context.scene.frame_current += frame_length
    getattr(font_obj, fx['attr']) = fx['to']
    font_obj.keyframe_insert(data_path=fx['attr'])
    if fx['return']:
        bpy.context.scene.frame_current += frame_length
        getattr(font_obj, fx['attr']) = fx['from']
        font_obj.keyframe_insert(data_path=fx['attr'])

    return font_obj

def get_fx_attr(fx_name):
    fx_attr_map = {
        'WIGGLE': ['rotation_euler', True],
        'SLIDE': ['location', False],
        # TODO support layered fx
        #'WOBBLE': ['rotation_euler', 'location'],
        #'SCALE': [], ...
    }
    return fx_attr_map[fx_name]

def anim_txt(txt="", time_offset=1, fx_name='', fx_from=[], fx_to=[], frames=0, randomize=False):

    if not (txt and type(txt) is str):
        return

    letters = string_to_letters(txt)

    # build fx dict
    fx_attr = get_fx_attr(fx_name)

    if not fx_attr:
        return

    fx = {
        'name': fx_name,
        'attr': fx_attr[:-1],
        'length': frames,
        'from': fx_from,
        'to': fx_to,
        'return': fx_attr[-1]
    }

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

        do_fx(letter, fx)

        # TODO calc randomized values on return fx

    bpy.context.scene.frame_current = start_frame

    return letters

loc_start = [-3.0, letter.location.y, letter.location.z]
loc_end = [letter.location.x, letter.location.y, letter.location.z]
anim_txt("slide the text", fx_name='SLIDE', fx_from=loc_start, fx_to=loc_end, frames=4)

rot_start = letter.rotation_euler
rot_end = [letter.rotation.x, letter.rotation.y, letter.rotation.z + z_rotation]
anim_txt("Wiggle, yeah!", fx_name='WIGGLE', fx_from=rot_start, fx_to=rot_end, frames=5)
