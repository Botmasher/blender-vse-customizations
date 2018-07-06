import bpy

#3 Align Object in Camera Viewport
##
## Blender Python script by Josh R (GitHub user Botmasher)

# Base implementation
# - determine point at center of camera x,y
# - determine focal point for camera z
# - place object at point
# - scale object to fit within frustum
#   - account for all points (or just normals) in mesh
#

def find_center(cam, offset=[0,0,0]):
    if cam.type != 'CAMERA': return
    point = [cam.location[x] + offset[x] for x in range(cam.location)]
    return point

def find_edges(cam):
    r = bpy.context.scene.render.resolution_x
    b = bpy.context.scene.render.resolution_y
    trbl = [0, r, b, 0]
    return trbl

def translatable(*objs):
    """Determine if the object exists and is movable"""
    for obj in objs:
        if not obj or not obj.location:
            return False
    return True

# simplified - imagine camera angle perpendicular to x-y plane
def center_obj_in_straighton_cam(obj, cam, scale):
    if not translatable(obj, cam): return
    obj.location = cam.location
    obj.scale = scale
    return obj

## TODO:
##  iterate on center_obj() to work this way:
##  1. locate object on camera
##  2. add object constraint to rotate with camera
##  3. determine line of sight (LOS) from camera
##  4. constrain object along that LOS
##  5. scale object along LOS
##  6. remove constraints and LOS
##  FUTURE: determine when object scaled to fit within frustum
##      - requires point detection?
##      - only works with

# Override for object resize to pivot point
# https://blenderartists.org/t/how-to-bpy-ops-transform-resize-in-edit-mode-using-pivot/560381/2
def override(area_type, region_type):
    for area in bpy.context.screen.areas:
        if area.type == area_type:
            for region in area.regions:
                if region.type == region_type:
                    override = {'area': area, 'region': region}
                    return override
    #error message if the area or region wasn't found
    raise RuntimeError("Wasn't able to find " + region_type + " in area " + area_type + ". Make sure it's open while executing script.")

#we need to override the context of our operator
override = override('VIEW_3D', 'WINDOW')

def center_obj(obj=bpy.context.scene.objects.active, cam=bpy.context.scene.camera):
    if not translatable(obj, cam): return
    # method - create empty and scale
    # https://blender.stackexchange.com/questions/95370/positioning-object-to-the-center-of-camera-view-in-3d-scene
    empty = bpy.data.objects.new("empty-cam-center", None)
    bpy.context.scene.objects.link(empty)
    for o in bpy.context.scene.objects: o.select = False
    bpy.context.scene.objects.active = empty
    empty.location = obj.location
    empty.empty_draw_type = 'ARROWS'
    copy_rot = empty.constraints.new('COPY_ROTATION')
    copy_rot.target = cam
    bpy.context.scene.cursor_location = cam.location
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            area.spaces[0].pivot_point = 'CURSOR'
    empty.select = True
    bpy.ops.transform.resize(override, value=(0.0, 0.0, 0.0), constraint_axis=(False, False, False), constraint_orientation='GLOBAL')
    obj.location = empty.location
    obj.rotation_euler = empty.rotation_euler

    #obj.location = find_center(cam)
    return obj

## test call
center_obj()

# /!\ After small trials - any way to avoid detecting points and just use camera data? /!\

# Work through detecting object in camera again:
# https://blender.stackexchange.com/questions/45146/how-to-find-all-objects-in-the-cameras-view-with-python/45324
