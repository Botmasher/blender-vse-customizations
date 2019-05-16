import bpy
import bmesh
import math

# turn image plane into unfurlable paper
# - thicken (extrude) mesh to have front and back
# - select all edges
# - crease all edges
# - apply subdivision surface modifier (example settings: (4,4))
# - apply curve modifier
# - create bezier curve recursively spiraling inward
# - set curve modifier input value to created curve
# - parent curve to paper
# Go to edit mode, face selection mode and select all faces

def deselect(obj):
    obj.select = False
    return obj
def select(obj):
    obj.select = True
    return obj

# TODO: test and adjust extruding plane face
# source: https://blender.stackexchange.com/questions/115397/extrude-in-python
def extrude_mesh_face(obj, magnitude=1.0):
    """Extrude object face in mesh edit mode"""
    if obj.type != 'MESH' or not hasattr(obj, 'data'):
        return
    
    # change to edit mode and select face
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_mode(type='FACE')
    bpy.ops.mesh.select_all(action='SELECT')

    # create mesh
    mesh = bmesh.new()
    mesh = bmesh.from_edit_mesh(obj.data)

    # # setup for extruding mesh
    # for f in mesh.faces:
    #     face = f.normal
    # r = bmesh.ops.extrude_face_region(mesh, geom=mesh.faces[:])
    # verts = [e for e in r['geom'] if isinstance(e, bmesh.types.BMVert)]
    # # extrude mesh passing in length and verts
    # bmesh.ops.translate(mesh, vec=(face*vector), verts=verts)

    # extrude mesh through bpy.ops instead of above
    # inspired by https://stackoverflow.com/questions/37808840/selecting-a-face-and-extruding-a-cube-in-blender-via-python-api
    [deselect(face) for face in mesh.faces]
    mesh.faces.ensure_lookup_table()
    select(mesh.faces[0])
    bmesh.update_edit_mesh(obj.data, True)
    bpy.ops.mesh.extrude_faces_move(
        MESH_OT_extrude_faces_indiv = {
            "mirror": False
        },
        TRANSFORM_OT_shrink_fatten = {
            "value": -magnitude,
            "use_even_offset": True,
            "mirror": False,
            "proportional": 'DISABLED',
            "proportional_edit_falloff": 'SMOOTH',
            "proportional_size": 1,
            "snap": False,
            "snap_target": 'CLOSEST',
            "snap_point": (0, 0, 0), 
            "snap_align": False,
            "snap_normal": (0, 0, 0),
            "release_confirm": False
        }
    )

    # update & destroy mesh
    bmesh.update_edit_mesh(bpy.context.object.data) # write bmesh back to object mesh
    mesh.free()  # prevent further access

    # flip normals
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.flip_normals() 

    # recalculate uv
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project()

    # switch back to object mode
    bpy.ops.object.mode_set(mode='OBJECT')

    # recenter object origin
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    
    return obj

def select_and_crease(obj):
    """Set a hard crease along all edges of the object's mesh"""
    edges = []
    for edge in obj.data.edges:
        edge.crease = 1.0
        edges.append(edge)
    return edges

def _create_curve(name="paper-curve", curve_type="CURVE", coil_depth=1):
    """Make a new scroll-like coiled curve"""
    # create curve object and add to scene
    curve_data = bpy.data.curves.new(name, type=curve_type)
    curve_obj = bpy.data.objects.new(name, object_data=curve_data)
    bpy.context.scene.objects.link(curve_obj)
    bpy.context.scene.update()

    # curve config
    # create point data
    curve_data.splines.new(type='BEZIER')

    # TODO: recursively create up to coil_depth
    # def create_coordinates():
        # coordinates = [(1, 0, 0)]     # starting point
        # set lower then upper for each round of inner coiling
        # for n in range(1, coil_depth):
        #     coiling_offset = math.log(n) / 4
        #     coordinates.append((-1, coiling_offset, 0))
        #     coordinates.append((-1, 1 - coiling_offset, 0))
        # return coordinates
    # coordinates = create_coordinates()

    # set up points values for the curve
    coordinates = [
        (1.0, 0.0, 0.0),    # extra tail
        (-1.0, 0.0, 0.0),   # start of first coil
        (-1.0, 1.0, 0.0),   # top of coil
        (-1.0, 0.2, 0.0)    # end of first coil
    ]

    # create additional curve points on top of the one default point
    curve_data.splines[0].bezier_points.add(count=len(coordinates)-1)

    # map point coords to points data
    handle = (0.5, 0, 0)
    handle_type = 'ALIGNED'
    for i, point_data in enumerate(curve_data.splines[0].bezier_points):
        point_data.co = (*coordinates[i], 1)
        point_data.handle_left_type = handle_type
        point_data.handle_right_type = handle_type
        point_data.handle_left = handle
        point_data.handle_right = handle

    # TODO: unbreak curve handles and position points correctly
    # - consider starting from prefab bezier

    return curve_obj

def assign_existing_curve(obj, curve):
    if obj.type != 'MESH' or curve.type != 'CURVE':
        print("Failed to assign curve to object - invalid object or curve")
        return
    curve.parent = obj
    curve_modifier = obj.modifiers.get("curve")
    curve_modifier.curve = curve

def apply_modifiers(obj, curve=None, create_curve=False):
    modifiers = []

    # create subsurface modifier and set subdivisions
    subsurf_mod = obj.modifiers.new(
        name = 'subsurf',
        type = 'SUBSURF'
    )
    subsurf_mod.levels = 4
    subsurf_mod.render_levels = 4
    modifiers.append(subsurf_mod)

    # create curve modifier and set curve
    curve_mod = obj.modifiers.new(
        name = 'curve',
        type = 'CURVE'
    )
    # create coiled curve for paper modifier
    if create_curve:
        curve = _create_curve()
        curve_mod.object = curve
        curve.parent = obj
    # assign existing curve to paper modifier
    else:
        assign_existing_curve(obj, curve)

    modifiers.append(curve_mod)

    return modifiers

def _unalpha_texture_slot(texture_slot):
    texture_slot.use_map_alpha = False
    return texture_slot

def untransparent_img(obj):
    """Adjust transparent image plane background to albedo"""
    # turn off alpha for paper material
    material = obj.active_material
    material.use_transparency = False
    
    # turn off alpha for paper textures
    texture_slots = material.texture_slots
    for slot in texture_slots:
        slot and _unalpha_texture_slot(slot)

    return obj

## NOTE: below - run main functions

# find curve and paper mesh among selected
selected_objects = [obj for obj in bpy.context.scene.objects if obj.select]
paper_obj, furl_curve = (None, None)
for obj in selected_objects:
    if obj.type == 'MESH':
        paper_obj = obj
    if obj.type == 'CURVE':
        furl_curve = obj
        break

# set the plane alpha to nontransparent for paper effect
untransparent_img(paper_obj)

# furl paper
extrude_mesh_face(paper_obj, 0.01)
select_and_crease(paper_obj)
apply_modifiers(paper_obj, furl_curve)
