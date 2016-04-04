import bpy
import math

class Transitions (object):
    def push (toggle_in, toggle_out, toggle_mid, frames):
        """Slide a transform strip's position from left to right"""
        # references to active transform strip and its parent strip
        strip = bpy.context.scene.sequence_editor.active_strip
        parent = bpy.context.scene.sequence_editor.active_strip.input_1
        # get the current frame on the timeline
        playhead = bpy.context.scene.frame_current
        # edge of screen width accounting for image scale
        width = 50 + strip.scale_start_x * 50
        starting_x = strip.translate_start_x
        if toggle_mid:
            strip.keyframe_insert ('translate_start_x', -1, playhead)
            playhead += frames
            strip.translate_start_x = width
            strip.keyframe_insert ('translate_start_x', -1, playhead)
        if toggle_in:
            # keyframe the x position to just beyond L edge of screen
            playhead = strip.frame_start
            strip.translate_start_x = -(width)
            strip.keyframe_insert ('translate_start_x', -1, strip.frame_start)
            # change frames and keyframe x position to center of screen
            playhead = strip.frame_start+frames
            strip.translate_start_x = starting_x
            strip.keyframe_insert ('translate_start_x', -1, strip.frame_start+frames)
        if toggle_out:
            # keyframe the x position to end frame minus transition frames
            playhead = strip.frame_start - frames + strip.frame_final_duration
            strip.keyframe_insert ('translate_start_x', -1, playhead)
            # change frames and keyframe x position to just beyond R edge of screen
            playhead = strip.frame_start + strip.frame_final_duration
            strip.translate_start_x = width
            strip.keyframe_insert ('translate_start_x', -1, playhead)
        return None

    def pull (toggle_in, toggle_out, toggle_mid, frames):
        """Slide a transform strip's position from right to left"""
        # references to active transform strip and its parent strip
        strip = bpy.context.scene.sequence_editor.active_strip
        parent = bpy.context.scene.sequence_editor.active_strip.input_1
        # get the current frame on the timeline
        playhead = bpy.context.scene.frame_current
        # edge of screen width accounting for image scale
        width = 50 + strip.scale_start_x * 50
        starting_x = strip.translate_start_x
        if toggle_mid:
            strip.keyframe_insert ('translate_start_x', -1, playhead)
            playhead += frames
            strip.translate_start_x = -width
            strip.keyframe_insert ('translate_start_x', -1, playhead)
        if toggle_in:
            # keyframe the x position to just beyond R edge of screen
            playhead = strip.frame_start
            strip.translate_start_x = width
            strip.keyframe_insert ('translate_start_x', -1, strip.frame_start)
            # change frames and keyframe x position to center of screen
            playhead = strip.frame_start+frames
            strip.translate_start_x = starting_x
            strip.keyframe_insert ('translate_start_x', -1, strip.frame_start+frames)
        if toggle_out:
            # keyframe the x position to end frame minus transition duration
            playhead = strip.frame_start - frames + strip.frame_final_duration
            strip.keyframe_insert ('translate_start_x', -1, playhead)
            # change frames and keyframe x position to just beyond L edge of screen
            playhead = strip.frame_start + strip.frame_final_duration
            strip.translate_start_x = -width
            strip.keyframe_insert ('translate_start_x', -1, playhead)
        return None

    def hoist (toggle_in, toggle_out, toggle_mid, frames):
        """Slide a transform strip's position from bottom to top"""
        # references to active transform strip and its parent strip
        strip = bpy.context.scene.sequence_editor.active_strip
        parent = bpy.context.scene.sequence_editor.active_strip.input_1
        # get the current frame on the timeline
        playhead = bpy.context.scene.frame_current
        # edge of screen height accounting for image scale and uniform scale toggled
        if strip.use_uniform_scale:
            height = 50 + strip.scale_start_x * 50
        else:
            height = 50 + strip.scale_start_y * 50
        starting_y = strip.translate_start_y
        if toggle_mid:
            strip.keyframe_insert ('translate_start_y', -1, playhead)
            playhead += frames
            strip.translate_start_y = height
            strip.keyframe_insert ('translate_start_y', -1, playhead)
        if toggle_in:
            # keyframe the y position to just beyond bottom edge of screen
            playhead = strip.frame_start
            strip.translate_start_y = -height
            strip.keyframe_insert ('translate_start_y', -1, strip.frame_start)
            # change frames and keyframe y position to center of screen
            playhead = strip.frame_start+frames
            strip.translate_start_y = starting_y
            strip.keyframe_insert ('translate_start_y', -1, strip.frame_start+frames)
        if toggle_out:
            # keyframe the y position to end of strip minus transition duration
            playhead = strip.frame_start - frames + strip.frame_final_duration
            strip.keyframe_insert ('translate_start_y', -1, playhead)
            # change frames and keyframe y position to just beyond top edge of screen
            playhead = strip.frame_start + strip.frame_final_duration
            strip.translate_start_y = height
            strip.keyframe_insert ('translate_start_y', -1, playhead)
        return None

    def drop (toggle_in, toggle_out, toggle_mid, frames):
        """Slide a strip's opacity between opaque and transparent over time"""
        # references to active transform strip and its parent strip
        strip = bpy.context.scene.sequence_editor.active_strip
        parent = bpy.context.scene.sequence_editor.active_strip.input_1
        # get the current frame on the timeline
        playhead = bpy.context.scene.frame_current
        # edge of screen height accounting for image scale and uniform scale toggled
        if strip.use_uniform_scale:
            height = 50 + strip.scale_start_x * 50
        else:
            height = 50 + strip.scale_start_y * 50
        starting_y = strip.translate_start_y
        if toggle_mid:
            strip.keyframe_insert ('translate_start_y', -1, playhead)
            playhead += frames
            strip.translate_start_y = -height
            strip.keyframe_insert ('translate_start_y', -1, playhead)
        if toggle_in:
            # keyframe the y position to just beyond top edge of screen
            playhead = strip.frame_start
            strip.translate_start_y = height
            strip.keyframe_insert ('translate_start_y', -1, strip.frame_start)
            # change frames and keyframe y position to center of screen
            playhead = strip.frame_start+frames
            strip.translate_start_y = starting_y
            strip.keyframe_insert ('translate_start_y', -1, strip.frame_start+frames)
        if toggle_out:
            # keyframe the y position to end of strip minus transition duration
            playhead = strip.frame_start - frames + strip.frame_final_duration
            strip.keyframe_insert ('translate_start_y', -1, playhead)
            # change frames and keyframe y position to just beyond bottom of screen
            playhead = strip.frame_start + strip.frame_final_duration
            strip.translate_start_y = -height
            strip.keyframe_insert ('translate_start_y', -1, playhead)
        return None

    def fade (toggle_in, toggle_out, toggle_mid, frames):
        """Slide a transform strip's position from left to right"""
        # references to active transform strip and its parent strip
        strip = bpy.context.scene.sequence_editor.active_strip
        parent = bpy.context.scene.sequence_editor.active_strip.input_1
        # get the current frame on the timeline
        playhead = bpy.context.scene.frame_current
        starting_alpha = strip.blend_alpha
        if toggle_mid:
            strip.keyframe_insert ('blend_alpha', -1, playhead)
            playhead += frames
            strip.blend_alpha = 0.0
            strip.keyframe_insert ('blend_alpha', -1, playhead)
        if toggle_in:
            # keyframe to transparent
            playhead = strip.frame_start
            strip.blend_alpha = 0.0
            strip.keyframe_insert ('blend_alpha', -1, strip.frame_start)
            # change frames and keyframe to opaque
            playhead = strip.frame_start+frames
            strip.blend_alpha = starting_alpha
            strip.keyframe_insert ('blend_alpha', -1, strip.frame_start+frames)
        if toggle_out:
            # keyframe to current opacity
            playhead = strip.frame_start - frames + strip.frame_final_duration
            strip.keyframe_insert ('blend_alpha', -1, playhead)
            # change positions and keyframe to transparent
            playhead = strip.frame_start + strip.frame_final_duration
            strip.blend_alpha = 0.0
            strip.keyframe_insert ('blend_alpha', -1, playhead)
        return None