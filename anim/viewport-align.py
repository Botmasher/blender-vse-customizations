import bpy
from mathutils import Matrix
import bpy_extras

## Align Object in Camera Viewport
##
## Blender Python script by Josh R (GitHub user Botmasher)

# /!\ Caution - current implementation slows with vertex count
# /!\ (may loop over vertices multiple times)

# Base implementation
# - determine point at center of camera x,y
# - determine focal point for camera z
# - place object at point
# - scale object to fit within frustum
#   - account for all points (or just normals) in mesh

# TODO align non-mesh objects like text (or separate?)

def get_current_cam_and_obj(scene=bpy.context.scene):
    cam = scene.camera
    obj = scene.objects.active
    return (cam, obj)

def is_translatable(*objs):
    """Determine if the object exists and is movable"""
    for obj in objs:
        if not obj or not obj.location:
            return False
    return True

## TODO iterate on center_obj() for better alignment
##  FUTURE: determine when object scaled to fit within view
##      - requires point detection?
##      - allow adjusting scale within view (like calculate view size * 0.5)

## newer iteration on center align
def center_in_cam_view(obj=bpy.context.object, cam=bpy.context.scene.camera, distance=0.0, snap=False):
    if not is_translatable(obj, cam):
        return

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
    if not point or not cam or not scene:
        return
    # scene to use for frame size
    # Camera object
    # World space location (mathutils.Vector)
    uv_loc = bpy_extras.object_utils.world_to_camera_view(scene, cam, point)
    # returns a Vector magnitude 3 with valid cam positions between 0<=uv_loc<=1
    #   - values for index 0,1 greater than 1 are above top-right of frame
    #   - values at index 2 less than 0 are behind camera
    return uv_loc

def is_frustum_loc(point, cam=bpy.context.scene.camera, scene=bpy.context.scene):
    """Check if a point falls within camera's rendered frame"""
    if not point or not cam or not scene: return
    uv_loc = bpy_extras.object_utils.world_to_camera_view(scene, cam, point)
    return (0.0 <= uv_loc[0] <= 1.0 and 0.0 <= uv_loc[1] <= 1.0 and uv_loc[2] >= 0.0)

def has_mesh(obj):
    """Check if the object contains mesh data"""
    if hasattr(obj.data, 'vertices'):
        return True
    return False

def is_camera(obj):
    """Check if the object is a Camera"""
    if obj and hasattr(obj, 'type') and obj.type == 'CAMERA':
        return True
    return False

def get_edge_vertices_uv_xy(obj, cam):
    """Find the rightmost, leftmost, topmost and bottommost vertex in camera view
    Return render UV and the world XY coordinates for these extremes
    """
    if not has_mesh(obj) or not is_camera(cam): return
    edges = {'u': [None, None], 'v': [None, None], 'x': [None, None], 'y': [None, None]}
    for v in obj.data.vertices:
        v_uv = get_frustum_loc(obj.matrix_world * v.co, cam=cam)
        # TODO add vertex to edges if it is more positive or negative than stored extreme edges
        # zeroth value for L/bottom of render screen, first value for R/top render screen
        edge_units = [['u', 'x'], ['v', 'y']]
        for i in range(2):
            uv, xy = edge_units[i]
            print("Vertex %s coords:" % uv.upper())
            v_uv and print(v_uv[i])
            print("Vertex %s coords:" % xy.upper())
            v.co and print((obj.matrix_world * v.co)[i])
            if edges[uv][0] is None or v_uv[i] < edges[uv][0]:
                edges[uv][0] = v_uv[i]
                edges[xy][0] = (obj.matrix_world * v.co)[i]
            if edges[uv][1] is None or v_uv[i] > edges[uv][1]:
                edges[uv][1] = v_uv[i]
                edges[xy][1] = (obj.matrix_world * v.co)[i]
    print("\n\nUV Extreme Edges:")
    print(edges)
    return edges

def is_clamped(r=[], r_min=0.0, r_max=1.0):
    """Check if all values in list fall between min and max values"""
    if min(*r, r_min) >= r_min and max(*r, r_max) <= r_max:
        return True
    return False

def ratio_scale_to_uv(width_u, height_v, downscale_factor):
    """Calculate scaledown UV width and height to fit within render UV"""
    # normalize <0 and >1 overflows (rendered UV points are in range 0-1)
    overscale_x = width_u - 1.0
    overscale_y = height_v - 1.0
    # use highest x or y to scale down uniformly
    overscale = overscale_y if overscale_y > overscale_x else overscale_x
    # already properly scaled
    if overscale <= 0: return 1.0
    # needs scaled
    downscale = 1.0 + overscale * 2.0   # double to account for both sides
    return downscale * downscale_factor

def move_vertices_to_uv(obj, width_u, height_v, edges):
    """Move a viewport-sized object entirely within render UV"""
    # store object's extreme UV points and dimensions
    edges_uv_flat = edges['u'] + edges['v']
    dimensions_uv = {'w': width_u, 'h': height_v}
    #dimensions_xy = {'w': edges['x'][1] - edges['x'][0], 'h': edges['y'][1] - edges['y'][1]}
    print(dimensions_uv)
    print(edges_uv_flat)

    # object fully in view - does not need moved
    if is_clamped(r=edges_uv_flat, r_min=0.0, r_max=1.0):
        print("Viewport Align - not moving object already fully in view")
        return

    # TODO: calc XY move from vert not from all space
    # - e.g. getting to U=0.3 will be different for a point at -0.3u, -0.3x at different depths
    # - e.g. getting to V=0.3 will differ for a point at 0.2v, 0.2y at different Z
    def test_vertex_calc(u, v, x, y):
        # NOTE if can't calc with these vals for a point, currently can't move correctly
        # NOTE find center of cam uv and translate to xy as point of comparison
        return

    # map point pos from UV to XY
    # anchor to viewport bottom left leaving margin on all sides
    target_uv = {'u': {}, 'v': {}}      # render (shape) space
    target_xy = {'x': {}, 'y': {}}      # world (form) space
    for d in dimensions_uv.keys():
        print(d)
        uv = 'u' if d == 'w' else 'v'
        margin_uv = (1 - dimensions_uv[d]) / 2   # centering between both sides
        print("margin on %s side: %s" % (uv, margin_uv))
        target_uv[uv]['low'] = margin_uv
        target_uv[uv]['high'] = margin_uv + dimensions_uv[d]
        print("2 margins plus body: %s" % (margin_uv + dimensions_uv[d] + margin_uv))

        # new x,y point at bottom left = (obj_xy / obj_uv) * new_target_uv
        xy = 'x' if d == 'w' else 'y'
        target_xy[xy]['high'] = (edges[xy][1] / edges[uv][1]) * target_uv[uv]['high']
        target_xy[xy]['low'] = (edges[xy][0] / edges[uv][0]) * target_uv[uv]['low']
    print(target_xy)

    # calculate object XY translation
    new_xy = {}
    for axis in target_xy:
        if axis not in ['x', 'y']: raise Exception("Viewport Align failed to move object {0} along {1} axis".format(obj, axis))
        new_delta = target_xy[axis]['high'] - target_xy[axis]['low']
        new_xy[axis] = getattr(obj.location, axis) + new_delta

    print(new_xy)

    ratio_scale = new_xy['x'], new_xy['y'], obj.location.z
    return ratio_scale

# TODO: rework movement
# - calculate edge vertices (incl uv and xy placement) after scale
#   - can rely on existing method above?
# - move to center using vertex uv & xy and cam current xy
#   - obj is centered visually to uv
#   - uv extremes account for margins: (1, 1) = (2*margin + w, 2*margin + h)

def determine_vertex_extremes(obj):
    """Calculate the most distant vertices """
    edges = {'u': [], 'v': [], 'x': [], 'y': []}
    # TODO calc extremes
    # - uv extremes are farthest from viewport center (0.5, 0.5)
    # - xy extremes just match the point
    #   - not highest XY values vs cam center
    return edges

def compare_abs_values_return_rel_values(a=[], b=None, origin=0):
    """Find the farthest of two values from origin"""
    if not b:
        # compare both elements of a two-element list
        if isinstance(a, list) and len(a) == 2:
            return a[0] if abs(a[0] - origin) > abs(a[1] - origin) else a[1]
        else:
            return None     # exception:
    # compare two values
    return a if abs(a - origin) > abs(b - origin) else b

def calc_move_vertex_to_pivot_xy_cam_center(vertex, cam, vertex_uv_xy):
    """Translate vertex from an extreme UV point to a new XY based on camera XY
    vertex_uv_xy = {'u': [0,1], 'v': , 'xy': [0,1]}
    """
    print(vertex_uv_xy)
    # X distance from cam
    cam_u = 0.5
    obj_u = vertex_uv_xy['u']   # compare_abs_values_return_rel_values(vertex_uv_xy['u'])
    u_dist = cam_u - obj_u
    x_dist = vertex_uv_xy['x'] - cam.location.x

    # Y distance from cam
    cam_v = 0.5
    obj_v = vertex_uv_xy['v']   # compare_abs_values_return_rel_values(vertex_uv_xy['v'])
    v_dist = cam_v - obj_v
    y_dist = vertex_uv_xy['y'] - cam.location.y

    margin_uv = {
        'left': 0.2,
        'right': 0.8,
        'bottom': 0.2,
        'top': 0.8,
        'center': [0.5, 0.5]
    }

    # Ratio for mvmt space from vertex to cam

    # account for 0.0 (no diff btwn cam loc and vertex loc)
    if not v_dist or not u_dist:
        print("unable to determine distance from cam center")
        return
    # for every unit u=1.0 move x=?
    vertex_x_per_u = x_dist / u_dist
    # for every unit v=1.0 move y=?
    vertex_y_per_v = y_dist / v_dist

    u_target = margin_uv['left']
    v_target = margin_uv['bottom']
    vertex_to_specific_x = vertex_x_per_u * (vertex_uv_xy['u'] - u_target)
    vertex_to_specific_y = vertex_y_per_v * (vertex_uv_xy['v'] - v_target)

    # TODO determine location of a fixed position relative to cam center (NOT obj)
    (cam.location.x - u_target, cam.location.y - v_target)

    obj.location = (cam.location.x - vertex_to_specific_x, cam.location.y - vertex_to_specific_y, obj.location.z)

    return vertex

# Fit based on vertex extremes NOT object center
# - calculate obj vertex X-Y extremes
# - figure out their center and distance
# - use the VERTEX center to align object in cam
def fit_vertices_to_frustum(obj, cam, move=True, scale_factor=1.0):
    if not has_mesh(obj) or not is_camera(cam) or len(obj.data.vertices) < 1:
        return

    # NOTE edges dict stores uv/xy keys with two-element array values storing low and high extremes
    #      { 'u': [], 'v': [], 'x': [], 'y': [] }
    edges = get_edge_vertices_uv_xy(obj, cam)
    if not edges: return

    # TODO then calculate this as a ratio of units needed to move
    # - how much must this object scale to fit within frustum?
    # - then, how much would it need to move for that scaled object to be entirely visible to current cam?
    width = edges['u'][1] - edges['u'][0]
    height = edges['v'][1] - edges['v'][0]

    obj.scale /= ratio_scale_to_uv(width, height, scale_factor)

    # TODO calc XY center of render viewport where UV (0.5, 0.5)
    # - this may be a line along global X,Y coords (see centering cam method)

    if move:
        move_pos = move_vertices_to_uv(obj, width, height, edges)
        print(move_pos)
        #obj.location = move_pos if move_pos else obj.location

    return obj

# TODO allow stretch (non-uniform scale)
# TODO move instead of scale if object could fit
#   - may want to move if object center is outside frustum
#   - alternatively guard check if obj inside frustum in the first place

# test runs
#fit_vertices_to_frustum(bpy.context.object, bpy.context.scene.camera)
cam, obj = get_current_cam_and_obj()
obj_edges = get_edge_vertices_uv_xy(obj, cam)
# reduce to only most extreme val
if obj_edges:
    obj_edges = {k: compare_abs_values_return_rel_values(v) for (k, v) in obj_edges.items()}
    calc_move_vertex_to_pivot_xy_cam_center(obj, cam, obj_edges)
