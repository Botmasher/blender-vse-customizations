import bpy

class CamAnim:
	def __init__(self, cam, frames_per_space=1, frames_per_degree=0.2):
		self.cam = cam 					# reference to the animated cam
		self.path_markers = [] 	# list of markers to be set for and followed by animated cam
		self.frames_per_space = frames_per_space
		self.frames_per_degree = frames_per_degree
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
		"""
		TODO place marker in the scene at current cam loc and rot
		"""
		# set empty arrow for marker to cam loc and rot
		# set object constraints on empty so it cannot be moved or 
		# prevent empty name change (if using name to track)
		# push marker onto to camanim array at id position (plus dict assoc with bl_rna, object and list id?)
		print("Placed marker and added it to path markers array!")
		return None

	def replace_marker(self, id):
		"""
		TODO Update selected currently placed marker in the scene to current cam loc and rot
		"""
		print("Updated existing marker!")
		return None

	def remove_marker(self, id):
		"""
		TODO Delete selected currently placed marker from camanim tracking
		"""
		print("Deleted existing marker!")
		return None

	def animate(self, id):
		"""
		TODO Use array of markers to set keyframes timed out by frames per loc and rot unit
		"""
		# int(frames)! -- remember to round result of frames per space or per degree
		return None

camanim = CamAnim(bpy.context.scene.camera)

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
		self.layout.row().operator("camera.camanim_replace_marker", text="Place marker")
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
		camanim.replace_marker(None)
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
		camanim.remove_marker(None)
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
		return {'FINISHED'}

def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)

if __name__ == "__main__": register()