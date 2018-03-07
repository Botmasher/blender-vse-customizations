import bpy
from mathutils import Vector

# TODO track markers (incl replace and remove) through something other than name (add uuid property?)
# TODO adjust all markers, or all markers following currently selected one
# TODO place marker empty through mesh data + object data -> link to scene

class CamAnim:
	def __init__(self, cam=bpy.context.scene.camera, marker_name_base_text="camanim_marker", frames_per_space=2, frames_per_degree=0.2, frames_pause = 3):
		self.cam = cam
		self.marker_name_base_text = marker_name_base_text
		self.frames_per_space = frames_per_space
		self.frames_per_degree = frames_per_degree
		self.frames_pause = frames_pause 		# number of frames to wait between movements (exclusive; used for cutting strips btwn motion blur and other multi fx)
		self.marker_names = None
		self.current_marker_name = None
		return None

	def set_frames_per_space(self, frames_per_space):
		"""Set frames per space unit while transitioning between keyframe locs"""
		self.frames_per_space = frames_per_space
		return self.frames_per_space

	def set_frames_per_degree(self, frames_per_degree):
		"""Set frames per degree while transitioning between keyframe rots"""
		self.frames_per_degree = frames_per_degree
		return self.frames_per_degree

	def place_marker(self):
		"""Place marker in the scene at current cam loc and rot"""
		bpy.ops.object.empty_add(type="SINGLE_ARROW")
		marker = bpy.context.scene.objects.active
		marker.name = self.marker_name_base_text
		marker.location = self.cam.location
		marker.rotation_euler = self.cam.rotation_euler
		return None

	def replace_marker(self, marker):
		"""Update selected currently placed marker in the scene to current cam loc and rot"""
		if self.is_marker(marker.name):
			marker.location = self.cam.location
			marker.rotation_euler = self.cam.rotation_euler
		return None

	def remove_marker(self, marker):
		"""Delete selected currently placed marker from camanim tracking"""
		if self.is_marker(marker.name):
			bpy.context.scene.objects.unlink(marker)					# remove from scene
			bpy.data.objects.remove(marker, do_unlink=True)		# delete and verify unlink from whole project
		return None

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
		marker_names = self.sort_markers()
		if self.current_marker_name is None:
			self.current_marker_name = marker_names[0]
		try:
			marker_i = int(self.current_marker_name.split(".")[1])
		except:
			marker_i = len(marker_names)
		jump_i = marker_i + marker_count
		# cycle forward or backward through markers
		if jump_i > len(marker_names) or jump_i < 0:
			jump_i = 0
		else:
			jump_i -= 1		# generated names start from 001 and len is 1 over index
		self.snap_cam_to_marker(marker_names[jump_i])
		return None

	def is_marker(self, obj_name=None, obj=None):
		"""Check if named object is a CamAnim marker"""
		if obj is not None and self.marker_name_base_text in obj.name:
			return True
		elif obj_name is not None and self.marker_name_base_text in obj_name:
			return True
		else:
			return False

	def has_current_marker(self):
		"""Check if there is a stored current marker"""
		if self.current_marker_name is not None:
			return True
		return False

	def get_current_marker_details(self):
		"""Find the name and index of the current marker"""
		return {
			'name': self.current_marker_name,
			'id': self.get_marker_index(self.current_marker_name)
		}

	def get_marker_index(self, marker_name):
		"""Return the index along path of the current marker"""
		if marker_name is not None:
			sorted_markers = self.sort_markers()
			marker_i = None
			for i in range(len(sorted_markers)):
				if sorted_markers[i] == marker_name:
					marker_i = i
			if marker_i is not None: return marker_i
		return None

	def snap_cam_to_marker(self, marker_name):
		"""Set camera location and rotation to match marker"""
		marker = bpy.context.scene.objects[marker_name]
		self.cam.location = marker.location
		self.cam.rotation_euler = marker.rotation_euler
		self.current_marker_name = marker_name
		return marker

	def sort_markers(self, do_resort=True):
		"""Retrieve well-named markers and sort from earliest to latest
		
		Caution when proceeding without resorting as markers unsync easily! (e.g. user deletes marker)
		"""
		if do_resort == True or self.marker_names is None:
			self.marker_names = [o.name for o in bpy.context.scene.objects if self.is_marker(o.name)]
			self.marker_names.sort()
			# markers count from .001 - place latest marker (unappended) at the end
			self.marker_names.append(self.marker_names.pop(0))
		return self.marker_names

	def animate(self):
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
			if self.frames_pause > 0:
				bpy.context.scene.frame_current += self.frames_pause
				self.cam.keyframe_insert("location")
				self.cam.keyframe_insert("rotation_euler")
			
			# calculate diff between keyframes
			if i < len(marker_names) - 1:
				this_marker = bpy.context.scene.objects.get(name)
				next_marker = bpy.context.scene.objects.get(marker_names[i + 1])
				distance = (next_marker.location - this_marker.location).length
				added_frames = int(self.frames_per_space * distance)
				# TODO frame counts increase logarithmically for sense of nearing top speed
				# TODO factor in rotation (e.g. cam position stationary but rotates)
			else:
				added_frames = 0
			bpy.context.scene.frame_current += added_frames

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
		
		if bpy.context.scene.objects.active == bpy.context.scene.camera or camanim.is_marker(obj_name=bpy.context.scene.objects.active.name):
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
