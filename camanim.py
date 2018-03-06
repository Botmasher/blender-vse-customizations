import bpy

# TODO adjust all markers / all markers following currently selected one
# TODO place_marker empty through mesh data + object data -> link to scene
# TODO track markers (incl replace and remove) through something other than name (add uuid property?)
# TODO better way to store and retrieve markers (instance list breaks on undo or reload)

class CamAnim:
	def __init__(self, cam=bpy.context.scene.camera, marker_name_base_text="camanim_marker", frames_per_space=1, frames_per_degree=0.2, frames_pause = 3):
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
		print("Placed marker and added it to path markers array!")
		bpy.ops.object.empty_add(type="SINGLE_ARROW")
		marker = bpy.context.scene.objects.active
		marker.name = self.marker_name_base_text
		marker.location = self.cam.location
		marker.rotation_euler = self.cam.rotation_euler
		#self.path_markers.append(marker)
		return None

	def replace_marker(self, marker=bpy.context.scene.objects.active):
		"""Update selected currently placed marker in the scene to current cam loc and rot"""
		print("Updated existing marker!")
		if marker.name.split(".")[0] != self.marker_name: return None
		marker.location = self.cam.location
		marker.rotation_euler = self.cam.rotation_euler
		return None

	def remove_marker(self, marker=bpy.context.scene.objects.active):
		"""Delete selected currently placed marker from camanim tracking"""
		print("Deleted existing marker!")
		if marker.name.split(".")[0] != self.marker_name: return None
		bpy.context.scene.objects.unlink(marker)					# remove from scene
		bpy.data.objects.remove(marker, do_unlink=True)		# delete and verify unlink from whole project
		return None

	def jump_marker(self, marker_count):
		"""Jump camera count markers earlier or later along path"""
		marker_names = self.sort_markers()
		if self.current_marker_name is None:
			self.current_marker_name = marker_names[0]
		print(self.current_marker_name)
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
		self.current_marker_name = marker_names[jump_i]
		self.snap_cam_to_marker(self.current_marker_name)
		return None

	def is_marker(self, obj_name=bpy.context.scene.objects.active.name, obj=None):
		"""Check if named object is a CamAnim marker"""
		if obj is not None and self.marker_name_base_text in obj.name:
			return True
		elif self.marker_name_base_text in obj_name:
			return True
		else:
			return False

	def snap_cam_to_marker(self, marker_name):
		"""Set camera location and rotation to match marker"""
		marker = bpy.context.scene.objects[marker_name]
		self.cam.location = marker.location
		self.cam.rotation_euler = marker.rotation_euler
		return marker

	def sort_markers(self, do_resort=True):
		"""Retrieve well-named markers and sort from earliest to latest"""
		if do_resort == True or self.marker_names is None:
			# names count from .001 to unappended (LATEST one added)
			self.marker_names = [o.name for o in bpy.context.scene.objects if o.name.split(".")[0] == self.marker_name_base_text]
			self.marker_names.sort()
			# place latest marker at the end
			self.marker_names.append(self.marker_names.pop(0))
		return self.marker_names

	def animate(self):
		"""Use placed markers to set keyframes timed out by frames per loc and rot unit"""
		# int(frames)! -- remember to round result of frames per space or per degree
		marker_names = self.sort_markers()
		bpy.context.scene.frame_current = bpy.context.scene.frame_start + 1
		for name in marker_names:
			self.snap_cam_to_marker(name)
			self.cam.keyframe_insert("location")
			self.cam.keyframe_insert("rotation_euler")
			if self.frames_pause > 0:
				bpy.context.scene.frame_current += self.frames_pause
				self.cam.keyframe_insert("location")
				self.cam.keyframe_insert("rotation_euler")
			bpy.context.scene.frame_current += self.frames_per_space * 10  	# TODO calc bu btwn kfs
		if bpy.context.scene.frame_current > bpy.context.scene.frame_end:
			bpy.context.scene.frame_end = bpy.context.scene.frame_current + 1
		return None

camanim = CamAnim()

class CamAnimPanel(bpy.types.Panel):
	bl_label = "CamAnim Panel"
	bl_idname = "camera.camanim_panel"
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"
	bl_category = "CamAnim"

	def draw(self, ctx):
		# TODO check that selected is cam or marker
		if bpy.context.scene.objects.active == bpy.context.scene.camera or camanim.is_marker():
			self.layout.row().operator("camera.camanim_set_marker", text="Place marker")
			self.layout.row().operator("camera.camanim_replace_marker", text="Update marker")
			self.layout.row().operator("camera.camanim_delete_marker", text="Delete marker")
			self.layout.row().operator("camera.camanim_animate", text="Keyframe cam path")
			row = self.layout.row()
			row.operator("camera.camanim_prev_marker", text="Previous")
			row.operator("camera.camanim_next_marker", text="Next")

class CamAnimSetMarker(bpy.types.Operator):
	bl_label = "CamAnim Set Marker"
	bl_idname = "camera.camanim_set_marker"
	bl_description = "Place marker along CamAnim path"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(c, ctx):
		return ctx.mode == "OBJECT"

	def execute(self, ctx):
		# run camanim place_marker with current camera loc and rot
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
		# run camanim replace marker with current camera loc and rot
		camanim.replace_marker()
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
		# get active object and check that it is a camanim marker
		camanim.remove_marker()
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
		# get active object and check that it is a camanim marker
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
		# get active object and check that it is a camanim marker
		camanim.jump_marker(1)
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