import bpy

# TODO adjust all markers / all markers following currently selected one
# TODO place_marker empty through mesh data + object data -> link to scene
# TODO track markers (incl replace and remove) through something other than name (add uuid property?)
# TODO better way to store and retrieve markers (instance list breaks on undo or reload)

class CamAnim:
	def __init__(self, cam=bpy.context.scene.camera, marker_name="camanim_marker", frames_per_space=1, frames_per_degree=0.2, frames_pause = 3):
		self.cam = cam
		self.marker_name = marker_name
		self.frames_per_space = frames_per_space
		self.frames_per_degree = frames_per_degree
		self.frames_pause = frames_pause 		# number of frames to wait between movements (exclusive; used for cutting strips btwn motion blur and other multi fx)
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
		marker.name = self.marker_name
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

	def animate(self):
		"""
		TODO Use array of markers to set keyframes timed out by frames per loc and rot unit
		"""
		# int(frames)! -- remember to round result of frames per space or per degree
		# names count from .001 to unappended (LATEST one added)
		marker_names = [o.name for o in bpy.context.scene.objects if o.name.split(".")[0] == self.marker_name]
		marker_names.sort()
		# place latest marker at the end
		marker_names.append(marker_names.pop(0))
		bpy.context.scene.frame_current = bpy.context.scene.frame_start + 1
		for name in marker_names:
			self.cam.location = bpy.context.scene.objects[name].location
			self.cam.rotation_euler = bpy.context.scene.objects[name].rotation_euler
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
		# 
		# TODO check that selected is a marker
		self.layout.row().operator("camera.camanim_set_marker", text="Place marker")
		self.layout.row().operator("camera.camanim_replace_marker", text="Update marker")
		self.layout.row().operator("camera.camanim_delete_marker", text="Delete marker")
		self.layout.row().operator("camera.camanim_animate", text="Keyframe cam path")

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