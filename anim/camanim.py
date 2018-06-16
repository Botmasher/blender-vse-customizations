#!/usr/bin/env python
import bpy
from math import log
from mathutils import Vector
from bpy.props import *

## CamAnim
## a Blender Python extension by Joshua R (GitHub user Botmasher)
##
## Ordered marking of camera locations and rotations.
## Automatic camera animation along those markers.
##

# TODO chck that replace_current_markers and remove_current_markers do not break cycling or placement

# TODO adjust all markers, or all markers following currently selected one

# TODO allow for multiple cameras (currently leans on scene camera)
# - place, replace, jump, animate methods now take camera
# - check and pass currently selected camera from operators
# - update markers to store name of camera as well, allowing multiple tracks for multiple cameras

# TODO track markers (incl replace and remove) through something other than name (add uuid property?)

# TODO allow for undoing keyframing along path and resetting it

# NOTE sketch procedure to get all cameras
def get_scene_cameras():
	cams = []
	scene = bpy.context.scene
	for obj in scene.objects:
		if obj.type == 'CAMERA':
			cams.append(obj)
	return cams

print(get_scene_cameras())

# UI props for setting keyframing params
def setup_cam_ui_props():
	Cam = bpy.types.Camera
	cam.camanim_frames_per_space = FloatProperty(name="Location frames", description="How many frames to count between location units", default=3)
	Cam.camanim_frames_per_degree = FloatProperty(name="Rotation frames", description="How many frames to count between rotation degrees", default=0.1)
	Cam.camanim_min_frames_per_kf = IntProperty(name="Min in-betweens", description="Minimum number of frames between keyframes", default=0)
	Cam.camanim_max_frames_per_kf = IntProperty(name="Max in-betweens", description="Maximum number of frames between keyframes", default=9999)
	Cam.camanim_frames_pause = IntProperty(name="Pause frames", description="Length of \"long keyframes\" between movements", default=3)
	return

class CamAnim:
	def __init__(self, marker_name_text="camanim_marker"):
		# internal refs for building and storing markers
		self.sorted_markers = []                  # marker objects store cam loc-rot state
		self.marker_name_text = marker_name_text  # unique string found only in marker names - suffix added on duplication
		self.current_marker = None
		return None

	def find_highest_suffix(self):
		"""Find the highest numeral suffixed to placed marker names"""
		highest_i = 0
		found_marker = False
		for obj in bpy.context.scene.objects:
			if self.is_marker(obj):
				found_marker = True
				split_name = obj.name.split(".")
				marker_i = int(split_name[len(split_name)-1]) if len(split_name) > 0 else 0
				highest_i = marker_i if marker_i > highest_i else highest_i
		if found_marker:
			return highest_i
		else:
			return -1

	def place_marker(self, camera):
		"""Place marker in the scene at current cam loc and rot"""
		# create object
		marker = bpy.data.objects.new(name="", object_data=None)
		bpy.context.scene.objects.link(marker)
		marker.empty_draw_type = "SINGLE_ARROW"

		# orient to camera
		marker.rotation_euler = camera.rotation_euler

		# take over the duplication naming process
		# - append number to base name counting from "1"
		# - look for and increment largest suffix so far
		marker_suffix = self.find_highest_suffix() + 1
		marker.name = "{0}.{1}".format(self.marker_name_text, marker_suffix)
		marker.location = camera.location

		self.current_marker = marker
		return marker

	def replace_marker(self, camera, marker):
		"""Update selected placed marker in the scene to current cam loc and rot"""
		if not self.is_marker(marker): return
		marker.location = camera.location
		marker.rotation_euler = camera.rotation_euler
		self.current_marker = marker
		return marker

	def replace_current_marker(self, camera):
		"""Update current camera marker in the scene to a new cam loc and rot"""
		marker = self.current_marker
		if marker is None: return
		self.replace_marker(camera, marker)
		return marker

	def remove_marker(self, marker=None):
		"""Delete selected placed marker from camanim tracking"""
		if self.is_marker(marker):
			bpy.context.scene.objects.unlink(marker)					# remove from scene
			bpy.data.objects.remove(marker, do_unlink=True)		# delete and verify unlink from whole project
		return marker

	def remove_current_marker(self):
		"""Delete current camer marker from camanim tracking"""
		marker = self.current_marker
		if marker is None: return
		self.remove_marker(marker)
		return marker

	def jump_first_marker(self, camera):
		"""Jump to the first tracked marker"""
		self.sort_markers()
		if len(self.sorted_markers) < 1: return False
		self.snap_cam_to_marker(camera, self.sorted_markers[0])
		return True

	def jump_last_marker(self, camera):
		"""Jump to the final tracked marker"""
		self.sort_markers()
		if len(self.sorted_markers) < 1: return False
		self.snap_cam_to_marker(camera, self.sorted_markers[len(self.sorted_markers) - 1])
		return True

	def jump_marker(self, camera, marker_count):
		"""Jump camera a certain number of markers earlier or later along path"""
		self.sort_markers()
		if len(self.sorted_markers) < 1:
			return 0
		# determine index to jump from
		current_index = 0
		if self.current_marker is not None: 	# else current_index = 0
			for i in range(len(self.sorted_markers)):
				if self.sorted_markers[i] == self.current_marker:
					current_index = i
		# add index to jump to
		jump_i = current_index + marker_count
		# clamp jump to marker list length
		clamped_jump_i = jump_i % (len(self.sorted_markers))
		self.snap_cam_to_marker(camera, self.sorted_markers[clamped_jump_i])
		return clamped_jump_i

	def has_current_marker(self):
		"""Check if there is a stored current marker"""
		if self.current_marker is not None:
			return True
		return False

	def has_any_marker(self):
		"""Check if there are any stored markers"""
		self.sort_markers()
		if len(self.sorted_markers) > 0:
			return True
		return False

	def is_marker(self, obj=None):
		"""Check that an object's name contains the unique marker name base string"""
		if obj is not None and len(obj.name) >= len(self.marker_name_text) and self.marker_name_text == obj.name[0:len(self.marker_name_text)]:
			return True
		return False

	def get_current_marker_details(self):
		"""Find the name and index of the current marker"""
		if self.current_marker:
			return {
				'name': self.current_marker.name,
				'id': self.get_marker_index(self.current_marker)
			}
		return {}

	def get_marker_index(self, marker):
		"""Return the index along path of the current marker"""
		if marker is not None:
			self.sort_markers()
			marker_i = None
			for i in range(len(self.sorted_markers)):
				if self.sorted_markers[i] == marker:
					marker_i = i
			if marker_i is not None: return marker_i
		return None

	def snap_cam_to_marker(self, camera, marker):
		"""Set camera location and rotation to match marker"""
		camera.location = marker.location
		camera.rotation_euler = marker.rotation_euler
		self.current_marker = marker
		return marker

	def sort_markers(self):
		"""Retrieve well-named markers and sort from earliest to latest"""

		marker_indexes = [] 	# store all suffix "indexes" to sort
		markers_by_index = {} 	# marker_index: marker_object pairs for hash retrieval after sort

		# catalog indexes suffixed to all marker objects
		# NOTE relies on proper name formatting on marker creation
		for obj in bpy.context.scene.objects:
			if self.is_marker(obj):
				marker_split_name = obj.name.split(".") 	# "name_base.nnn"
				marker_index = int(marker_split_name[len(marker_split_name)-1])
				markers_by_index[marker_index] = obj
				marker_indexes.append(marker_index)
		# sort split suffixes and grab markers in that order
		marker_indexes.sort()
		markers = [markers_by_index[i] for i in marker_indexes]
		self.sorted_markers = markers
		return markers

	def animate(self, camera, frames_per_space=3, frames_per_degree=0.1, min_frames_per_kf=0, max_frames_per_kf=9999, frames_pause=3):
		"""Use placed markers to set keyframes timed out by frames per loc and rot unit"""
		self.sort_markers()
		bpy.context.scene.frame_current = bpy.context.scene.frame_start + 1

		# keyframe cam along markers
		for i in range(len(self.sorted_markers)):
			marker = self.sorted_markers[i]
			self.snap_cam_to_marker(camera, marker)
			camera.keyframe_insert("location")
			camera.keyframe_insert("rotation_euler")
			# start/end stasis gaps
			if 0 < i < len(self.sorted_markers) - 1 and frames_pause > 0:
				bpy.context.scene.frame_current += frames_pause
				camera.keyframe_insert("location")
				camera.keyframe_insert("rotation_euler")

			# calculate diff between keyframes
			if i < len(self.sorted_markers) - 1:
				this_marker = self.sorted_markers[i]
				next_marker = self.sorted_markers[i + 1]
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

def is_camera(obj=bpy.context.scene.objects.active):
	"""Check if an object has type 'CAMERA'"""
	return ctx.scene.objects.active.type == ctx.scene.camera.type

class CamAnimPanel(bpy.types.Panel):
	bl_label = "CamAnim"
	bl_idname = "camera.camanim_panel"
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"
	bl_category = "CamAnim"

	def draw(self, ctx):
		setup_cam_ui_props()

		layout = self.layout

		if ctx.scene.objects.active == ctx.scene.camera or camanim.is_marker(obj=ctx.scene.objects.active):
			col = layout.column(align=True)

			# update marker data and marker objects
			col.label("Manage markers")
			col.operator("camera.camanim_set_marker", text="Place marker")
			col.operator("camera.camanim_replace_current_marker", text="Update marker")
			col.operator("camera.camanim_remove_current_marker", text="Delete marker")

			# update camera loc-rot to match marker loc-rot
			if camanim.has_any_marker():
				col.label("Jump to marker")
				row = col.row(align=True)
				row.operator("camera.camanim_first_marker", text="First")
				row.operator("camera.camanim_last_marker", text="Last")
				if camanim.has_current_marker():
					row = col.row(align=True)
					row.operator("camera.camanim_prev_marker", text="Previous")
					row.operator("camera.camanim_next_marker", text="Next")

			# update marker data and display marker stats
			current_marker_stats = camanim.get_current_marker_details()
			col.operator("camera.camanim_refresh_markers", text="Refresh markers")
			if current_marker_stats and current_marker_stats['id'] is not None and current_marker_stats['id'] > -1:
				col.label("marker %s: %s" % (current_marker_stats.get('id'), current_marker_stats.get('name')))
			else:
				col.label("(no current marker)")

			# set keyframes
			if camanim.has_any_marker():
				col.label("Animate camera")
				cam = ctx.scene.camera.data
				col.row().prop(cam, "camanim_frames_per_space")
				col.row().prop(cam, "camanim_frames_per_degree")
				col.row().prop(cam, "camanim_min_frames_per_kf")
				col.row().prop(cam, "camanim_max_frames_per_kf")
				col.row().prop(cam, "camanim_frames_pause")
				col.row().operator("camera.camanim_animate", text="Keyframe camera")

		# invalid selection
		else:
			layout.label("Select Scene Camera...")

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
		obj = ctx.scene.objects.active
		if is_camera():
			camanim.place_marker(obj)
		return {'FINISHED'}

class CamAnimReplaceMarker(bpy.types.Operator):
	bl_label = "CamAnim Replace Marker"
	bl_idname = "camera.camanim_replace_current_marker"
	bl_description = "Replace current marker along CamAnim path"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(c, ctx):
		return ctx.mode == "OBJECT"

	def execute(self, ctx):
		camanim.replace_current_marker(bpy.context.scene.camera)
		return {'FINISHED'}

class CamAnimRemoveMarker(bpy.types.Operator):
	bl_label = "CamAnim Remove Marker"
	bl_idname = "camera.camanim_remove_current_marker"
	bl_description = "Remove marker from CamAnim path"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(c, ctx):
		return ctx.mode == "OBJECT"

	def execute(self, ctx):
		camanim.remove_current_marker(bpy.context.scene.objects.active)
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
		camanim.jump_marker(bpy.context.scene.camera, 0)
		return {'FINISHED'}

class CamAnimFirstMarker(bpy.types.Operator):
	bl_label = "CamAnim First Marker"
	bl_idname = "camera.camanim_first_marker"
	bl_description = "Jump to first marker along CamAnim path"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(c, ctx):
		return ctx.mode == "OBJECT"

	def draw(self, ctx):
		self.layout.row().label("Jumping to first available marker")

	def execute(self, ctx):
		camanim.jump_first_marker(bpy.context.scene.camera)
		return {'FINISHED'}

class CamAnimPrevMarker(bpy.types.Operator):
	bl_label = "CamAnim Previous Marker"
	bl_idname = "camera.camanim_prev_marker"
	bl_description = "Jump to previous marker along CamAnim path"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(c, ctx):
		return ctx.mode == "OBJECT"

	def draw(self, ctx):
		self.layout.row().label("Jumping to previous available marker")

	def execute(self, ctx):
		camanim.jump_marker(bpy.context.scene.camera, -1)
		return {'FINISHED'}

class CamAnimNextMarker(bpy.types.Operator):
	bl_label = "CamAnim Next Marker"
	bl_idname = "camera.camanim_next_marker"
	bl_description = "Jump to next marker along CamAnim path"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(c, ctx):
		return ctx.mode == "OBJECT"

	def draw(self, ctx):
		self.layout.row().label("Jumping to next available marker")

	def execute(self, ctx):
		camanim.jump_marker(bpy.context.scene.camera, 1)
		return {'FINISHED'}

class CamAnimLastMarker(bpy.types.Operator):
	bl_label = "CamAnim Last Marker"
	bl_idname = "camera.camanim_last_marker"
	bl_description = "Jump to final marker along CamAnim path"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(c, ctx):
		return ctx.mode == "OBJECT"

	def draw(self, ctx):
		self.layout.row().label("Jumping to last available marker")

	def execute(self, ctx):
		camanim.jump_last_marker(bpy.context.scene.camera)
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
		camanim.animate(bpy.context.scene.camera)
		return {'FINISHED'}

def register():
	bpy.utils.register_class(CamAnimPanel)
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_class(CamAnimPanel)
	bpy.utils.unregister_module(__name__)

if __name__ == "__main__": register()
