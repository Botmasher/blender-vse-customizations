import bpy

# audio input drives shape key value
# a Blender Python script by Botmasher (Josh)

# 0. select object in 3d view
# 1. make sure this script is open in the text editor
# 2. add path to your audio file below
# 3. (optional) rename your shape key below
# 4. (optional) choose a scene frame to start playing your audio file below
# 5. click "Run script" with this script open in the text editor

# audio to use and when to start playing
sound_file_path = '/Users/username/test.wav'   # path to your file
custom_key_name = 'audio-shape-key'            # rename your shape key
starting_frame = 0                             # scene frame to start playback

class Context_Mgr:
    text = "TEXT_EDITOR"
    graph = "GRAPH_EDITOR"
    vse = "SEQUENCE_EDITOR"
    def __init__ (self):
        return self
    def get (self):
        return bpy.context.area.type
    def set (self, context):
        old_context = bpy.context.area.type
        bpy.context.area.type = context
        return (old_context, context)
    def get_obj (self):
        return bpy.context.object

# get context and the object to shape key
ctx = Context_Mgr ()
obj = ctx.get_obj ()

class Audio_Shape_Key:
    def __init__ (self, selected_object, key_name):
        # add and store shape key
        if selected_object.data.shape_keys == None:
            selected_object.shape_key_add()
        shape_key = selected_object.shape_key_add()
        shape_key.name = key_name
        shape_key.value = 1.0
        self.key = shape_key
        self.sound_added = False
        # create dictionary for keyframes
        self.keyframes = {}
        # object this key belongs to
        self.object = selected_object
        ## key block this key belongs to
        #self.block = parent_key_block
    def set_keyframe (self, frame, value):
        bpy.context.scene.frame_current = frame
        self.key.keyframe_insert ("value", frame = frame)
        self.key.value = value
        self.key.keyframe_insert ("value", frame = frame)
        self.keyframes[frame] = value
    def get_keyframe_value (self, frame):
        return self.keyframes [frame]
    def get_keyframe_curve (self):
        # return the keyframe fcurve at this frame
        if self.object.data.animation_data.action is None:
            return None
        for fcurve in self.object.data.animation_data.action.fcurves:
            # the fcurve's name is the shape key path plus .value
            if (self.key.name+"\"") in fcurve.data_path:
                return fcurve
        return None
    def add_sound_to_keyframe (self, path):
        if self.sound_added == False:
            ctx.set ('GRAPH_EDITOR')
            bpy.ops.graph.sound_bake (filepath=path)
            ctx.set ('TEXT_EDITOR')
            self.sound_added = True
    def add_sound_to_sequencer (self, path, frame):
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
        if self.get_envelope() == None:
            ctx.set ('GRAPH_EDITOR')
            bpy.ops.graph.fmodifier_add(type='ENVELOPE')
            ctx.set ('TEXT_EDITOR')
        return self.get_envelope()
    def get_envelope (self):
        for modifier in self.get_keyframe_curve().modifiers:
            if modifier.type == "ENVELOPE":
                return modifier
        return None
    def set_envelope (self, reference, minimum, maximum):
        envelope = self.get_envelope()
        if envelope != None:
            envelope.reference_value = reference
            envelope.default_min = minimum
            envelope.default_max = maximum
        return envelope

# add shape key
audio_key = Audio_Shape_Key (obj, custom_key_name)

# add keyframe to shape key value
audio_key.set_keyframe (starting_frame, 1.0)

# bake sound to the shape key fcurve
audio_key.add_sound_to_keyframe (sound_file_path)

# add envelope to the sound / shape key fcurve
audio_key.add_envelope ()
audio_key.set_envelope (0.0, 0.0, 0.8)

# add same sound at same frame in sequencer
audio_key.add_sound_to_sequencer (sound_file_path, starting_frame)