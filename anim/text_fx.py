import bpy
import random
from bpy.props import *

def is_text(obj):
    return obj and hasattr(obj, 'type') and obj.type == 'FONT'

## take txt input and turn it into single-letter text objects
def string_to_letters(txt="", spacing=0.0):
    origin = bpy.context.scene.cursor_location
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

def center_letter_fx(letters_parent):
    """Move fx letter parent to simulate switching from left aligned to center aligned text"""
    # TODO allow other alignments; account for global vs parent movement
    extremes = []
    extremes[0] = letters_parent[0].location.x
    extremes[1] = letters_parent[-1].location.x + letters_parent[-1].dimensions.x
    distance = extremes[1] - extremes[0]
    letters_parent.location.x -= distance
    return letters_parent

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
    letters_parent = bpy.data.objects.new("text_fx", None)
    bpy.context.scene.objects.link(letters_parent)
    letters_parent.empty_draw_type = 'ARROWS'
    letters_parent.empty_draw_size = 1.0

    # store properties in empty
    letters_parent.text_fx.frames = frames
    letters_parent.text_fx.spacing = spacing
    letters_parent.text_fx.randomize = randomize
    letters_parent.text_fx.name = fx_name
    letters_parent.text_fx.text = txt

    # TODO use parent to align letters (without realignment they grow to right)

    # keyframe effect for each letter
    for i in range(len(letters)):
        letter = letters[i]

        # attach to parent but remove offset
        letter.parent = letters_parent
        letter.matrix_parent_inverse = letters_parent.matrix_world.inverted()

        frame = start_frame + offsets[i]
        bpy.context.scene.frame_current = frame

        keyframe_letter_fx(letter, fx)

        # TODO calc randomized values on return fx

    bpy.context.scene.frame_current = start_frame

    return letters

def find_text_fx_src():
    scene = bpy.context.scene
    obj = scene.objects.active
    if obj and hasattr(obj, "text_fx") and is_text(obj) and obj.text_fx.text:
        return obj.text_fx
    return scene.text_fx

# TODO set up props menu on empty (also shows up on letter select?)
#   - modify the existing fx
#   - update the text string
#       - accept text input directly
#       - accept named text_editor object

class TextFxProperties(bpy.types.PropertyGroup):
    text = StringProperty(name="Text", description="Text that was split into animated letters", default="")
    frames = IntProperty(name="Frames", description="Frame duration of effect on each letter", default=5)
    spacing = FloatProperty(name="Spacing", description="Distance between letters", default=0.0)
    time_offset = IntProperty(name="Timing", description="Frames to wait between each letter's animation", default=1)
    randomize = BoolProperty(name="Randomize", description="Vary the time offset for each letter's animation", default=False)
    replace = BoolProperty(name="Replace", description="Replace the current effect (otherwise added to letters)", default=False)
    effect = EnumProperty(
        name = 'Effect',
        description = 'Overall effect to give when animating the letters',
        items = [('wiggle', 'Wiggle', 'Add wiggle effect to text'),
                 ('slide_in', 'Slide-in', 'Add slide-in effect to text'),
                 ('slide_out', 'Slide-out', 'Add slide-out effect to text')]
    )

# TODO layer effects vs replace effects
#   - are created fx mutable?
#   - replace each time vs stack effects?
#   - keep record of each object's effects and props for those fx?
# effects = SomeProperty(name="Applied effects", array_length=99, default=[None for i in range(99)])
# TODO randomize effects

def create_text_fx_props(bpy_type, fx_collection=False):
    bpy_type.text_fx = bpy.props.PointerProperty(type=TextFxProperties)
    return bpy_type.text_fx

class TextFxOperator(bpy.types.Operator):
    bl_label = "Text FX Operator"
    bl_idname = "object.text_fx"
    bl_description = "Create and configure text effect"

    def execute(self, ctx):
        props_src = find_text_fx_src()

        # TODO add effect to obj vs create new obj

        #loc_deltas = [-3.0, 0.0, 0.0]
        #anim_txt("slide the text", fx_name='SLIDE_IN', fx_delta=loc_deltas, frames=4)

        rot_deltas = [0.0, 0.0, 0.5]
        anim_txt("Wiggle, yeah!", fx_name='WIGGLE', fx_delta=rot_deltas, frames=5, spacing=0.1)

        return {'FINISHED'}

class TextFxPanel(bpy.types.Panel):
    bl_label = "Text FX Panel"
    bl_idname = "object.text_fx_panel"
    bl_category = "TextFX"
    bl_context = "objectmode"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"

    def draw(self, ctx):
        props_src = find_text_fx_src()
        if props_src.id_data:
            self.layout.row().prop(props_src, "text")
            self.layout.row().prop(props_src, "effect")
            self.layout.row().prop(props_src, "frames")
            self.layout.row().prop(props_src, "spacing")
            self.layout.row().prop(props_src, "time_offset")
            row = self.layout.row()
            row.prop(props_src, "randomize")
            row.prop(props_src, "replace")
            self.layout.row().operator("object.text_fx", text="Create Text Effect")

def register():
    bpy.utils.register_class(TextFxProperties)
    bpy.utils.register_class(TextFxOperator)
    bpy.utils.register_class(TextFxPanel)
    # TODO assign class props and store locally on object instead
    create_text_fx_props(bpy.types.Object)  # text_fx empty props
    create_text_fx_props(bpy.types.Scene)   # UI props before text_fx created


def unregister():
    bpy.utils.unregister_class(TextFxPanel)
    bpy.utils.unregister_class(TextFxOperator)
    bpy.utils.register_class(TextFxProperties)

if __name__ == '__main__':
    register()
