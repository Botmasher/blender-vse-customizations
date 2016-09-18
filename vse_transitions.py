import math
import bpy
from bpy.props import *

class Transition (object):
    def handler ():
        # all transitions to call mapped to transition_type string
        effect = {'left':Transition.left, 'right':Transition.right,
                'top':Transition.top, 'bottom':Transition.bottom,
                'fade':Transition.opacity_down, 'unfade':Transition.opacity_up, 
                'scale':Transition.scale, 'scale_down':Transition.scale_down, 
                'clockwise':Transition.rotate_clock,'counterclock':Transition.rotate_counterclock}
        # references to active transform strip
        strip = bpy.context.scene.sequence_editor.active_strip
        # length of the transition (distance between keyframes)
        duration = strip.transition_frames
        
        if strip.transition_placement == 'mid':
            # current frame
            start_frame = bpy.context.scene.frame_current
            # call the effect function
            effect[strip.transition_type] (strip, start_frame, duration)
       
        elif strip.transition_placement == 'in':
            # count frames from left edge of the strip
            start_frame = strip.frame_start + duration
            # call the effect function, reversing duration for transition "in" effect
            effect[strip.transition_type] (strip, start_frame, -duration)
            
            # move playhead to avoid keyframing wrong values back-to-back
            bpy.context.scene.frame_current = start_frame + 1
        
        elif strip.transition_placement == 'out':
            # count frames from right edge of the strip
            start_frame = strip.frame_start + strip.frame_final_duration - duration
            # move playhead to last frame to avoid keyframing to wrong values
            #bpy.context.scene.frame_current = strip.frame_start + strip.frame_final_duration
            # call the effect function
            effect[strip.transition_type] (strip, start_frame, duration)
            
            # move playhead to avoid keyframing wrong values back-to-back 
            bpy.context.scene.frame_current = start_frame - 1
        return None

    def get_screen_dimensions (strip):
        # edges of screen (as percentage) accounting for image scale and uniform scale toggled
        width = 50 + strip.scale_start_x * 50
        if strip.use_uniform_scale:
            height = 50 + strip.scale_start_x * 50
        else:
            height = 50 + strip.scale_start_y * 50
        return (width,height)

    def set (strip, property_name, end_value, starting_frame, duration):
        """Move to starting frame, set a keyframe for a property, move to final frame (starting frame plus duration), change property value, set keyframe for the property."""
        # move to and keyframe the starting frame (just leaving its current value)
        bpy.context.scene.frame_set(starting_frame)
        strip.keyframe_insert (property_name, -1, starting_frame)

        # move to and keyframe the ending frame with the final property value
        bpy.context.scene.frame_current += duration
        
        # insert keyframe on the property at the final frame
        strip.keyframe_insert (property_name, -1, starting_frame+duration)

        # give the relevant property_name a new ending value
        if property_name == 'translate_start_x':
            strip.translate_start_x = end_value
        elif property_name == 'translate_start_y':
            strip.translate_start_y = end_value
        elif property_name == 'scale_start_x':
            strip.scale_start_x = end_value
        elif property_name == 'scale_start_y':
            strip.scale_start_y = end_value
        elif property_name == 'rotation_start':
            strip.rotation_start = end_value
        elif property_name == 'blend_alpha':
            strip.blend_alpha = end_value
        else:
            pass

        # insert keyframe on the property at the final frame
        strip.keyframe_insert (property_name, -1, starting_frame+duration)
        
        # set transparency type to stack with other images/movies
        strip.blend_type = 'ALPHA_OVER'
        # refresh the sequence editor window
        bpy.ops.sequencer.refresh_all()
        return None

    def clear (strip):
        """Remove all keyframes from the transition properties fields and reset their values"""
        # select frame in the center of the strip and remember values
        bpy.context.scene.frame_current = ((strip.frame_start+strip.frame_final_duration) - strip.frame_start) * 0.5
        remember_values =               \
            [ strip.blend_alpha,        \
            strip.translate_start_x,    \
            strip.translate_start_y,    \
            strip.use_uniform_scale,    \
            strip.scale_start_x,        \
            strip.scale_start_y,        \
            strip.rotation_start ]
        # move to the first frame in this strip
        bpy.context.scene.frame_current = strip.frame_start
        # get list of all properties that Transition messes with
        properties = Transition.strip_properties(strip)
        # count through every frame looking for keyframes
        for frame in range (strip.frame_start-1, strip.frame_start+strip.frame_final_duration+1):
            # attempt to remove keyframes on all transition properties this frame
            for prop in properties:
                try:
                    strip.keyframe_delete(prop, -1, frame)
                except:
                    pass
            # try to skip ahead to the next keyframe
            try:
                bpy.ops.screen.keyframe_jump()
            except:
                pass
            # set the frame variable to match skip ahead
            frame = bpy.context.scene.frame_current
        # reset transform properties to default values
        strip.translate_start_x = remember_values[1]
        strip.translate_start_y = remember_values[2]
        strip.blend_alpha = remember_values[0]
        strip.use_uniform_scale = remember_values[3]
        strip.scale_start_x = remember_values[4]
        strip.scale_start_y = remember_values[5]
        strip.rotation_start = remember_values[6]
        # refresh the sequence editor
        bpy.ops.sequencer.refresh_all()
        return None

    def strip_properties (strip):
        """Strip property values to transition when given a property name string as key"""
        return {'blend_alpha': strip.blend_alpha, 
                'translate_start_x': strip.translate_start_x, 
                'translate_start_y': strip.translate_start_y, 
                'scale_start_x': strip.scale_start_x, 
                'scale_start_y': strip.scale_start_y, 
                'rotation_start': strip.rotation_start
                }

    def left (strip, start_frame, duration):
        """Set up values to slide a strip's position to or from left edge of screen"""
        end_value = -(Transition.get_screen_dimensions(strip)[0]) * strip.transition_strength
        # setup the keyframing function
        Transition.set (strip, 'translate_start_x', end_value, start_frame, duration)

    def right (strip, start_frame, duration):
        """Set up values to slide a strip's position to or from right edge of screen"""
        end_value = Transition.get_screen_dimensions(strip)[0] * strip.transition_strength
        # setup the keyframing function
        Transition.set (strip, 'translate_start_x', end_value, start_frame, duration)

    def top (strip, start_frame, duration):
        """Set up values to slide a strip's position to or from top edge of screen"""
        end_value = Transition.get_screen_dimensions(strip)[1] * strip.transition_strength
        # setup the keyframing function
        Transition.set (strip, 'translate_start_y', end_value, start_frame, duration)

    def bottom (strip, start_frame, duration):
        """Set up values to slide a strip's position to or from bottom edge of screen"""
        end_value = -(Transition.get_screen_dimensions(strip)[1]) * strip.transition_strength
        # setup the keyframing function
        Transition.set (strip, 'translate_start_y', end_value, start_frame, duration)

    def opacity_up (strip, start_frame, duration):
        """Set up values to slide a strip's opacity to or from opaque"""
        end_value = 0.0 + strip.transition_strength
        # setup the keyframing function
        Transition.set (strip, 'blend_alpha', end_value, start_frame, duration)

    def opacity_down (strip, start_frame, duration):
        """Set up values to slide a strip's opacity to or from transparent"""
        end_value = 1.0 - strip.transition_strength
        # setup the keyframing function
        Transition.set (strip, 'blend_alpha', end_value, start_frame, duration)

    def scale (strip, start_frame, duration):
        # check if need to scale y separately
        if not strip.use_uniform_scale:
            # scale proportionally based on y to x ratio
            end_value = (strip.scale_start_y/strip.scale_start_x) * strip.transition_strength
            Transition.set (strip, 'scale_start_y', end_value, start_frame, duration)
        # scale x (or both if uniform scale is checked)
        end_value = strip.scale_start_x * strip.transition_strength
        Transition.set (strip, 'scale_start_x', end_value, start_frame, duration)

    def scale_down (strip, start_frame, duration):
        # check if need to scale y separately
        if not strip.use_uniform_scale:
            # scale down proportionally based on y to x ratio
            end_value = 0.05 * (strip.scale_start_y / strip.scale_start_x) / strip.transition_strength
            Transition.set (strip, 'scale_start_y', end_value, start_frame, duration)
        # scale x (scales both if using uniform scale)
        end_value = 0.05 / strip.transition_strength
        Transition.set (strip, 'scale_start_x', end_value, start_frame, duration)

    def rotate_clock (strip, start_frame, duration):
        end_value = strip.rotation_start + (360 * strip.transition_strength)
        Transition.set (strip, 'rotation_start', end_value, start_frame, duration)

    def rotate_counterclock (strip, start_frame, duration):
        end_value = strip.rotation_start - (360 * strip.transition_strength)
        Transition.set (strip, 'rotation_start', end_value, start_frame, duration)


#
# Custom properties for Transition object to read as transition options
#
bpy.types.TransformSequence.transition_type = EnumProperty(
    items = [('counterclock', 'Counterclock', 'to or from counterclockwise rotation'),
             ('clockwise', 'Clockwise', 'to or from a clockwise rotation'),
             ('scale', 'Scale', 'zoom in or out (scale set)'),
             ('unfade', 'Unfade', 'to or from opaque'),
             ('fade', 'Fade', 'to or from transparent'),
             ('bottom', 'Bottom', 'to or from bottom'),
             ('top', 'Top', 'to or from top'),
             ('right', 'Right', 'to or from right edge'),
             ('left', 'Left', 'to or from left edge')],
    name = 'Type',
    default = 'fade',
    description = 'Type of transition to add to this strip'
    )

bpy.types.TransformSequence.transition_placement = EnumProperty(
    items = [('in', 'In', 'Add transition to left edge of strip'),
             ('out', 'Out', 'Add transition to right edge of strip'),
             ('mid', 'Mid', 'Add transition at the current frame')],
    name = 'Placement',
    description = 'Where to add transition within this strip'
    )

bpy.types.TransformSequence.transition_frames = IntProperty (
    name = 'Duration (frames)', 
    default = 10,
    description = 'Number of frames the transition will last'
    )

bpy.types.TransformSequence.transition_strength = FloatProperty (
    name = 'Strength', 
    default = 1.0, 
    min = 0.0, 
    max = 5.0, 
    description = 'Change the impact of the effect (defaults to 1.0 = 100%)'
    )

# bpy.types.TransformSequence.transition_in = BoolProperty(
#     name = 'In',
#     description = 'Add edge transition (duration counted forwards from left edge of this strip)'
#     )

# bpy.types.TransformSequence.transition_out = BoolProperty(
#     name = 'Out',
#     description = 'Add edge transition (duration counted backwards from right edge of this strip)'
#     )
    
# bpy.types.TransformSequence.transition_mid = BoolProperty(
#     name = 'Current Frame',
#     description = 'Add transition at this point (duration counted forwards from current frame)'
#     )

class CustomTransitionsPanel (bpy.types.Panel):
    """Create a Panel in Strip Properties"""
    bl_label = 'Transitions'
    bl_idname = 'strip.transitions_panel'
    bl_space_type = 'SEQUENCE_EDITOR'
    bl_region_type = 'UI'
    
    def draw (self, context):
        strip = context.scene.sequence_editor.active_strip
        
        # check that active strip is a transform strip
        is_transform = False
        if strip != None:
            is_transform = strip.type == 'TRANSFORM'

        # display if this is already a transition-ready transform strip
        if is_transform:
            # drop down menu for selecting transition function
            self.layout.row().prop(strip,'transition_type')
            # integer input for setting transition length in frames
            self.layout.row().prop(strip,'transition_frames')
            self.layout.row().prop(strip,'transition_strength')
            # check boxes for toggling transition in/out/mid
            #row_1 = self.layout.split(0.4)
            #row_1.prop(strip,'transition_in')
            #row_1.prop(strip,'transition_out')
            #self.layout.row().prop(strip,'transition_mid')
            # button series for choosing placement (in/out/current)
            self.layout.prop(strip,'transition_placement', expand=True)
            # execute button
            self.layout.separator()
            # text for transition button
            button_text = "Create Transition"

        # display if this is not a transition-ready transform strip
        else:
            button_text = "Add Transform Strip"

        # display transition add button
        self.layout.operator('strip.transition_add', text=button_text)

        # display keyframe removal button
        self.layout.operator('strip.transition_delete', text="/!\\ Clear Keyframe Fields /!\\")

class AddTransition (bpy.types.Operator):
    bl_label = 'Add Transitions'
    bl_idname = 'strip.transition_add'
    bl_description = 'Use transition settings to create keyframes in active strip'
    def execute (self, context):

        #
        # Transition-transform-strips instead of all transits in one transform
        #

        if this is a transform strip or a movie/image
            # add transform strip (operator class below)
            # make sure that new strip is active and selected
            # run Transition.handler() on that strip


        # add the selected transition if this is a transform strip
        if context.scene.sequence_editor.active_strip.type == 'TRANSFORM':
            try:
                Transition.handler()
            except:
                raise NotImplementedError ('Method Transition.handler() not implemented in Transition object')
        # otherwise add a transform strip
        else:
            add_transform_strip(context.scene.sequence_editor.active_strip)
        return{'FINISHED'}

class DeleteTransition (bpy.types.Operator):
    bl_label = 'Delete Transitions'
    bl_idname = 'strip.transition_delete'
    bl_description = 'Delete ALL visible keyframes from strip transition fields (opacity, position, scale, rotation)'
    def execute (self, context):
        # delete all keyframes if this is a transform strip
        if context.scene.sequence_editor.active_strip.type == 'TRANSFORM':
            try:
                Transition.clear(context.scene.sequence_editor.active_strip)
            except:
                raise NotImplementedError('Method Transition.clear(strip) not implemented in Transition object')
        # otherwise add a transform strip
        else:
            add_transform_strip(context.scene.sequence_editor.active_strip)
        return {'FINISHED'}

def add_transform_strip (base_strip):
    # deselect all strips to avoid adding multiple effect strips
    for s in bpy.context.scene.sequence_editor.sequences_all:
        s.select = False

    #
    # Transition-transform-strips instead of all transits in one transform
    #

    # Should first argument expect base_strip? Just any transitionable strip?
    
    if SELECTEDSTRIP is a 'TRANSFORM' strip or in ('IMAGE', 'MOVIE'):
        # create a new transform strip
        # select that new transform strip
        # read the current selected transition property for building name
        # rename transform strip to match selected property
        # set transform blend type to ALPHA_OVER
        # if it's a parent strip, set its type to alpha_over
        # return back to execute function that ran this one

    # make sure this is a transform-ready image or movie
    if base_strip.type in ('IMAGE', 'MOVIE'):
        # select this strip and create a transform effect strip on it
        base_strip.select = True
        bpy.ops.sequencer.effect_strip_add(type='TRANSFORM')
        # find strip we just created and set it to alpha bg
        for s in bpy.context.scene.sequence_editor.sequences_all:
            # check that it uses this base strip as its input
            if hasattr(s,'input_1') and s.input_1.name == base_strip.name:
                s.blend_type = 'ALPHA_OVER'
        # make this parent strip invisible
        base_strip.blend_type = 'ALPHA_OVER'
        base_strip.blend_alpha = 0.0
    return None

def register():
    bpy.utils.register_class(CustomTransitionsPanel)
    bpy.utils.register_class(AddTransition)
    bpy.utils.register_class(DeleteTransition)

def unregister():
    bpy.utils.unregister_class(CustomTransitionsPanel)
    bpy.utils.unregister_class(AddTransition)
    bpy.utils.unregister_class(DeleteTransition)

if __name__ == '__main__':
    register()
    #unregister()