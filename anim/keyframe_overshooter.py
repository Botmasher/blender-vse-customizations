import bpy

## Keyframe Overshooter
## script by Joshua R (GitHub user Botmasher)
##
## Overshoot i% over n frames before settling into a final animated value.
##

# TODO add visual to dopesheet showing which interpolation used by selected kfs

class KeyframeOvershooter():
	def __init__(self):
		return

	def is_animated(self, obj):
		if not obj or not obj.animation_data or not obj.animation_data.action:
			print("No keyframes found - select an animated object")
			return False
		return True

	def get_selected_kfs(self, obj=bpy.context.scene.objects.active):
		if not self.is_animated(obj):
			return
		kfs = []
		for curve in obj.animation_data.action.fcurves:
			for kp in curve.keyframe_points:
				if kp.select_control_points:
					kfs.append(kp)
		return kfs

	def set_kf_attr(self, kf, attr_name, attr_value):
		if not self.is_animated(obj):
			return
		try:
			self.setattr(kf, attr_name, attr_value)
		except:
			raise Exception("Failed trying to set keyframe {0} attribute {1} to {2}".format(kf, attr_name, attr_value))
		return kf

	def interpolate_selected_kfs(self, obj, interpolation_type='BACK'):
		"""Set the interpolation for all selected keyframes on selected object"""
		# NOTE: first select kfs in dopesheet or graph or select them programmatically
		keyframes = self.get_selected_kfs(obj)
		for kf in keyframes:
			self.set_kf_attr(kf, 'interpolation', interpolation_type)
		return keyframes

	def is_number(self, value):
		"""Check if a value is of a number type"""
		value_type = type(value)
		return (value_type is int or value_type is float)

	def is_number_list(self, v):
		"""Check if a value is a list containing only numbers"""
		for value in v:
			value_type = type(value)
			if value_type is not int and value_type is not float:
				return False
		return True

	def is_transform_list(self, v):
		"""Check if a value is a location/rotation/scale transform list"""
		if len(v) == 3 and self.is_number_list(v):
			return True
		return False

	def test_compare_overshoot_methods(self, v_source, v_target):
		# sample inputs given overshoot_percent=1.1
		# (target - source) * overshoot_percent
		# [0, 0, 0] 		-> 		[1, 1, 1]
		# 	result:		[1.1, 1.1, 1.1]
		# 	expected: [1.1, 1.1, 1.1]
		# [-1, 0, 2] 		->		[1, -1, 0]
		# 	result:		[2.2, -1.1, -2.2]
		# 	expected: [1.2, -1.1, -0.2]
		# [-1, -1, -1] 	-> 		[1, 1, 1]
		# 	result: 	[2.2, 2.2, 2.2]
		# 	expected: [1.2, 1.2, 1.2]
		# [1, 1, 1] 		-> 		[1, 1, 1]
		# 	result: 	[0, 0, 0]
		# 	expected: [0, 0, 0]
		# [0, -15, 0] 	-> 		[20, 15, 20]
		# 	result: 	[22, 33, 22]
		# 	expected: [22, 18, 22]
		# [1, 1, 0] 		-> 		[-20, -15, -20]
		# 	result: 	[-23.1, -17.6, -22]
		# 	expected: [-22.1, -16.6, -22]
		# target + ((target - source) * (overshoot_percent - 1))
		methods = [
			lambda x,y: [(x[i] - y[i]) * overshoot_percent for i in range(len(x))],
			lambda x,y: [x[i] + (x[i] - y[i]) * (overshoot_percent - 1) for i in range(len(x))]
		]
		results = [method(v_source, v_target) for method in methods]
		return results

	# TODO account for speed (distance/frames)
	def calculate_distanced_overshoot(self, source_v, target_v, overshoot_percent):
		"""Build a new vector with calculated overshoots based on source-target deltas"""
		if not self.is_transform_list(source_v) or not self.is_transform_list(target_v) or not self.is_number(overshoot_percent):
			print ("Unable to compare transforms and calculate overshoot")
			return
		v = []
		for i in range(len(source_v)):
			overshoot = (target_v[i] - source_v[i]) * (overshoot_percent - 1)
			target_value = target_v[i] + overshoot
			v.append(target_value)
		return v

	def calculate_plain_overshoot(self, target_v, overshoot_percent):
		"""Build a new vector with calculated overshoots beyond a target value"""
		if not self.is_transform_list(target_v) or not self.is_number(overshoot_percent):
			return
		return [value * overshoot_percent for value in target_v]

	def set_kf(self, obj, attr, value, frame):
		"""Insert a keyframe on an object attribute"""
		bpy.context.scene.frame_current = frame
		obj.keyframe_insert(attr)
		setattr(obj, attr, value)
		obj.keyframe_insert(attr)

	def overshoot_transform(self, obj, attr, target_value, frames=5, overshoot_frames=2, overshoot_percent=1.1):
		"""Give current selected keyframes a dynamic interpolation"""
		if not hasattr(obj, attr):
			return

		# frames to kf
		scene = bpy.context.scene
		start_frame = scene.frame_current
		overshoot_frame = start_frame + frames
		final_frame = overshoot_frame + overshoot_frames

		# initial kf
		start_value = getattr(obj, attr)
		print(start_value)
		self.set_kf(obj, attr, start_value, start_frame)

		# overshoot kf
		overshoot_value = self.calculate_distanced_overshoot(start_value, target_value, overshoot_percent)
		self.set_kf(obj, attr, overshoot_value, overshoot_frame)

		# target kf
		self.set_kf(obj, attr, target_value, final_frame)

		# reset playhead
		bpy.context.scene.frame_current = start_frame

		return obj.animation_data.action.fcurves

kfer = KeyframeOvershooter()

# ui and props

# TODO set frames defaults based on render settings
# class KfOvershootProperties(bpy.types.PropertyGroup)
# 	attr = EnumProperty(
#         name = "Attribute",
#         description = "Transform axis for rotation effects",
#         items = [
#             ("location", "Location", "Keyframe the object's location"),
#             ("rotation_euler", "Rotation", "Keyframe the object's rotation"),
#             ("scale", "Scale", "Keyframe the object's scale")
#         ]
#     )
# 	#attr_raw = StringProperty(name="Raw attribute", description="Name of attribute to keyframe", default="")
# 	target = FloatVectorProperty(name="Target", description="Final value for object transform to settle on", size=3)
# 	percent = FloatProperty(name="Multiplier", description="Target value multiplier for the overshoot", default=1.1)
# 	pre_frames = IntProperty(name="Frames", description="Frames before overshoot value", min=1, default=5)
# 	post_frames = IntProperty(name="Overshoot frames", description="Frames after overshoot value", min=1, default=2)
# 	use_distance = BoolProperty(name="Use distance", description="Factor in distance when calculaing overshoot", default=False)

kf_overshoot_props = {
	'attr': EnumProperty(
        name = "Attribute",
        description = "Transform axis for rotation effects",
        items = [
            ("location", "Location", "Keyframe the object's location"),
            ("rotation_euler", "Rotation", "Keyframe the object's rotation"),
            ("scale", "Scale", "Keyframe the object's scale")
        ]
    ),
	'target': FloatVectorProperty(name="Target", description="Final value for object transform to settle on", size=3),
	'percent': FloatProperty(name="Multiplier", description="Target value multiplier for the overshoot", default=1.1),
	'pre_frames': IntProperty(name="Frames", description="Frames before overshoot value", min=1, default=5),
	'post_frames': IntProperty(name="Overshoot frames", description="Frames after overshoot value", min=1, default=2),
	'use_distance': BoolProperty(name="Use distance", description="Factor in distance when calculaing overshoot", default=False)
}

# TODO set these, iterate through keys when setting props
props_src_type = bpy.types.Scene
for prop_name, prop_value in kf_overshoot_props.items():
	setattr(props_src_type, prop_name, prop_value)

# 	- or consider comments on property() get/set below...
# class C(object):
#     def getx(self): return self._x
#     def setx(self, value): self._x = value
#     def delx(self): del self._x
#     x = property(getx, setx, delx, "I'm the 'x' property.")
# Decorators make defining new properties or modifying existing ones easy:
# class C(object):
#     @property
#     def x(self):
#         "I am the 'x' property."
#         return self._x
#     @x.setter
#     def x(self, value):
#         self._x = value
#     @x.deleter
#     def x(self):
#         del self._x

def is_overshoot_data(props_dict):
	if type(props_dict) is not dict:
		return False
	for prop_name in kf_overshoot_props.keys():
		if prop_name not in overshoot_props:
			return False
	for prop_name in props_dict:
		if prop_name not in kf_overshoot_props:
			return False
	return True

def handle_overshoot(overshoot_props={}):
	if not is_overshoot_data(overshoot_props):
		return
	res = kfer.overshoot_transform(
		obj,
		overshoot_props['attr'],
		overshoot_props['end'],
		frames=overshoot_props['frames'],
		overshoot_frames=overshoot_props['overshoot_frames']
	)
	return res

class KfOvershootOperator(bpy.types.Operator):
    bl_label = "Keyframe Overshooter"
    bl_idname = "object.keyframe_overshooter"
    bl_description = "Keyframe transform past target before settling into final value"

    def execute(self, context):
		scene = context.scene
		overshoot_props = {prop_name: getattr(scene, prop_name) for prop_name in kf_overshoot_props.keys()}
		# TODO wrap method call to pass in just dict and obj
		handle_overshoot(overshoot_props)
        return {'FINISHED'}

class KfOvershootPanel(bpy.types.Panel):
    bl_label = "Keyframe Overshooter Tools"
    bl_idname = "object.keyframe_overshoot_panel"
    bl_category = "Keyframe Overshooter"
    bl_context = "objectmode"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"

    def draw(self, context):
		layout = self.layout
		for prop_name in kf_overshoot_props.keys():
			layout.row().prop(context.scene, prop_name)
        layout.row().operator("object.keyframe_overshooter", text="Animate")

def register():
	bpy.utils.register_class(KfOverhootProperties)
	bpy.types.Scene.keyframe_overshoot_data = bpy.props.PointerProperty(type=TextFxProperties)
    bpy.utils.register_class(KfOverhootOperator)
    bpy.utils.register_class(KfOverhootPanel)

def unregister():
    bpy.utils.unregister_class(KfOvershootPanel)
	try:
		delete(bpy.types.keyframe_overshoot_data)
	except:
		print("Unable to remove keyframe_overshoot_data from bpy.types.Scene")
    bpy.utils.unregister_class(KfOvershootOperator)
	bpy.utils.unregister_class(KfOverhootProperties)

if __name__ == '__main__':
	register()
	#unregister()
