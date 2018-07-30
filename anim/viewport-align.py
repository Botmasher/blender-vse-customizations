import bpy
from mathutils import Matrix
import bpy_extras

#3 Align Object in Camera Viewport
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

def calc_move_vertex_to_pivot_xy_cam_center(cam, vertex_uv_xy):
    """Translate vertex from an extreme UV point to a new XY based on camera XY
    vertex_uv_xy = {'u': [0,1], 'v': , 'xy': [0,1]}
    """
    # X distance from cam
    cam_u = 0.5
    obj_u = vertex_uv_xy['u'][0] if abs(vertex_uv_xy['u'][0]) > abs(vertex_uv_xy['u'][1]) else vertex_uv_xy['u'][1]
    u_dist = cam_u - obj_u
    # Y distance from cam
    cam_v = 0.5
    obj_v = vertex_uv_xy['v'][0] if abs(vertex_uv_xy['v'][0]) > abs(vertex_uv_xy['v'][1]) else vertex_uv_xy['v'][1]
    v_dist = cam_v - obj_v

    dist_from_cam = [u_dist, v_dist]    # uv sign and mag
    # TEST: move vertex to cam center
    cam_u_to_x = 0.5 / cam.location.x
    cam_v_to_x = 0.5 / cam.location.y
    obj.location = (obj.location.x + dist_from_cam[0], obj.location.y + dist_from_cam[1], obj.location.z)
    return obj


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

# test
fit_vertices_to_frustum(bpy.context.object, bpy.context.scene.camera)

# TODO allow stretch (non-uniform scale)
# TODO move instead of scale if object could fit
#   - may want to move if object center is outside frustum
#   - alternatively guard check if obj inside frustum in the first place
def fit_to_frustum(obj, cam=bpy.context.scene.camera, move_into_view=True, margin=0.0, distance=5.0, distort=False):
    if not has_mesh(obj) or not is_camera(cam):
        return
    vertex_extremes = [0.0, 0.0, 0.0]
    # calculate mesh vertices far outside of viewport
    # TODO rework calculations here to store XY excess only at this step
    overflow_high = 0.0
    move_loc = obj.location
    for vertex in obj.data.vertices:
        uvz = get_frustum_loc(obj.matrix_world * vertex.co, cam=cam)
        # shallow Z location closest to camera (negative is behind)
        if uvz[2] < 0 and abs(uvz[2]) > abs(vertex_extremes[2]):
            # TODO handle Z index behind cam
            # use high negative w to move object in front of cam and recurse for u,v
            # move into cam view and retry
            center_in_cam_view(obj=obj, cam=cam, distance=distance)
            return fit_to_frustum(obj, cam=cam, move_into_view=False, margin=margin, distance=distance, distort=distort)
        # cut off and store excess (outside range 0-1)
        overflows = [max(0, d - 1.0) if d > 0 else d for d in uvz]
        # keep track of highest excess found so far
        vertex_extremes = [overflows[i] if abs(overflows[i]) > abs(vertex_extremes[i]) else vertex_extremes[i] for i in range(len(vertex_extremes))]
    # farthest XY locations outside UV render frame
    overflow_high = max(abs(overflows[0]), abs(overflows[1]))

    # use high UV to rescale object
    # TODO check meshes entirely out of viewport (move into view?)
    # adjust calc so mesh ends up fully inside (see vertex loop at top of method)
    # EITHER    double change to account for both sides (e.g. top AND bottom)
    # OR        move in opposite direction
    overflow_high *= 2              # account for excess on both sides
    obj.scale /= 1 + overflow_high
    #obj.location = move_loc        # move for both sides

    print("\nObj vertices in render space: {0}".format(vertex_extremes))
    print("Attempting to adjust by {0}".format(overflow_high))

    ## TODO move realign
    ##  - center first, check again then move
    ##  - centering first above avoids dealing with outside values
    #for i in range(len(vertex_extremes)):
    #    move_loc[i] *= vertex_extremes[i]

    return vertex_extremes

# test
#fit_to_frustum(bpy.context.object, margin=1.0)
