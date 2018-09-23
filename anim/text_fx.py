import bpy
import random
from bpy.props import *

def is_text(obj):
    return obj and hasattr(obj, 'type') and obj.type == 'FONT'

## take txt input and turn it into single-letter text objects
def string_to_letters(txt="", spacing=0.0):
    origin = [0, 0, 0]
    offset_x = 0
    letter_objs = []
    for l in txt:
        letter = bpy.data.curves.new(name="\"{0}\"-letter-{1}".format(txt, l), type="FONT")
        letter.body = l if l != " " else "a"
        letter_obj = bpy.data.objects.new(letter.name, letter)
        bpy.context.scene.objects.link(letter_obj)
        letter_obj.location = [offset_x, *origin[1:]]

        # base spacing on letter width
        bpy.context.scene.update()
        letter_offset = letter_obj.dimensions.x + spacing
        offset_x += letter_offset

        # delete blank spaces
        if l == " ":
            for obj in bpy.context.scene.objects:
                obj.select = False
            letter_obj.select = True
            bpy.ops.object.delete()
        else:
            letter_objs.append(letter_obj)

    return letter_objs

# temp method for constructing fx
def keyframe_letter_fx (font_obj, fx={}):
    """Keyframe an effect on a letter based on an fx dict

    fx = {
        'name': '',         # like 'SLIDE'
        'attr': '',         # attribute to set on obj
        'to_from': '10',    # point-to-point, cyclical, custom
        'change': [],       # delta (1) from base value (0)
        'length': 0         # frames
    }
    """

    if not fx or not hasattr(font_obj, fx['attr']):
        return

    if not hasattr(font_obj, 'type') or font_obj.type != 'FONT' or not 'attr' in fx:
        return

    def set_kf(obj, attr=None, value=None, frame_skip=0):
        if not hasattr(obj, attr) or not hasattr(obj, 'keyframe_insert') or not value:
            return
        setattr(obj, attr, value)
        kf = obj.keyframe_insert(data_path=attr)
        bpy.context.scene.frame_current += frame_skip
        return kf

    # TODO keyframe location over frame_length frames

    start_value = getattr(font_obj, fx['attr']).copy()
    changed_value = fx['change']

    # keyframe effect
    for target in fx['to_from']:
        fx_value = changed_value if target == '1' else start_value
        print("setting {0} to {1}".format(fx['attr'], fx_value))
        set_kf(font_obj, attr=fx['attr'], value=fx_value, frame_skip=fx['length'])
    # undo last frame skip since not adding another kf
    bpy.context.scene.frame_current -= fx['length']

    return font_obj

def get_fx_map(fx_name):
    WIGGLE = 'WIGGLE'
    SLIDE_IN = 'SLIDE_IN'
    SLIDE_OUT = 'SLIDE_OUT'
    name = 'name'
    attr = 'attr'
    to_from = 'to_from'
    fx_map = {
        WIGGLE: {
            name: WIGGLE,
            attr: 'rotation_euler',
            to_from: '010'
        },
        SLIDE_IN: {
            name: SLIDE_IN,
            attr: 'location',
            to_from: '10'
        },
        SLIDE_OUT: {
            name: SLIDE_OUT,
            attr: 'location',
            to_from: '01'
        }
        # TODO support layered fx
        #'WOBBLE': ['rotation_euler', 'location'],
        #'SCALE': [], ...
    }
    if not fx_name in fx_map:
        return
    return fx_map[fx_name]

def anim_txt(txt="", time_offset=1, fx_name='', fx_delta=None, frames=0, spacing=0.0, randomize=False):

    if not (txt and type(txt) is str and fx_delta):
        return

    letters = string_to_letters(txt, spacing=spacing)

    # build fx dict
    fx = get_fx_map(fx_name)

    if not fx:
        return

    fx['length'] = frames
    fx['change'] = fx_delta

    offsets = [i * time_offset for i in range(len(letters))]
    randomize and random.shuffle(offsets)
    start_frame = bpy.context.scene.frame_current

    # TODO think through tricky cases where fx have:
    # - staggered starts but ending at the same frame
    # - logarithmic staggered starts or ends
    # - randomizing or complex animations
    # - ...

    # set up parent for holding letters
    empty_data = bpy.data.objects.new("letter_fx", None)
    letters_empty = bpy.context.scene.objects.link(empty_data)
    letters_empty.draw_size = 1.0
    letters_empty.draw_type = 'ARROWS'

    # store properties in empty
    empty.text_fx_props.frames = frames
    empty.text_fx_props.spacing = spacing
    empty.text_fx_props.randomize = randomize
    empty.text_fx_props.name = fx_name
    empty.text_fx_props.txt = txt

    # TODO use parent to align letters (without realignment they grow to right)

    # keyframe effect for each letter
    for i in range(len(letters)):
        letter = letters[i]

        # attach to parent but remove offset
        letter.parent = letters_empty
        letter.matrix_parent_inverse = letters_empty.matrix_world.inverse()

        frame = start_frame + offsets[i]
        bpy.context.scene.frame_current = frame

        keyframe_letter_fx(letter, fx)

        # TODO calc randomized values on return fx

    bpy.context.scene.frame_current = start_frame

    return letters

# TODO set up props menu on empty (also shows up on letter select?)
#   - modify the existing fx
#   - update the text string

class TextFxProperties(bpy.types.PropertyGroup):
    name = StringProperty(name="Letter Effect name", description="Name of the effect applied to letters")
    txt = StringProperty(name="Letter Effect text", description="Text that was split into animated letters")
    frames = IntProperty(name="Letter Effect frames", description="Frame duration of effect on each letter", default=5)
    spacing = FloatProperty(name="Letter Effect spacing", description="Distance between letters", default=0.0)
    time_offset = IntProperty(name="Letter Effect timing", description="Frames to wait between each letter's animation", default=1)
    randomize = BoolProperty(name="Randomize Letter Effect", description="Vary the time offset for each letter's animation", default=False)

#loc_deltas = [-3.0, 0.0, 0.0]
#anim_txt("slide the text", fx_name='SLIDE_IN', fx_delta=loc_deltas, frames=4)

rot_deltas = [0.0, 0.0, 0.5]
anim_txt("Wiggle, yeah!", fx_name='WIGGLE', fx_delta=rot_deltas, frames=5, spacing=0.1)

def register():
    bpy.utils.register_class(TextFxProperties)
    bpy.types.Object.text_fx_props = bpy.props.PointerProperty(type=PropertyGroup)

if __name__ == '__main__':
    register()
