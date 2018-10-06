import bpy
import random
from bpy.props import *

## Text FX data

class Singleton:
    instance = None
    def __new__(singleton):
        return super().__new__(singleton) if not singleton.instance else singleton.instance

class TextEffectsMap(Singleton):
    def __init__(self):
        WIGGLE = 'WIGGLE'
        SLIDE_IN = 'SLIDE_IN'
        SLIDE_OUT = 'SLIDE_OUT'
        POP_IN = 'POP_IN'
        POP_OUT= 'POP_OUT'
        # 1 target, 0 base, o overshoot
        self.map = {
            WIGGLE: self.create_fx_entry(name=WIGGLE, attr='rotation_euler', kf_arc=[(0, 0), (0.5, 1), (0.5, -0.5), (0.25, 0)]),
            SLIDE_IN: self.create_fx_entry(name=SLIDE_IN, attr='location', kf_arc=[(0, 1), (1, 1), (0.25, 0)]),
            SLIDE_OUT: self.create_fx_entry(name=SLIDE_OUT, attr='location', kf_arc=[(0, 0), (1, 1.1), (0.25, 1)]),
            POP_IN: self.create_fx_entry(name=POP_IN, attr='scale', kf_arc=[(0, 0), (1, 1.1), (0.25, 1)]),
            POP_OUT: self.create_fx_entry(name=POP_OUT, attr='scale', kf_arc=[(0, 1.1), (0.25, 1), (1, 0)])
            # TODO support layered fx
            #'WOBBLE': ['rotation_euler', 'location'],
            #'SCALE_UP': [], ...
            #'SCALE_DOWN': [], ...
        }

    def set_kf_arc(self, name, kf_arc):
        if type(kf_arc) != list:
            print("Failed to assign kf_arc to text_fx {0} - expected list".format(name))
            return
        if name in self.map:
            self.map[name]['kf_arc'] = kf_arc
            return True
        return False

    # TODO edit kf_arc list values for given effect

    def get_map(self):
        return self.map

    def keys(self):
        return self.map.keys()

    def values(self):
        return self.map.values()

    def get_fx(self, name=''):
        if not name in self.map:
            print("Text effect fx_map - unrecognized effect name {0}".format(name))
            return
        return self.map[name]

    def check_fx_vals(self, name, attr, kf_arc):
        if type(name) == str and type(attr) == str and type(kf_arc) == list:
            return True
        return False

    def create_fx_entry(self, name='', attr='', kf_arc=[]):
        if not self.check_fx_vals(name, attr, kf_arc):
            print("Unable to map text fx {0} to effect arc {1}".format(name, attr, kf_arc))
            return
        return {
            'name': name,
            'attr': attr,
            'kf_arc': kf_arc
        }

    def set_fx(self, name='', attr='', kf_arc=[(0, 0), (1, 1)]):
        if not self.check_fx_vals(name, attr, kf_arc):
            return
        self.map[name] = self.create_fx_entry(name=name, attr=attr, kf_arc=kf_arc)
        return self.map[name]

fx_map = TextEffectsMap()


## Text FX calcs

def is_text(obj):
    return obj and hasattr(obj, 'type') and obj.type == 'FONT'

## take txt input and turn it into single-letter text objects
def string_to_letters(txt="", spacing=0.0, font=''):
    origin = bpy.context.scene.cursor_location
    offset_x = 0
    letter_objs = []
    # create font curve object for each letter
    for l in txt:

        # letter data
        letter = bpy.data.curves.new(name="\"{0}\"-letter-{1}".format(txt, l), type="FONT")
        letter.body = l if l != " " else "a"

        # assign selected font
        if font and font in bpy.data.fonts:
            letter.font = bpy.data.fonts[font]

        # letter object
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
def keyframe_letter_fx (font_obj, fx={}, frames=0):
    """Keyframe an effect on a letter based on an fx dict

    fx = {
        'name': '',         # like 'SLIDE'
        'attr': '',         # attribute to set on obj
        'kf_arc': [],       # (frame_mult, value_mult) pairs
        'transform': [],    # delta multiplied by value_mult and added to base value at each kf set
        'length': 0         # frame count multiplied by frame_mult at each kf set
    }
    """

    if not hasattr(font_obj, 'type') or font_obj.type != 'FONT' or not 'attr' in fx:
        print("Failed to keyframe letter effect on {0} - expected a font curve".format(font_obj))
        return

    if not fx or not hasattr(font_obj, fx['attr']) or 'transform' in fx:
        print("Failed to set letter effect keyframe on {1} - unrecognized attribute or value".format(font_obj, f['attr']))
        return

    def set_kf(obj, attr=None, value=None, frame_skip=0):
        if not hasattr(obj, attr) or not hasattr(obj, 'keyframe_insert') or not value:
            print("Failed to set keyframe on {0} for attribute {1}".format(obj, attr))
            return
        print(value)
        setattr(obj, attr, value)
        kf = obj.keyframe_insert(data_path=attr)
        bpy.context.scene.frame_current += frame_skip
        return kf

    value_base = None
    if 'location' in fx['attr']:
        value_base = font_obj.location[:]
    elif 'rotation' in fx['attr']:
        value_base = font_obj.rotation_euler[:]
    elif 'scale' in fx['attr']:
        value_base = font_obj.scale[:]
    else:
        print("Did not recognize attr {0} on text object {1} for known text effects".format(attr, obj))

    # keyframe along effect arc
    print("Keyframing along {0} effect arc for letter {1}".format(fx['name'], font_obj))
    for kf_mults in fx['kf_arc']:
        # multiply user settings by effect factors to get each kf
        frame_mult = kf_mults[0]
        value_mult = kf_mults[1]
        kf_value = value_mult * fx['transform']
        kf_frames = frames * frame_mult

        target_value = None
        # TODO recognize x/y differences for slide
        if 'location' in fx['attr']:
            target_value = (value_base.x + kf_value, value_base.y, value_base.z)
        # TODO recognize clockwise/counterclockwise for rotation
        elif 'rotation' in fx['attr']:
            value_base = (value_base.x, value_base.y, value_base.z + kf_value)
        elif 'scale' in fx['attr']:
            value_base = (value_base.x * kf_value, value_base.y * kf_value, value_base.z * kf_value)
        else:
            print("Did not recognize attr {0} on text object {1} for known text effects".format(attr, obj))

        set_kf(font_obj, attr=fx['attr'], value=kf_value, frame_skip=kf_frames)

    return font_obj

def center_letter_fx(letters_parent):
    """Move fx letter parent to simulate switching from left aligned to center aligned text"""
    # TODO allow other alignments; account for global vs parent movement
    extremes = []
    extremes[0] = letters_parent[0].location.x
    extremes[1] = letters_parent[-1].location.x + letters_parent[-1].dimensions.x
    distance = extremes[1] - extremes[0]
    letters_parent.location.x -= distance
    return letters_parent

def anim_txt(txt="", time_offset=1, fx_name='', fx_delta=None, frames=0, spacing=0.0, font='', randomize=False):

    if not (txt and type(txt) is str and fx_delta != None):
        return

    letters = string_to_letters(txt, spacing=spacing, font=font)

    # build fx dict
    fx = fx_map.get_fx(fx_name)

    if not fx:
        print("Did not recognize fx_map data for text effect: {0}".format(fx))
        return

    fx['length'] = frames
    fx['transform'] = fx_delta

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

        keyframe_letter_fx(letter, fx, frames)

        # TODO calc randomized values on return fx

    bpy.context.scene.frame_current = start_frame

    return letters

def find_text_fx_src():
    scene = bpy.context.scene
    obj = scene.objects.active
    if obj and hasattr(obj, "text_fx") and is_text(obj) and obj.text_fx.text:
        return obj.text_fx
    return scene.text_fx


## Text FX interface

# TODO set up props menu on empty (also shows up on letter select?)
#   - modify the existing fx
#   - update the text string
#       - accept text input directly
#       - accept named text_editor object

def format_fx_enum():
    fx_items = []
    fx_names_alphasort = sorted(fx_map.keys())
    for k in fx_names_alphasort:
        item_name = "{0}{1}".format(k[0].upper(), k[1:].lower().replace("_", " "))
        item_description = "Add {0} effect to text".format(k.lower())
        fx_items.append((k, item_name, item_description))
    return fx_items

class TextFxProperties(bpy.types.PropertyGroup):
    text = StringProperty(name="Text", description="Text that was split into animated letters", default="")
    frames = IntProperty(name="Frames", description="Frame duration of effect on each letter", default=5)
    spacing = FloatProperty(name="Spacing", description="Distance between letters", default=0.1)
    time_offset = IntProperty(name="Timing", description="Frames to wait between each letter's animation", default=1)
    randomize = BoolProperty(name="Randomize", description="Vary the time offset for each letter's animation", default=False)
    replace = BoolProperty(name="Replace", description="Replace the current effect (otherwise added to letters)", default=False)
    transform = FloatProperty(name="Transform", description="Added value for letter location/rotation/scale (depending on effect)", default=1.0)
    font = StringProperty(name="Font", description="Loaded font used for letters in effect", default="Bfont")
    direction = EnumProperty(
        name = "Direction",
        description = "Transform direction for directional effects",
        items = [
            ("top", "Top", "Transform letters to or from the top"),
            ("bottom", "Bottom", "Transform letters to or from the bottom"),
            ("left", "Left", "Transform letters to or from the left side"),
            ("right", "Right", "Transform letters to or from the right side")
        ]
    )
    effect = EnumProperty(
        name = "Effect",
        description = "Overall effect to give when animating the letters",
        items = format_fx_enum()
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

        anim_txt(props_src.text, fx_name=props_src.effect, font=props_src.font, fx_delta=props_src.transform, frames=props_src.frames, spacing=props_src.spacing)

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
            self.layout.row().prop(props_src, "transform")
            self.layout.row().prop(props_src, "frames")
            self.layout.row().prop(props_src, "spacing")
            self.layout.row().prop(props_src, "time_offset")
            self.layout.prop_search(props_src, "font", bpy.data, 'fonts')
            self.layout.row().prop(props_src, "direction")
            row = self.layout.row()
            row.prop(props_src, "randomize")
            row.prop(props_src, "replace")
            self.layout.row().operator("object.text_fx", text="Create Text Effect")

    def update_scene_fonts(self):
        print(bpy.context.scene.fonts)
        for font in bpy.data.fonts:
            if font.name not in bpy.context.scene.fonts:
                bpy.context.scene.fonts.add(font.name)
        return bpy.context.scene.fonts

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
