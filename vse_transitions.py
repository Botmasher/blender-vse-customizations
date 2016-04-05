import bpy
import math

class Transition (object):
    def handler ():
        effect = {'left':Transition.left,'right':Transition.right,'top':Transition.top,'bottom':Transition.bottom,'fade':Transition.fade}
        # references to active transform strip and its parent
        strip = bpy.context.scene.sequence_editor.active_strip
        parent = strip.input_1
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
        elif strip.transition_placement == 'out':
            # count frames from right edge of the strip
            start_frame = strip.frame_start + strip.frame_final_duration - duration
            # call the effect function
            effect[strip.transition_type] (strip, start_frame, duration)        
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
        # move to and keyframe the starting frame
        bpy.context.scene.frame_current = starting_frame
        strip.keyframe_insert (property_name, -1, starting_frame)
        # move to and keyframe the ending frame with the final property value
        bpy.context.scene.frame_current += duration
        
        # set keyframe values on the appropriate property_name
        if property_name == 'translate_start_x':
            strip.translate_start_x = end_value
        elif property_name == 'translate_start_y':
            strip.translate_start_y = end_value
        elif property_name == 'scale_start_x':
            strip.scale_start_x = end_value
        elif property_name == 'scale_start_y':
            strip.scale_start_y = end_value
        elif property_name == 'blend_alpha':
            strip.blend_alpha = end_value
        else:
            pass

        strip.keyframe_insert (property_name, -1, starting_frame+duration)
        return None

    def strip_properties (strip):
        """Strip property values to transition when given a property name string as key"""
        return {'translate_start_x': strip.translate_start_x,
                'translate_start_y': strip.translate_start_y,
                'scale_start_x': strip.scale_start_x,
                'scale_start_y': strip.scale_start_y,
                'blend_alpha': strip.blend_alpha
                }

    def left (strip, start_frame, duration):
        """Set up values to slide a strip's position to or from left edge of screen"""
        end_value = -(Transition.get_screen_dimensions(strip)[0])
        # setup the keyframing function
        Transition.set (strip, 'translate_start_x', end_value, start_frame, duration)

    def right (strip, start_frame, duration):
        """Set up values to slide a strip's position to or from right edge of screen"""
        end_value = Transition.get_screen_dimensions(strip)[0]
        # setup the keyframing function
        Transition.set (strip, 'translate_start_x', end_value, start_frame, duration)

    def top (strip, start_frame, duration):
        """Set up values to slide a strip's position to or from top edge of screen"""
        end_value = Transition.get_screen_dimensions(strip)[1]
        # setup the keyframing function
        Transition.set (strip, 'translate_start_y', end_value, start_frame, duration)

    def bottom (strip, start_frame, duration):
        """Set up values to slide a strip's position to or from bottom edge of screen"""
        end_value = -(Transition.get_screen_dimensions(strip)[1])
        # setup the keyframing function
        Transition.set (strip, 'translate_start_y', end_value, start_frame, duration)

    def fade (strip, start_frame, duration):
        """Set up values to slide a strip's opacity to or from transparent"""
        end_value = 0.0
        # setup the keyframing function
        Transition.set (strip, 'blend_alpha', end_value, start_frame, duration)