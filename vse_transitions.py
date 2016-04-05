import bpy
import math

class Transition (object):
    def handler ():
        # all transitions to call mapped to transition_type string
        effect = {'left':Transition.left, 'right':Transition.right,
                'top':Transition.top, 'bottom':Transition.bottom,
                'fade':Transition.opacity_down, 'unfade':Transition.opacity_up, 
                'scale_up':Transition.scale_up, 'scale_down':Transition.scale_down, 
                'clockwise':Transition.rotate_clock,'counterclock':Transition.rotate_counterclock}
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
        # move to and keyframe the starting frame (just leaving its current value)
        bpy.context.scene.frame_current = starting_frame
        strip.keyframe_insert (property_name, -1, starting_frame)
        # move to and keyframe the ending frame with the final property value
        bpy.context.scene.frame_current += duration
        
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

        strip.keyframe_insert (property_name, -1, starting_frame+duration)
        return None

    def clear (strip):
        """Remove all keyframes from the transition properties fields and reset their values"""
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
        strip.translate_start_x = 0.0
        strip.translate_start_y = 0.0
        strip.blend_alpha = 1.0
        strip.use_uniform_scale = True
        strip.scale_start_x = 1.0
        strip.rotation_start = 1.0

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

    def scale_up (strip, start_frame, duration):
        end_value = strip.scale_start_x * 3.5 * strip.transition_strength
        Transition.set (strip, 'scale_start_x', end_value, start_frame, duration)
        if not strip.use_uniform_scale:
            end_value = strip.scale_start_y *3.5 * strip.transition_strength
            Transition.set (strip, 'scale_start_y', end_value, start_frame, duration)

    def scale_down (strip, start_frame, duration):
        end_value = strip.scale_start_x * 0.05 / strip.transition_strength
        Transition.set (strip, 'scale_start_x', end_value, start_frame, duration)
        if not strip.use_uniform_scale:
            end_value = strip.scale_start_y * 0.05 / strip.transition_strength
            Transition.set (strip, 'scale_start_y', end_value, start_frame, duration)

    def rotate_clock (strip, start_frame, duration):
        end_value = strip.rotation_start + (360 * strip.transition_strength)
        Transition.set (strip, 'rotation_start', end_value, start_frame, duration)

    def rotate_counterclock (strip, start_frame, duration):
        end_value = strip.rotation_start - (360 * strip.transition_strength)
        Transition.set (strip, 'rotation_start', end_value, start_frame, duration)