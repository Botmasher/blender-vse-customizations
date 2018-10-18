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
        NONE = 'NONE'
        # (frames_factor, value_factor) arc
        self.map = {
            # TODO set slide, pop, other surrounding-letter-touching overshoots based on letter spacing
            WIGGLE: self.create_fx_entry(name=WIGGLE, attr='rotation_euler', kf_arc=[(0, 0), (0.5, 1), (0.5, -0.5), (0.25, 0)]),
            SLIDE_IN: self.create_fx_entry(name=SLIDE_IN, attr='location', kf_arc=[(0, 1), (1, -0.05), (0.25, 0)]),
            SLIDE_OUT: self.create_fx_entry(name=SLIDE_OUT, attr='location', kf_arc=[(0, 0), (0.25, -0.02), (1, 1)]),
            POP_IN: self.create_fx_entry(name=POP_IN, attr='scale', kf_arc=[(0, 0), (1, 1.1), (0.25, 1)]),
            POP_OUT: self.create_fx_entry(name=POP_OUT, attr='scale', kf_arc=[(0, 1.1), (0.25, 1), (1, 0)]),
            NONE: self.create_fx_entry(name=NONE, attr='', kf_arc=[])
            # TODO support layered fx
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

    def normalize_name(self, name):
        if type(name) != str: return
        return name.upper().replace(" ", "_")

    def exists(self, name):
        if not name in self.map:
            print("Unrecognized effect name {0} in text effects fx_map".format(name))
            return False
        return True

    def get_fx(self, name=''):
        normalized_name = self.normalize_name(name)
        if self.exists(normalized_name):
            return self.map[normalized_name]
        return

    def check_fx_vals(self, name, attr, kf_arc):
        if type(name) == str and type(attr) == str and type(kf_arc) == list:
            return True
        return False

    def get_attr(self, name=''):
        effect = self.get_fx(name)
        if effect:
            return effect['attr']
        return

    def create_fx_entry(self, name='', attr='', kf_arc=[]):
        if not self.check_fx_vals(name, attr, kf_arc):
            print("Unable to map text fx {0} to {1} effect arc {2}".format(name, attr, kf_arc))
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
    origin = (0, 0, 0)
    offset_x = 0
    letter_objs = []
    # create font curve object for each letter
    for l in txt:

        # letter data
        letter = bpy.data.curves.new(name="\"{0}\"-letter-{1}".format(txt, l), type="FONT")
        letter.body = l if l != " " else ""

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

def set_kf(obj, attr=None, value=None, frames_before=0, frames_after=0):
    if not hasattr(obj, attr) or not hasattr(obj, 'keyframe_insert') or value == None:
        print("Failed to set keyframe on {0} for attribute {1}".format(obj, attr))
        return
    bpy.context.scene.frame_current += frames_before
    setattr(obj, attr, value)
    kf = obj.keyframe_insert(data_path=attr)
    bpy.context.scene.frame_current += frames_after
    return kf

# construct fx
def keyframe_letter_fx (font_obj, fx={}):
    """Keyframe an effect on a letter based on an fx dict

    fx = {
        'name': '',         # like 'SLIDE'
        'attr': '',         # attribute to set on obj
        'kf_arc': [],       # (frame_mult, value_mult) pairs
        'transform': [],    # delta multiplied by value_mult and added to base value at each kf set
        'length': 0         # each letter anim's frame count - multiplied by frame_mult at each kf set
        'offset': 0         # gap between letter anims to stagger each letter's effect
    }
    """

    if not hasattr(font_obj, 'type') or font_obj.type != 'FONT' or not 'attr' in fx:
        print("Failed to keyframe letter effect on {0} - expected a font curve".format(font_obj))
        return

    if not fx or not hasattr(font_obj, fx['attr']) or 'transform' not in fx:
        print("Failed to set letter effect keyframe on {1} - unrecognized attribute or value".format(font_obj, fx['attr']))
        return

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
        kf_frames = int(round(fx['length'] * frame_mult))

        target_value = None
        # TODO recognize x/y differences for slide
        # using fx['direction'] for IN and OUT!
        #   - 'left' x factor subtracted from 0 to 1
        #   - 'right' x factor added from 0 to 1
        #   - 'top' y factor added from 0 to 1
        #   - 'bottom' y factor subtracted from 0 to 1
        print(fx['transform'])
        if 'location' in fx['attr']:
            # calc fixed loc for all location kfs
            transform = fx['transform']
            if fx['axis'] == 'y':
                new_fixed_target_all_letters = font_obj.parent.location.y + transform
                updated_target = lerp_step(origin=font_obj.matrix_world.translation.y, target=new_fixed_target_all_letters, factor=value_mult)
                target_value = (value_base[0], updated_target, value_base[2])
            elif fx['axis'] == 'x':
                new_fixed_target_all_letters = font_obj.parent.location.x + transform
                updated_target = lerp_step(origin=font_obj.matrix_world.translation.x, target=new_fixed_target_all_letters, factor=value_mult)
                target_value = (updated_target, value_base[1], value_base[2])
            elif fx['axis'] == 'z':
                new_fixed_target_all_letters = font_obj.parent.location.z + transform
                updated_target = lerp_step(origin=font_obj.matrix_world.translation.z, target=new_fixed_target_all_letters, factor=value_mult)
                target_value = (value_base[0], value_base[1], updated_target)
            else:
                # location not recognized
                print("Did not recognize location axis for text fx - failed to animate letters")
                return
        elif 'rotation' in fx['attr']:
            print('Animating rotation and using direction {0}'.format(fx['direction']))
            if fx['direction'] == 'clockwise':
                target_value = (value_base[0], value_base[1], value_base[2] - kf_value)
            else:
                target_value = (value_base[0], value_base[1], value_base[2] + kf_value)
        elif 'scale' in fx['attr']:
            target_value = (value_base[0] * kf_value, value_base[1] * kf_value, value_base[2] * kf_value)
        else:
            print("Did not recognize attr {0} on text object {1} for known text effects".format(attr, obj))

        set_kf(font_obj, attr=fx['attr'], value=target_value, frames_before=kf_frames)

    return font_obj

def lerp_step(origin=0, target=1, factor=0):
    """Step interpolate between origin and target values by a delta factor"""
    return (origin + ((target - origin) * factor))

def center_letter_fx(letters_parent):
    """Move fx letter parent to simulate switching from left aligned to center aligned text"""
    # TODO allow other alignments; account for global vs parent movement
    extremes = []
    extremes[0] = letters_parent[0].location.x
    extremes[1] = letters_parent[-1].location.x + letters_parent[-1].dimensions.x
    distance = extremes[1] - extremes[0]
    letters_parent.location.x -= distance
    return letters_parent

def parent_anim_letters(letters, fx, parent=None, start_frame=0, kf_handler=keyframe_letter_fx):
    """Attach letters to fx parent and keyframe each letter's effect based on fx data"""
    kfs = []

    for letter in letters:

        # attach to parent but remove offset
        if parent:
            letter.parent = parent
            letter.matrix_parent_inverse = parent.matrix_world.inverted()

        fx['attr'] and fx['kf_arc'] and kfs.append(keyframe_letter_fx(letter, fx))

        print("Anim frames: {0} -- Anim offset: {1} -- Current frame: {2}".format(fx['length'], fx['offset'], bpy.context.scene.frame_current))

        bpy.context.scene.frame_current += fx['offset']

    return kfs

# NOTE remove or rebuild
# or automatically reverse letters for backwards slide effects (in from left)
def reverse_fx(fx_name, fx_origin, fx_target):
    # TODO if continue to use, do custom comparisons for each effect
    # TODO support other writing system directions
    # alternatively allow this to be set as a prop
    if fx_name == 'SLIDE_OUT' and fx_origin < fx_target:
        reversed = True
    elif fx_name == 'SLIDE_IN' and fx_origin > fx_target:
        reversed = True
    else:
        reversed = False

def translate_letters(parent=None, target_location=None, default_location=(0,0,0), use_cursor=True):
    if not parent: return
    if use_cursor:
        parent.location = bpy.context.scene.cursor_location
    elif target_location:
        parent.location = target_location
    else:
        parent.location = default_location

def anim_txt(txt="", time_offset=1, fx_name='', anim_order="forwards", fx_delta=None, axis="", anim_length=5, anim_stagger=0, spacing=0.0, font=''):

    if not (txt and type(txt) is str and fx_delta != None):
        return

    if bpy.context.scene.objects.active:
        target_location = bpy.context.scene.objects.active
    else:
        target_location = bpy.context.scene.cursor_location

    # build letter objects
    letters = string_to_letters(txt, spacing=spacing, font=font)

    # build fx dict
    fx = fx_map.get_fx(fx_name)
    if not fx:
        print("Did not recognize fx_map data for text effect: {0}".format(fx))
        return
    fx['length'] = anim_length
    fx['offset'] = anim_stagger
    fx['transform'] = fx_delta
    fx['axis'] = axis

    #offsets = [i * time_offset for i in range(len(letters))]
    #randomize and random.shuffle(offsets)
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
    letters_parent.text_fx.frames = anim_length
    letters_parent.text_fx.time_offset = anim_stagger
    letters_parent.text_fx.spacing = spacing
    letters_parent.text_fx.name = fx_name
    letters_parent.text_fx.text = txt

    # letter orders: front-to-back, back-to-front, random
    letter_orders = {
        'forwards': lambda l: [*l],
        'backwards': lambda l: reversed(l),
        'random': lambda l: random.sample(l, len(l))
    }
    letters = letter_orders.get(anim_order, lambda l: l)(letters)
    # if anim_order == 'random':
    #     random.shuffle(letters)
    # elif anim_order == 'backwards':
    #     letters = reversed(letters)
    # else:
    #     letters = letters

    # keyframe effect for each letter
    parent_anim_letters(letters, fx, parent=letters_parent, start_frame=start_frame)

    # move letters to calculated target
    translate_letters(parent=letters_parent, target_location=target_location)

    bpy.context.scene.frame_current = start_frame

    return letters

# TODO letters are created in line with cursor at least along y but parent is not

# TODO allow multiple fonts
def set_font(letters_parent, font_name):
    """Update the font for each letter in a text effect object"""
    if not hasattr(letters_parent, 'children'): return
    if not font_name in bpy.data.fonts: return
    for letter in letters_parent.children:
        letter.data.font = font_name
    return font_name

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
    frames = IntProperty(name="Frames", description="Frame duration of effect on each letter", default=10)
    spacing = FloatProperty(name="Spacing", description="Distance between letters", default=0.1)
    time_offset = IntProperty(name="Timing", description="Frames to wait between each letter's animation", default=1)
    #randomize = BoolProperty(name="Randomize", description="Vary the time offset for each letter's animation", default=False)
    replace = BoolProperty(name="Replace", description="Replace the current effect (otherwise added to letters)", default=False)
    transform = FloatProperty(name="Transform", description="Added value for letter location/rotation/scale (depending on effect)", default=1.0)
    font = StringProperty(name="Font", description="Loaded font used for letters in effect", default="Bfont")
    axis = EnumProperty(
        name = "Axis",
        description = "Transform axis for directional effects",
        items = [
            ("x", "Horizontal", "Transform letters along the x axis"),
            ("y", "Vertical", "Transform letters along the y axis"),
            ("z", "Depth", "Transform letters along the z axis")
        ],
        default='x'
    )
    letters_order = EnumProperty(
        name = "Order",
        description = "Letter animation order",
        items = [
            ("forwards", "Forwards", "Animate text from first to last letter"),
            ("backwards", "Backwards", "Animate text from last to first letter"),
            ("random", "Random", "Animate text letters in random order")
        ]
    )
    clockwise = BoolProperty(name="Clockwise", description="Rotate letters clockwise", default=True)
    effect = EnumProperty(
        name = "Effect",
        description = "Overall effect to give when animating the letters",
        items = format_fx_enum()
    )

# TODO layer effects vs replace effects
#   - are created fx mutable?
#   - replace each time vs stack effects?
#   - keep record of each object's effects and props for those fx?

# TODO handler to delete all letters on fx object deleted

class TextFxOperator(bpy.types.Operator):
    bl_label = "Text FX Operator"
    bl_idname = "object.text_fx"
    bl_description = "Create and configure text effect"

    def execute(self, ctx):
        props_src = find_text_fx_src()

        # TODO add effect to obj vs create new obj
        #   - example: font changed

        modified_attr = fx_map.get_attr(name=props_src.effect)

        if modified_attr == 'location':
            axis = props_src.axis
            transform =props_src.transform
        elif 'rotation' in modified_attr:
            axis = 'clockwise' if props_src.clockwise else 'counterclockwise'
            transform = props_src.transform
        elif 'scale' in modified_attr:
            transform = 1.0
            axis = props_src.axis
        else:
            print("No location/rotation/scale attr recognized for effect - cancelling text effect")
            return {'FINISHED'}

        anim_txt(props_src.text, fx_name=props_src.effect, font=props_src.font, fx_delta=transform, axis=axis, anim_order=props_src.letters_order, anim_stagger=props_src.time_offset, anim_length=props_src.frames, spacing=props_src.spacing)

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
        location_str = 'location'
        rotation_str = 'rotation'
        scale_str = 'scale'
        modified_attr = fx_map.get_attr(name=props_src.effect)
        if props_src.id_data:
            layout = self.layout
            for prop_name in props_src.keys():
                # fall back to scene data if letters prop is undefined
                if hasattr(props_src, prop_name) and getattr(props_src, prop_name) is not None:
                    fx_data = props_src
                else:
                    fx_data = bpy.context.scene.text_fx

                if prop_name == 'font':
                    layout.prop_search(fx_data, prop_name, bpy.data, 'fonts')
                    # TODO load a new font not just select loaded font
                    #row = layout.split(percentage=0.25)
                    #row.template_ID(ctx.curve, prop_name, open="font.open", unlink="font.unlink")
                elif prop_name == 'axis':
                    location_str in modified_attr and self.layout.row().prop(fx_data, "axis")
                elif prop_name == 'clockwise':
                    rotation_str in modified_attr and self.layout.row().prop(fx_data, "clockwise")
                elif prop_name == 'transform':
                    scale_str not in modified_attr and self.layout.row().prop(fx_data, "transform")
                else:
                    layout.row().prop(fx_data, prop_name)

            layout.row().operator("object.text_fx", text="Create Text Effect")

# props container
# - scene stores data before objects created
# - empty objects store created effect

class TextFxRegister():
    def __init__(self):
        self.is_registered = False
        self.registered_types = []
        self.text_fx_attr = 'text_fx'

    def register(self, text_fx_types=[]):
        bpy.utils.register_class(TextFxProperties)
        bpy.utils.register_class(TextFxOperator)
        bpy.utils.register_class(TextFxPanel)
        text_fx_types and self.create_text_fx_props(bl_types=text_fx_types, PropsClass=TextFxProperties)
        self.is_registered = True

    def unregister(self):
        self.remove_text_fx_props()
        bpy.utils.unregister_class(TextFxOperator)
        bpy.utils.unregister_class(TextFxPanel)
        bpy.utils.register_class(TextFxProperties)
        self.is_registered = False

    def create_text_fx_props(self, bl_types=[], PropsClass=None):
        if not bl_types or not PropsClass:
            return []
        text_fx_attrs = []
        for bl_type in bl_types:
            if bl_type not in self.registered_types and hasattr(bpy.types, bl_type):
                bpy_types_object = getattr(bpy.types, bl_type)
                bpy_types_object.text_fx = bpy.props.PointerProperty(type=PropsClass)
                text_fx_attrs.append(bpy_types_object.text_fx)
                self.registered_types.append(bl_type)
        return text_fx_attrs

    def remove_text_fx_props(self):
        del_types = []
        for bl_type in self.registered_types:
            if hasattr(bpy.types, bl_type):
                bpy_type = getattr(bpy.types, bl_type)
                if hasattr(bpy_type, self.text_fx_attr):
                    bl_type_text_fx = getattr(getattr(bpy.types, bl_type), self.text_fx_attr)
                    try:
                        del bl_type_text_fx
                    except:
                        print("Failed to delete attribute {0}".format(bl_type_text_fx))
                else:
                    continue
            else:
                continue
        return

registration = TextFxRegister()
#__name__ == '__main__' and registration.register(text_fx_types=['Object', 'Scene'])
__name__ == '__main__' and registration.unregister()
