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

def center_obj(obj):
    if not obj or not obj.location: return
    cam = bpy.context.scene.camera

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
    empty.scale = (0, 0, 0)     # constrain along Camera Z
    obj.location = empty.location
    obj.rotation_euler = empty.rotation_euler

    #obj.location = find_center(cam)
    return obj

## test call
center_obj(bpy.context.scene.objects.active)

# /!\ After small trials - any way to avoid detecting points and just use camera data? /!\

# Work through detecting object in camera again:
# https://blender.stackexchange.com/questions/45146/how-to-find-all-objects-in-the-cameras-view-with-python/45324
