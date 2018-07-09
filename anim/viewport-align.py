import bpy
from mathutils import Matrix
import bpy_extras

#3 Align Object in Camera Viewport
##
## Blender Python script by Josh R (GitHub user Botmasher)

# Base implementation
# - determine point at center of camera x,y
# - determine focal point for camera z
# - place object at point
# - scale object to fit within frustum
#   - account for all points (or just normals) in mesh

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

## TODO:
##  iterate on center_obj() to work this way:
##  FUTURE: determine when object scaled to fit within view
##      - requires point detection?
##      - allow adjusting scale within view (like calculate view size * 0.5)

## newer iteration on center align
def center_in_cam_view(obj=bpy.context.object, cam=bpy.context.scene.camera, distance=0.0, snap=False):
    if not translatable(obj, cam): return

    # move and rotate obj to cam
    obj.location = cam.location
    obj.rotation_euler = cam.rotation_euler
    v = (0.0, 0.0, -distance)

    # local move away cam using matrix translation
    # https://blender.stackexchange.com/questions/82265/move-object-along-local-axis-with-python-api
    if snap:
        # parent to camera
        obj.parent = cam
        obj.matrix_basis = Matrix.Translation(v)
    else:
        obj.matrix_basis *= Matrix.Translation(v)

    return obj

## test call
#center_in_cam_view(distance=5.0)

# Find object edges vs camera view edges

def get_frustum_loc(point, cam=bpy.context.scene.camera, scene=bpy.context.scene):
    """Determine location of a point within camera's rendered frame"""
    if not point or not cam or not scene: return
    # scene to use for frame size
    # Camera object
    # World space location (mathutils.Vector)
    uv_loc = bpy_extras.object_utils.world_to_camera_view(scene, cam, point)
    # returns a Vector magnitude 3 with valid cam positions between 0<=uv_loc<=1
    #   - values for index 0,1 greater than 1 are above top-right of frame
    #   - values at index 2 less than 0 are behind camera
    #print(uv_loc)
    return uv_loc

def is_frustum_loc(point, cam=bpy.context.scene.camera, scene=bpy.context.scene):
    """Check if a point falls within camera's rendered frame"""
    if not point or not cam or not scene: return
    uv_loc = bpy_extras.object_utils.world_to_camera_view(scene, cam, point)
    return (0.0 <= uv_loc[0] <= 1.0 and 0.0 <= uv_loc[1] <= 1.0 and uv_loc[2] >= 0.0)

def fit_to_frustum(obj, cam=bpy.context.scene.camera, distance=5.0, distort=False):
    if not hasattr(obj.data, 'vertices'): return    # no mesh to check
    vertex_extremes = [0.0, 0.0, 0.0]
    for vertex in obj.data.vertices:
        uv = get_frustum_loc(obj.matrix_world * vertex.co, cam=cam)
        print(uv)
        if uv[0] > 1 or uv[0] < 0:
            if abs(uv[0]) > abs(vertex_extremes[0]):
                vertex_extremes[0] = uv[0]
        if uv[1] > 1 or uv[0] < 0:
            if abs(uv[1]) > abs(vertex_extremes[1]):
                vertex_extremes[1] = uv[1]
        if uv[2] < 0 and abs(uv[2]) > abs(vertex_extremes[2]):
            vertex_extremes[2] = uv[2]
    for extreme in vertex_extremes:
        # TODO use highest negative w to move object in front of cam and recurse for u,w
        # /!\ currently just trusts that object is in front of cam /!\
        if vertex_extremes[2] < 0.0 :
           # move along Z
           # obj.location += (uv[2] - 1.0 - distance)
           pass
        if abs(vertex_extremes[0]) > 1.0:
            if abs(vertex_extremes[1]) > 1.0 and abs(vertex_extremes[1] > vertex_extremes[0]):
                # scale along y
                pass
            # scale along x
            pass
    print (vertex_extremes)
    return vertex_extremes

fit_to_frustum(bpy.context.scene.objects.active)

# Work through detecting object in camera again:
# https://blender.stackexchange.com/questions/45146/how-to-find-all-objects-in-the-cameras-view-with-python/45324
