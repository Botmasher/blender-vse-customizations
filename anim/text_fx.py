import bpy
import random
from bpy.props import *
from collections import deque

## Text FX
## Blender Python script by Joshua R (Botmasher)
##
## Create letter-by-letter text effects
##
## NOTE: clarify semantics of "effects" / "fx" (used interchangeably)
##  - "effects" ambiguity: fx data vs fx'd letters vs fx letters parents
##
## Intended use:
##  - place a new text effect in the scene
##      - each effect has separate letter objects attached to an empty parent
##      - empty parent stores the fx props data
##  - modify (or simulate modification of) an existing text effect
##      - select text fx letters parent to retrieve data and change through UI
##
## Structure:
##  - tool ui:  text_fx props, panel, operator (including registration and prop assignment)
##  - fx data:  stored and accessed with TextEffectsMap
##  - fx logic: apply effects to create fx letters & parent
##

# TODO define axes on effects map instead of props
#   - changing axis may change fx, e.g. slide X/Y vs perspective Z
#   - allow action control in fx map data (rotate: wiggle Z vs turn Y)

## Effects data

class Singleton:
    instance = None
    def __new__(singleton):
        return super().__new__(singleton) if not singleton.instance else singleton.instance

class TextEffectsMap(Singleton):
    map = {}
    def __init__(self, default_fx=True):
        # TODO set slide, pop, other surrounding-letter-touching overshoots based on letter spacing
        if default_fx:
            self.create_fx(name='WIGGLE', attr='rotation_euler', kf_arc=[(0, 0), (0.5, 1), (0.5, -0.5), (0.25, 0)], axis=['z'])
            self.create_fx(name='PUSH_IN', attr='location', kf_arc=[(0, 1), (1, -0.05), (0.25, 0)], axis=['x'])
            self.create_fx(name='PUSH_OUT', attr='location', kf_arc=[(0, 0), (0.25, -0.02), (1, 1)], axis=['x'])
            self.create_fx(name='FALL_IN', attr='location', kf_arc=[(0, 1), (1, -0.05), (0.25, 0)], axis=['y'])
            self.create_fx(name='FALL_OUT', attr='location', kf_arc=[(0, 0), (0.25, -0.02), (1, 1)], axis=['y'])
            self.create_fx(name='POP_IN', attr='scale', kf_arc=[(0, 0), (1, 1.1), (0.25, 1)], axis=['x', 'y', 'z'])
            self.create_fx(name='POP_OUT', attr='scale', kf_arc=[(0, 1.1), (0.25, 1), (1, 0)], axis=['x', 'y', 'z'])
            self.create_fx(name='NONE', attr='', kf_arc=[], axis=[])

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

    def get_fx_entry(self, name='', normalize=True):
        if normalize:
            name = self.normalize_name(name)
        if self.exists(name):
            return self.map[name]

    def get_compound_fx(self, name=''):
        normalized_name = self.normalize_name(name)
        effects = []
        # no known effect
        if not self.exists(normalized_name):
            return effects
        # known compound effect
        if type(self.map[normalized_name]) is list:
            try:
                effects = [self.map[effect_name] for effect_name in self.map[normalize_name]]
                return effects
            except:
                print("Error building compound fx list for effect {0}".format(normalized_name))
        # known individual effect
        else:
            effects.append(self.get_fx_entry(normalized_name, normalize=False))
            return effects

    def check_fx_vals(self, name, attr, kf_arc, axis):
        if type(name) == str and type(attr) == str and type(kf_arc) == list and type(axis) == list:
            return True
        return False

    def get_attrs(self, name=''):
        effects = self.get_compound_fx(name)
        fx_attrs = []
        def simplify_transform_attr(attr_name):
            if 'location' in attr_name:
                return 'location'
            elif 'rotation' in attr_name:
                return 'rotation'
            elif 'scale' in attr_name:
                return 'scale'
            else:
                return ''
        if effects:
            fx_attrs = {simplify_transform_attr(effect['attr']) for effect in effects}
        return list(fx_attrs)

    def create_compound_fx(self, name='', effects=[]):
        known_fx = []
        if name and effects:
            for effect in effects:
                if type(effect) is str and self.exists(effect):
                    known_fx.append(effect)
            self.map[name] = effects

    def add_compound_fx(self, effect, name=''):
        if self.exists(name) and self.exists(effect) and type(self.map[name]) is list:
            self.map[name].append(effect)

    def remove_compound_fx(self, effect, name=''):
        if self.exists(name) and self.exists(effect) and type(self.map[name]) is list and effect in self.map[name]:
            self.map[name].remove(effect)

    def create_fx(self, name='', attr='', kf_arc=[], axis=[]):
        if not self.check_fx_vals(name, attr, kf_arc, axis):
            print("Unable to map text fx {0} to {1} effect arc {2}".format(name, attr, kf_arc))
            return
        self.map[name] = {
            'name': name,
            'attr': attr,
            'kf_arc': kf_arc,
            'axis': axis
        }

    def set_fx(self, name='', attr='', kf_arc=[(0, 0), (1, 1)], axis=['x', 'y', 'z']):
        if not self.check_fx_vals(name, attr, kf_arc, axis):
            return
        self.map[name] = self.create_fx(name=name, attr=attr, kf_arc=kf_arc, axis=axis)
        return self.map[name]


## Effects application

class TextEffectsMaker:

    def __init__(self, fx_map):
        self.set_fx_map(fx_map)

    def set_fx_map(self, fx_map):
        """Update the TextEffectsMap instance used for effects data"""
        if type(fx_map) is not TextEffectsMap:
            return False
        self.fx_map = fx_map
        return True

    def get_fx_map(self):
        """Update the TextEffectsMap instance used for effects data"""
        return self.fx_map

    def is_text(self, obj):
        return obj and hasattr(obj, 'type') and obj.type == 'FONT'

    def create_letter(self, text, letter="", font=None):
        """Make letter data, letter object and link letter to scene"""
        if type(letter) is not str or type(text) is not str:
            return
        # letter data
        name = "\"{0}\"-letter-{1}".format(text, letter)
        letter_data = bpy.data.curves.new(name=name, type='FONT')
        letter_data.body = letter if letter != " " else ""
        # assign selected font
        if font and font in bpy.data.fonts:
            letter_data.font = bpy.data.fonts[font]
        # letter object
        letter_obj = bpy.data.objects.new(letter_data.name, letter_data)
        bpy.context.scene.objects.link(letter_obj)
        return letter_obj

    ## take txt input and turn it into single-letter text objects
    def string_to_letters(self, txt="", spacing=0.0, font=''):
        """Take a string and create an array of letter objects"""
        origin = (0, 0, 0)
        offset_x = 0
        letter_objs = []

        # create font curve object for each letter
        for l in txt:

            # letter data
            letter_obj = self.create_letter(txt, letter=l, font=font)

            # set offset and base spacing on letter width
            letter_obj.location = [offset_x, *origin[1:]]
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

    def set_kf(self, obj, attr=None, value=None, frames_before=0, frames_after=0):
        """Keyframe an object's attribute to the given value, moving playhead
        frames_before first and frames_after later"""
        if not hasattr(obj, attr) or not hasattr(obj, 'keyframe_insert') or value == None:
            print("Failed to set keyframe on {0} for attribute {1}".format(obj, attr))
            return
        bpy.context.scene.frame_current += frames_before
        setattr(obj, attr, value)
        kf = obj.keyframe_insert(data_path=attr)
        bpy.context.scene.frame_current += frames_after
        return kf

    # construct fx
    def keyframe_letter_fx (self, font_obj, effect={}):
        """Keyframe an effect on a letter based on an fx dict

        fx = {
            'name': '',         # like 'SLIDE'
            'attr': '',         # attribute to set on obj (location, rotation, scale)
            'kf_arc': [],       # (frame_mult, value_mult) pairs
            'transform': {},    # location, rotation, scale magnitudes multiplied by value_mult and added to base value at each kf set
            'axis': [],         # direcitonal axes along which to apply transforms
            'length': 0,        # each letter anim's frame count - multiplied by frame_mult at each kf set
            'offset': 0         # gap between letter anims to stagger each letter's effect
        }
        """
        # TODO update fx map above to reflect passed-in effect from effects list, plus sibling transforms, axis

        if not hasattr(font_obj, 'type') or not hasattr(font_obj, 'parent') or font_obj.type != 'FONT' or not effect or not 'attr' in effect:
            print("Failed to keyframe letter effect on {0} - expected a font curve parented to a letter fx empty".format(font_obj))
            return

        if not hasattr(font_obj, effect['attr']):
            print("Failed to set letter effect keyframe on {1} - unrecognized attribute or value".format(font_obj, effect['attr']))
            return

        value_base = None
        transform_magnitude = None
        axis = [dir.lower() for dir in effect['axis']]
        if 'location' in effect['attr']:
            value_base = font_obj.location[:]
            transform_magnitude = effect['transforms']['location']
        elif 'rotation' in effect['attr']:
            value_base = font_obj.rotation_euler[:]
            transform_magnitude = effect['transforms']['rotation']
        elif 'scale' in effect['attr']:
            value_base = font_obj.scale[:]
            transform_magnitude = effect['transforms']['scale']
        else:
            print("Did not recognize attr {0} on text object {1} for known text effects".format(attr, obj))
            return

        # keyframe along effect arc
        print("Keyframing along {0} effect arc for letter {1}".format(effect['name'], font_obj))

        for kf_mults in effect['kf_arc']:
            # multiply user settings by effect factors to get each kf
            frame_mult = kf_mults[0]
            value_mult = kf_mults[1]
            kf_value = value_mult * transform_magnitude
            kf_frames = int(round(effect['length'] * frame_mult))

            target_transform = {'x': value_base[0], 'y': value_base[1], 'z': value_base[2]}

            if 'location' in effect['attr']:
                # calc fixed loc for all location kfs
                # TODO recalculate since all axes passed in, but some add 0.0
                for dir in axis:
                    try:
                        # transform magnitude for this direction relative to parent
                        new_fixed_target = getattr(font_obj.parent.location, dir) + kf_value
                        # global world object origin for this direction
                        world_origin = getattr(font_obj.matrix_world.translation, dir)
                        #  step to new value for this direction
                        dir_value = self.lerp_step(origin=world_origin, target=new_fixed_target, factor=value_mult)
                        # store keyframe values for all axes
                        target_transform = {k: v if k != dir else dir_value for k, v in target_transform.items()}
                    except:
                        # location not recognized
                        print("Did not recognize {0} axis '{1}' for text fx - failed to animate letters".format(effect['attr'], dir))
                        return
            elif 'rotation' in effect['attr']:
                # TODO double check clockwise/counterclockwise (plus vs minus)
                for dir in axis:
                    try:
                        dir_value = target_transform[dir] - kf_value
                        target_transform = {k: v if k != dir else dir_value for k, v in target_transform.items()}
                    except:
                        print("Did not recognize {0} axis '{1}' for text fx - failed to animate letters".format(effect['attr'], dir))
                        return
            elif 'scale' in effect['attr']:
                for dir in axis:
                    try:
                        dir_value = target_transform[dir] * kf_value
                        target_transform = {k: v if k != dir else dir_value for k, v in target_transform.items()}
                    except:
                        print("Did not recognize {0} axis '{1}' for text fx - failed to animate letters".format(effect['attr'], dir))
                        return
            else:
                print("Did not recognize attr {0} on text object {1} for known text effects".format(attr, obj))

            target_value = [target_transform['x'], target_transform['y'], target_transform['z']]
            self.set_kf(font_obj, attr=effect['attr'], value=target_value, frames_before=kf_frames)

        return font_obj

    def lerp_step(self, origin=0, target=1, factor=0):
        """Step interpolate between origin and target values by a delta factor"""
        return (origin + ((target - origin) * factor))

    def center_letter_fx(self, letters_parent):
        """Move fx letter parent to simulate switching from left aligned to center aligned text"""
        # TODO allow other alignments; account for global vs parent movement
        extremes = []
        extremes[0] = letters_parent[0].location.x
        extremes[1] = letters_parent[-1].location.x + letters_parent[-1].dimensions.x
        distance = extremes[1] - extremes[0]
        letters_parent.location.x -= distance
        return letters_parent

    def parent_anim_letters(self, letters, fx, parent=None, start_frame=0, kf_handler=keyframe_letter_fx):
        """Attach letters to fx parent and keyframe each letter's effect based on fx data"""
        kfs = []

        for effect in fx['effects']:

            effect['length'] = fx['length']
            effect['transforms'] = fx['transforms']

            for letter in letters:

                # attach to parent but remove offset
                if not parent:
                    print("Expected text fx letter parent for '{0}' but parent is {1}".format(letter, parent))
                    return
                letter.parent = parent
                letter.matrix_parent_inverse = parent.matrix_world.inverted()

                effect['attr'] and effect['kf_arc'] and kfs.append(self.keyframe_letter_fx(letter, effect))

                #print("Anim frames: {0} -- Anim offset: {1} -- Current frame: {2}".format(fx['length'], fx['offset'], bpy.context.scene.frame_current))

                bpy.context.scene.frame_current += fx['offset']

        return kfs

    def set_parent_location(self, obj=None, target=None, default=(0,0,0), use_cursor=True):
        """Set the parent"""
        if not obj: return
        if use_cursor:
            obj.parent.location = bpy.context.scene.cursor_location
        elif target:
            obj.parent.location = target
        else:
            obj.parent.location = default

    def is_transform_map(self, d, transform_keys=['location', 'rotation', 'scale']):
        """Check if map contains location, rotation, scale keys with transform values"""
        value_types = (float, int)
        if len(d.keys()) != len(transform_keys):
            return False
        for transform in transform_keys:
            if transform not in d:
                return False
            if type(d[transform]) not in value_types:
                return False
        return True

    def anim_txt(self, txt="", time_offset=1, fx_name='', anim_order="forwards", fx_deltas={}, anim_length=5, anim_stagger=0, spacing=0.0, font=''):
        # TODO use clockwise to set rot +- for transformed x,y,z
        if not (txt and type(txt) is str and fx_deltas != None):
            return

        if bpy.context.scene.objects.active:
            target_location = bpy.context.scene.objects.active
        else:
            target_location = bpy.context.scene.cursor_location

        # build letter objects
        letters = self.string_to_letters(txt, spacing=spacing, font=font)

        # check format of axis and delta maps
        if not self.is_transform_map(fx_deltas):
            return

        # build fx dict
        fx = {}
        effects = fx_map.get_compound_fx(fx_name)
        if not effects:
            print("Failed to find fx_map data for text effect: {0}".format(fx_name))
            return
        fx['name'] = fx_name
        fx['effects'] = effects
        fx['length'] = anim_length
        fx['offset'] = anim_stagger
        fx['transforms'] = fx_deltas    # magnitude only; axis set in effects map

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
        self.parent_anim_letters(letters, fx, parent=letters_parent, start_frame=start_frame)

        # move letters to calculated target
        letters and self.set_parent_location(obj=letters[0], target=target_location)

        bpy.context.scene.frame_current = start_frame

        return letters

    # TODO letters are created in line with cursor at least along y but parent is not

    def set_font(self, letters_parent, font_name):
        """Update the font for each letter in a text effect object"""
        if not hasattr(letters_parent, 'children'): return
        if not font_name in bpy.data.fonts: return
        for letter in letters_parent.children:
            letter.data.font = font_name
        return font_name

    def find_text_fx_src(self):
        """Return the active text fx object or scene if there is none"""
        scene = bpy.context.scene
        obj = scene.objects.active
        if obj and hasattr(obj, "text_fx") and self.is_text(obj) and obj.text_fx.text:
            return obj
        return scene


## Effects interface

# text fx instances
fx_map = TextEffectsMap()       # data
#fx_map = TextEffectsMap()       # singleton test
fx = TextEffectsMaker(fx_map)   # logic

# TODO set up props menu on empty (also shows up on letter select?)
#   - modify the existing fx
#   - update the text string
#       - accept text input directly
#       - accept named text_editor object

def format_fx_enum():
    fx_items = deque([])
    fx_names_alphasort = sorted(fx_map.keys(), reverse=True)
    for k in fx_names_alphasort:
        item_name = "{0}{1}".format(k[0].upper(), k[1:].lower().replace("_", " "))
        if k.lower() == 'none':
            item_description = "Add no effect to text"
            fx_items.appendleft((k, item_name, item_description))
            continue
        item_description = "Add {0} effect to text".format(k.lower())
        fx_items.append((k, item_name, item_description))
    fx_items.reverse()
    return list(fx_items)

# UI checklist for prop names
# add, remove, reorder props to determine UI visibility
text_fx_prop_names = [
    'text',
    'font',
    'effect',
    'letters_order',
    'frames',
    'spacing',
    'time_offset',
    #'replace',
    'transform_location',
    #'axis_location',
    'transform_rotation',
    #'axis_rotation',
    'transform_scale',
    'clockwise'
]

class TextFxProperties(bpy.types.PropertyGroup):
    text = StringProperty(name="Text", description="Text that was split into animated letters", default="")
    font = StringProperty(name="Font", description="Loaded font used for letters in effect", default="Bfont")
    effect = EnumProperty(
        name = "Effect",
        description = "Overall effect to give when animating the letters",
        items = format_fx_enum()
    )
    letters_order = EnumProperty(
        name = "Order",
        description = "Letter animation order",
        items = [
            ("random", "Random", "Animate text letters in random order"),
            ("backwards", "Backwards", "Animate text from last to first letter"),
            ("forwards", "Forwards", "Animate text from first to last letter")
        ]
    )
    frames = IntProperty(name="Frames", description="Frame duration of effect on each letter", default=10)
    spacing = FloatProperty(name="Spacing", description="Distance between letters", default=0.1)
    time_offset = IntProperty(name="Timing", description="Frames to wait between each letter's animation", default=1)
    replace = BoolProperty(name="Replace", description="Replace the current effect (otherwise added to letters)", default=False)
    transform_location = FloatProperty(name="Location change", description="Added value for letter location effect", default=1.0)
    transform_rotation = FloatProperty(name="Rotation change", description="Added value for letter rotation effect", default=1.0)
    transform_scale = FloatProperty(name="Scale change", description="Added value for letter scale effect", default=1.0)
    axis_location = EnumProperty(
        name = "Axis",
        description = "Transform axis for location effects",
        items = [
            ("z", "Z", "Move letters along the z axis"),
            ("y", "Y", "Move letters along the y axis"),
            ("x", "X", "Move letters along the x axis")
        ],
        default='x'
    )
    axis_rotation = EnumProperty(
        name = "Axis",
        description = "Transform axis for rotation effects",
        items = [
            ("z", "Z", "Rotate letters along the z axis"),
            ("y", "Y", "Rotate letters along the y axis"),
            ("x", "X", "Rotate letters along the x axis")
        ],
        default='z'
    )
    clockwise = BoolProperty(name="Clockwise", description="Rotate letters clockwise", default=True)

# TODO layer effects vs replace effects
#   - are created fx mutable?
#   - replace each time vs stack effects?
#   - keep record of each object's effects and props for those fx?

# TODO handler to delete all letters on fx object deleted

class TextFxOperator(bpy.types.Operator):
    bl_label = "Text FX"
    bl_idname = "object.text_fx"
    bl_description = "Create and configure text effect"

    def execute(self, ctx):
        props_src = fx.find_text_fx_src()
        text_fx = props_src.text_fx

        # TODO add effect to obj vs create new obj
        #   - example: font changed

        # TODO list all modified attrs for compound fx
        modified_attrs = fx_map.get_attrs(name=text_fx.effect)

        # compile map of all transform magnitude deltas
        # NOTE x,y,z now defined in effects map - originally set here
        transforms = {
            'location': text_fx.transform_location,
            'rotation': text_fx.transform_rotation,
            'scale': text_fx.transform_scale
        }
        if not text_fx.clockwise:
            transforms['rotation'] = -transforms['rotation']

        #for attr in effects_attrs:
        #   if not hasattr(obj, attr):
        #       print("No location/rotation/scale attr recognized for effect - cancelling text effect")
        #       return {'FINISHED'}

        fx.anim_txt(text_fx.text, fx_name=text_fx.effect, font=text_fx.font, fx_deltas=transforms, anim_order=text_fx.letters_order, anim_stagger=text_fx.time_offset, anim_length=text_fx.frames, spacing=text_fx.spacing)

        return {'FINISHED'}

class TextFxPanel(bpy.types.Panel):
    bl_label = "Text FX Tools"
    bl_idname = "object.text_fx_panel"
    bl_category = "TextFX"
    bl_context = "objectmode"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"

    def draw(self, ctx):
        props_src = fx.find_text_fx_src()
        modified_attrs = fx_map.get_attrs(name=props_src.text_fx.effect)

        if props_src:
            layout = self.layout
            text_fx = props_src.text_fx

            for prop_name in text_fx_prop_names:
                # fall back to scene data if letters prop is undefined
                if hasattr(text_fx, prop_name) and getattr(text_fx, prop_name) is not None:
                    fx_data = text_fx
                else:
                    fx_data = bpy.context.scene.text_fx

                if prop_name == 'font':
                    layout.prop_search(fx_data, prop_name, bpy.data, 'fonts')
                    # TODO load a new font not just select loaded font
                    #row = layout.split(percentage=0.25)
                    #row.template_ID(ctx.curve, prop_name, open="font.open", unlink="font.unlink")
                elif prop_name in ['transform_location', 'axis_location']:
                    'location' in modified_attrs and self.layout.row().prop(fx_data, prop_name)
                elif prop_name in ['transform_rotation', 'axis_rotation', 'clockwise']:
                    'rotation' in modified_attrs and self.layout.row().prop(fx_data, prop_name)
                elif prop_name == 'transform_scale':
                    'scale' in modified_attrs and self.layout.row().prop(fx_data, prop_name)
                else:
                    layout.row().prop(fx_data, prop_name)

            layout.row().operator("object.text_fx", text="Create Text Effect")

# props container
# - scene stores data before objects created
# - empty objects store created effect

def create_text_fx_props():
    bpy.types.Object.text_fx = bpy.props.PointerProperty(type=TextFxProperties)
    bpy.types.Scene.text_fx = bpy.props.PointerProperty(type=TextFxProperties)
    return

def remove_text_fx_props():
    try:
        del bpy.types.Object.text_fx
    except:
        print("Failed to delete text_fx props from bpy.types.Object")
    try:
        del bpy.types.Scene.text_fx
    except:
        print("Failed to delete text_fx props from bpy.types.Scene")
    return

def register():
    remove_text_fx_props()
    bpy.utils.register_class(TextFxProperties)
    bpy.utils.register_class(TextFxOperator)
    bpy.utils.register_class(TextFxPanel)
    create_text_fx_props()

def unregister():
    remove_text_fx_props()
    bpy.utils.unregister_class(bpy.types.TextFxProperties)
    bpy.utils.unregister_class(bpy.types.OBJECT_OT_text_fx)
    bpy.utils.unregister_class(TextFxPanel)

__name__ == '__main__' and register()
#__name__ == '__main__' and unregister()
