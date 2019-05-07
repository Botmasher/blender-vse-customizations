import bpy
import bmesh

# expect to start with a flat image plane
paper_obj = bpy.context.scene.objects.active

# optionally adjust transparent background to white
untransparent = True
if untransparent:
    # turn off alpha for paper material
    mat = paper_obj.active_material
    mat.use_transparent = False
    # turn off alpha for paper textures
    for tex_slot in mat.texture_slots:
        if not tex_slot:
            continue
        tex = tex_slot.texture
        tex.use_map_alpha = False

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

# TODO: test and adjust extruding plane face
# source: https://blender.stackexchange.com/questions/115397/extrude-in-python

def extrude_mesh_face(obj, vector):
    """Extrude object face in mesh edit mode"""
    if obj.type != 'MESH':
        return
    
    # change to edit mode and select face
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_mode(type='FACE')
    bpy.ops.mesh.select_all(action='SELECT')

    # create mesh
    mesh = bmesh.new()
    mesh = bmesh.from_edit_mesh(bpy.context.object.data)

    # setup for extruding mesh
    for f in mesh.faces:
        face = f.normal
    r = bmesh.ops.extrude_face_region(mesh, geom=mesh.faces[:])
    verts = [e for e in r['geom'] if isinstance(e, bmesh.types.BMVert)]
    # extrude mesh passing in length and verts
    bmesh.ops.translate(mesh, vec=(face*vector), verts=verts)

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