import bpy

# audio input drives shape key value
# a Blender Python script by Josh (github.com/Botmasher)
#
#   0. open this script in the text editor
#   1. select object in 3d view
#   2. add path to your audio file below
#   3. name your shape key below
#   4. choose a scene frame to start playing your audio file below
#   5. click "Run script" with this script open in the text editor
#

# audio to use and when to start playing
sound_file_path = '/Users/username/test.wav'   # path to your file
custom_key_name = 'audio-shape-key'            # rename your shape key
starting_frame = 0                             # scene frame to start playback

class Context_Manager:
    text = "TEXT_EDITOR"
    graph = "GRAPH_EDITOR"
    vse = "SEQUENCE_EDITOR"
    def __init__ (self):
        return self
    def get (self):
    ''' Read the current context
    '''
        return bpy.context.area.type
    def set (self, context):
    ''' Change the current context
    '''
        old_context = bpy.context.area.type
        bpy.context.area.type = context
        return (old_context, context)
    def object (self):
    ''' Read the active object
    '''
        return bpy.context.object

class Audio_Shape_Key:
    def __init__ (self, selected_object, key_name, value=0.0):
    ''' Create and name a shape key in selected object's data.
    '''
        # add and store shape key
        if selected_object.data.shape_keys == None:
            selected_object.shape_key_add()
        shape_key = selected_object.shape_key_add()
        shape_key.name = key_name
        self.key = shape_key
        self.key.value = value
        # toggle when bake sound to key
        self.sound_added = False
        # create dictionary for keyframes
        self.keyframes = {}
        # object this key belongs to
        self.object = selected_object
    def set_keyframe (self, frame, value):
    ''' Keyframe shapekey and store frame:value pair in dictionary
    '''
        bpy.context.scene.frame_current = frame
        self.key.keyframe_insert ("value", frame = frame)
        self.key.value = value
        self.key.keyframe_insert ("value", frame = frame)
        self.keyframes[frame] = value
    def get_keyframe_value (self, frame):
    ''' Return the shape key's value at a specific frame
    '''
        return self.keyframes [frame]
    def get_keyframe_curve (self):
    ''' Return the shape key's fcurve
    '''
        # return the keyframe fcurve at this frame
        if self.object.data.animation_data.action is None:
            return None
        for fcurve in self.object.data.animation_data.action.fcurves:
            # the fcurve's name is the shape key path plus .value
            if (self.key.name+"\"") in fcurve.data_path:
                return fcurve
        return None
    def add_sound_to_keyframe (self, path):
    ''' Bake sound to a keyframe in this shape key
    '''
        if self.sound_added == False:
            ctx.set ('GRAPH_EDITOR')
            bpy.ops.graph.sound_bake (filepath=path)
            ctx.set ('TEXT_EDITOR')
            self.sound_added = True
    def add_sound_to_sequencer (self, path, frame):
    ''' Add audio to the sequencer - independent of baking
    '''
        ctx.set ('SEQUENCE_EDITOR')
        bpy.ops.sequencer.sound_strip_add(filepath=sound_file_path)
        sound_strip = bpy.context.scene.sequence_editor.active_strip
        # set video to length of the audio
        if bpy.context.scene.frame_start == 1:
            bpy.context.scene.frame_start = 0
        if bpy.context.scene.frame_end < sound_strip.frame_final_duration:
            bpy.context.scene.frame_end = sound_strip.frame_final_duration
        ctx.set ('TEXT_EDITOR')
    def add_envelope (self):
    ''' Add an envelope modifier to the baked sound keyframe's fcurve
    '''
        if self.get_envelope() == None:
            ctx.set ('GRAPH_EDITOR')
            bpy.ops.graph.fmodifier_add(type='ENVELOPE')
            ctx.set ('TEXT_EDITOR')
        return self.get_envelope()
    def get_envelope (self):
    ''' Return the envelope modifier at this baked sound keyframe's fcurve
    '''
        for modifier in self.get_keyframe_curve().modifiers:
            if modifier.type == "ENVELOPE":
                return modifier
        return None
    def set_envelope (self, reference, minimum, maximum):
    ''' Adjust the modifier's value if this shape key has an envelope
    '''
        envelope = self.get_envelope()
        if envelope != None:
            envelope.reference_value = reference
            envelope.default_min = minimum
            envelope.default_max = maximum
        return envelope
    def get_value (self):
    ''' Read the value of this shape key
    '''
        return self.key.value
    def set_value (self, value):
    ''' Adjust the value of this shape key
    '''
        self.key.value = value
        return self.key.value

# get context and the object to key
ctx = Context_Manager ()
obj = ctx.object ()

# add shape key
audio_key = Audio_Shape_Key (obj, custom_key_name, 1.0)

# add keyframe to shape key value
audio_key.set_keyframe (starting_frame, 1.0)

# bake sound to the shape key fcurve
audio_key.add_sound_to_keyframe (sound_file_path)

# add envelope to the sound / shape key fcurve
audio_key.add_envelope ()
audio_key.set_envelope (0.0, 0.0, 0.8)

# add same sound at same frame in sequencer
audio_key.add_sound_to_sequencer (sound_file_path, starting_frame)