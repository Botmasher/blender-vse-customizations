#!/usr/bin/env python
import bpy
from math import log
from mathutils import Vector
from bpy.props import *

# TODO track markers (incl replace and remove) through something other than name (add uuid property?)
# TODO adjust all markers, or all markers following currently selected one
# TODO place marker empty through mesh data + object data -> link to scene

bpy.types.TimelineMarker.marker_id = StringProperty(
    name = 'Marker ID',
    description = 'Unique timeline marker ID'
)

class CamAnim:
	def __init__(self, cam=bpy.context.scene.camera, marker_name_text="camanim_marker"):
		self.cam = cam
		# TODO decide to store markers array vs dict
		self.markers = {}
		self.marker_name_text = marker_name_text
		self.current_marker = None
		return None

	def place_marker(self):
		"""Place marker in the scene at current cam loc and rot"""
		bpy.ops.object.empty_add(type="SINGLE_ARROW")
		marker = bpy.context.scene.objects.active
		marker.name = self.marker_name_text
		marker.location = self.cam.location
		marker.rotation_euler = self.cam.rotation_euler
		self.markers[marker.as_pointer] = marker
		return marker

	def replace_marker(self, marker):
		"""Update selected currently placed marker in the scene to current cam loc and rot"""
		if self.is_marker(marker):
			marker.location = self.cam.location
			marker.rotation_euler = self.cam.rotation_euler
		return marker

	def remove_marker(self, marker):
		"""Delete selected currently placed marker from camanim tracking"""
		if self.is_marker(marker):
			bpy.context.scene.objects.unlink(marker)			# remove from scene
			bpy.data.objects.remove(marker, do_unlink=True)		# delete and verify unlink from whole project
		return marker

	def jump_first_marker(self):
		"""Jump to the first tracked marker"""
		sorted_markers = self.sort_markers()
		self.snap_cam_to_marker(sorted_markers[0])
		return None

	def jump_last_marker(self):
		"""Jump to the final tracked marker"""
		sorted_markers = self.sort_markers()
		self.snap_cam_to_marker(sorted_markers[len(sorted_markers) - 1])
		return None

	def jump_marker(self, marker_count):
		"""Jump camera count markers earlier or later along path"""
		markers = self.sort_markers()
		if self.current_marker is None:
			self.current_marker = markers[0]
		try:
			marker_i = int(self.current_marker_name.split(".")[1])
		except:
			marker_i = len(markers)
		jump_i = marker_i + marker_count
		# cycle forward or backward through markers
		if jump_i > len(markers) or jump_i < 0:
			jump_i = 0
		else:
			jump_i -= 1		# generated names start from 001 and len is 1 over index
		self.snap_cam_to_marker(markers[jump_i])
		return None

	def is_marker(self, marker=None, obj_name=None):
		"""Check if named object is a CamAnim marker"""
		if marker is not None and marker.as_pointer in self.markers:
			return True
		elif obj_name is not None and self.marker_name_text in obj_name:
			return True
		else:
			return False

	def has_current_marker(self):
		"""Check if there is a stored current marker"""
		if self.current_marker is not None:
			return True
		return False

	def get_current_marker_details(self):
		"""Find the name and index of the current marker"""
		return {
			'name': self.current_marker.name,
			'id': self.get_marker_index(self.current_marker)
		}

	def get_marker_index(self, marker):
		"""Return the index along path of the current marker"""
		if marker is not None:
			sorted_markers = self.sort_markers()
			marker_i = None
			for i in range(len(sorted_markers)):
				if sorted_markers[i] == marker:
					marker_i = i
			if marker_i is not None: return marker_i
		return None

	def snap_cam_to_marker(self, marker):
		"""Set camera location and rotation to match marker"""
		self.cam.location = marker.location
		self.cam.rotation_euler = marker.rotation_euler
		self.current_marker = marker
		return marker

	def sort_markers(self, do_resort=True):
		"""Retrieve well-named markers and sort from earliest to latest

		Caution when proceeding without resorting as markers unsync easily! (e.g. user deletes marker)
		"""
		# TODO handle sorting markers array
		if do_resort == True:
			unsorted_markers = [o.name for o in bpy.context.scene.objects if self.is_marker(o)]
			unsorted_markers.sort()
			# markers count from .001 - place latest marker (unappended) at the end
			sorted_marker_names.append(unsorted_markers.pop(0))
            sorted_markers = [bpy.contxt.scene.objects[m] for m in sorted_marker_names]
        # TODO return and use a sorted list instead of the dictionary
        return sorted_markers

	def animate(self, frames_per_space=3, frames_per_degree=0.1, min_frames_per_kf=0, max_frames_per_kf=9999, frames_pause=3):
		"""Use placed markers to set keyframes timed out by frames per loc and rot unit"""
		marker_names = self.sort_markers()
		bpy.context.scene.frame_current = bpy.context.scene.frame_start + 1

		# keyframe cam along markers
		for i in range(len(marker_names)):
			name = marker_names[i]
			self.snap_cam_to_marker(name)
			self.cam.keyframe_insert("location")
			self.cam.keyframe_insert("rotation_euler")
			# start/end stasis gaps
			if 0 < i < len(marker_names) - 1 and frames_pause > 0:
				bpy.context.scene.frame_current += frames_pause
				self.cam.keyframe_insert("location")
				self.cam.keyframe_insert("rotation_euler")

			# calculate diff between keyframes
			if i < len(marker_names) - 1:
				this_marker = bpy.context.scene.objects.get(name)
				next_marker = bpy.context.scene.objects.get(marker_names[i + 1])
				loc_distance = (next_marker.location - this_marker.location).length
				rot_distance = (Vector(next_marker.rotation_euler) - Vector(this_marker.rotation_euler)).magnitude * 57.2958
				# smooth frame count over distance to give sense of reaching top speed
				added_loc_frames = int(log(max(1, 10 * frames_per_space * loc_distance), 2))
				added_rot_frames = int(log(max(1, frames_per_degree * rot_distance), 2))
				added_frames = added_loc_frames + added_rot_frames
				# clamp frame count between the two keyframes
				clamped_frames = min(max(min_frames_per_kf, int(added_frames)), max_frames_per_kf)
			else:
				clamped_frames = 0
			bpy.context.scene.frame_current += clamped_frames

		# stretch timeline to fit keyframes
		if bpy.context.scene.frame_current > bpy.context.scene.frame_end:
			bpy.context.scene.frame_end = bpy.context.scene.frame_current + 1

		return None

camanim = CamAnim()

class CamAnimPanel(bpy.types.Panel):
	bl_label = "CamAnim"
	bl_idname = "camera.camanim_panel"
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"
	bl_category = "CamAnim"

	def draw(self, ctx):
		layout = self.layout

		if bpy.context.scene.objects.active == bpy.context.scene.camera or camanim.is_marker(obj_name=bpy.context.scene.objects.active):
			col = layout.column(align=True)

			# update marker data and marker objects
			col.label("Manage markers")
			col.operator("camera.camanim_set_marker", text="Place marker")
			col.operator("camera.camanim_replace_marker", text="Update marker")
			col.operator("camera.camanim_delete_marker", text="Delete marker")

			# update marker data and cam
			col.label("Jump to marker")
			row = col.row(align=True)
			row.operator("camera.camanim_first_marker", text="First")
			row.operator("camera.camanim_last_marker", text="Last")
			if camanim.has_current_marker() == True:
				row = col.row(align=True)
				row.operator("camera.camanim_prev_marker", text="Previous")
				row.operator("camera.camanim_next_marker", text="Next")

			# update marker data and display marker stats
			current_marker_stats = camanim.get_current_marker_details()
			col.operator("camera.camanim_refresh_markers", text="Refresh markers")
			if current_marker_stats['id'] is not None and current_marker_stats['id'] > -1:
				col.label("marker %s: %s" % (current_marker_stats.get('id'), current_marker_stats.get('name')))
			else:
				col.label("(no current marker)")

			# set keyframes
			col.label("Animate camera")
			col.row().operator("camera.camanim_animate", text="Keyframe camera")

		else:
			layout.label("Select Camera or CamAnim Marker...")

		return None

class CamAnimSetMarker(bpy.types.Operator):
	bl_label = "CamAnim Set Marker"
	bl_idname = "camera.camanim_set_marker"
	bl_description = "Place marker along CamAnim path"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(c, ctx):
		return ctx.mode == "OBJECT"

	def execute(self, ctx):
		camanim.place_marker()
		return {'FINISHED'}

class CamAnimReplaceMarker(bpy.types.Operator):
	bl_label = "CamAnim Replace Marker"
	bl_idname = "camera.camanim_replace_marker"
	bl_description = "Replace current marker along CamAnim path"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(c, ctx):
		return ctx.mode == "OBJECT"

	def execute(self, ctx):
		camanim.replace_marker(bpy.context.scene.objects.active)
		return {'FINISHED'}

class CamAnimRemoveMarker(bpy.types.Operator):
	bl_label = "CamAnim Remove Marker"
	bl_idname = "camera.camanim_delete_marker"
	bl_description = "Remove marker from CamAnim path"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(c, ctx):
		return ctx.mode == "OBJECT"

	def execute(self, ctx):
		camanim.remove_marker(bpy.context.scene.objects.active)
		return {'FINISHED'}

class CamAnimRefreshMarkers(bpy.types.Operator):
	bl_label = "CamAnim Refresh Markers"
	bl_idname = "camera.camanim_refresh_markers"
	bl_description = "Jump to current marker along CamAnim path"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(c, ctx):
		return ctx.mode == "OBJECT"

	def execute(self, ctx):
		camanim.jump_marker(0)
		return {'FINISHED'}

class CamAnimFirstMarker(bpy.types.Operator):
	bl_label = "CamAnim First Marker"
	bl_idname = "camera.camanim_first_marker"
	bl_description = "Jump to first marker along CamAnim path"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(c, ctx):
		return ctx.mode == "OBJECT"

	def execute(self, ctx):
		camanim.jump_first_marker()
		return {'FINISHED'}

class CamAnimPrevMarker(bpy.types.Operator):
	bl_label = "CamAnim Previous Marker"
	bl_idname = "camera.camanim_prev_marker"
	bl_description = "Jump to previous marker along CamAnim path"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(c, ctx):
		return ctx.mode == "OBJECT"

	def execute(self, ctx):
		camanim.jump_marker(-1)
		return {'FINISHED'}

class CamAnimNextMarker(bpy.types.Operator):
	bl_label = "CamAnim Next Marker"
	bl_idname = "camera.camanim_next_marker"
	bl_description = "Jump to next marker along CamAnim path"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(c, ctx):
		return ctx.mode == "OBJECT"

	def execute(self, ctx):
		camanim.jump_marker(1)
		return {'FINISHED'}

class CamAnimLastMarker(bpy.types.Operator):
	bl_label = "CamAnim Last Marker"
	bl_idname = "camera.camanim_last_marker"
	bl_description = "Jump to final marker along CamAnim path"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(c, ctx):
		return ctx.mode == "OBJECT"

	def execute(self, ctx):
		camanim.jump_last_marker()
		return {'FINISHED'}

class CamAnimAnimate(bpy.types.Operator):
	bl_label = "CamAnim Animate"
	bl_idname = "camera.camanim_animate"
	bl_description = "Follow and keyframe along CamAnim path"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(c, ctx):
		return ctx.mode == "OBJECT"

	def execute(self, ctx):
		camanim.animate()
		return {'FINISHED'}

def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)

if __name__ == "__main__": register()
