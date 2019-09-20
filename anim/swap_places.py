import bpy

## Objects Swap Places
## Blender Python script by Joshua (GitHub user Botmasher)

# TODO: props
clockwise = False   # or counterclock
horizontal = True   # or vert
frame_length = 20   # length of the swap in frames

def get_selected_objects():
    """List all objects currently selected in scene"""
    selected_objs = [
        obj for obj in bpy.context.scene.objects
        if obj.select
    ]
    return selected_objs

# TODO: order objects by position in cam
def swap_objects(objects_list):
    # pair off objects
    obj_pairs = []
    for obj in objects_list:
        if not obj_pairs or len(obj_pairs[-1]) > 1:
            obj_pairs.append([obj])
        else:
            obj_pairs[-1].append(obj)
    # leave off stranded nonpair
    if len(obj_pairs[-1]) != 2:
        obj_pairs = obj_pairs[:-1]

    # swap objects in each pair
    # TODO: optimize positioning, add horiz vs vert positioning
    for obj_pair in obj_pairs:
        obj_a, obj_b = obj_pair
        loc_a = obj_a.location
        loc_b = obj_b.location
        obj_a.keyframe_insert('location')
        obj_b.keyframe_insert('location')
        bpy.context.scene.frame_current += frame_length
        obj_a.location = loc_b
        obj_a.keyframe_insert('location')
        obj_b.location = loc_a
        obj_b.keyframe_insert('location')

objs = get_selected_objects()
swap_objects(objs)
