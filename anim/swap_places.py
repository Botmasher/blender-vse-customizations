import bpy

## Objects Swap Places
## Blender Python script by Joshua (GitHub user Botmasher)

# TODO: props
clockwise = False   # or counterclock
horizontal = True   # or vert
frame_length = 20   # length of the swap in frames

def get_selected():
    """List all objects currently selected in scene"""
    return bpy.context.view_layer.objects.selected

# TODO: order objects by position in cam
def pair_elements(elements, cut_straggler=False):
    # pair all pairable inpit
    object_pairs = [
        [elements[i], elements[i+1]]
        for i in range(0, len(elements), 2)
        if i + 1 < len(elements)
    ]
    # add lone nonpair if uncut
    if not cut_straggler and not len(elements) % 2:
        object_pairs.append([elements[-1]])
    
    return object_pairs

def move_and_keyframe(obj, loc):
    obj.keyframe_insert('location')
    obj.location = loc
    obj.keyframe_insert('location')

def swap_objects(objects_list):
    # pair off objects
    obj_pairs = pair_elements(objects_list, True)

    # swap objects in each pair
    # TODO: optimize positioning, add horiz vs vert positioning
    for obj_pair in obj_pairs:
        if len(obj_pair) != 2:
            raise ValueError(f"Unpaired, unswappable objects in {obj_pair}")
        (obj_a, obj_b) = obj_pair
        loc_a = obj_a.location[:]
        loc_b = obj_b.location[:]
        move_and_keyframe(obj_a, loc_a)
        move_and_keyframe(obj_b, loc_b)
        
        bpy.context.scene.frame_current += int(frame_length * 0.5)
        mid_loc_a = loc_b + ((loc_a - loc_b) * 0.5)
        mid_loc_b = loc_a + ((loc_a - loc_b) * 0.5)
        # TODO: move up/down out of the way midway in view
        mid_loc_a.z += 2.5 if clockwise else -2.5
        mid_loc_b.z += -2.5 if clockwise else 2.5
        move_and_keyframe(obj_a, mid_loc_a)
        move_and_keyframe(obj_b, mid_loc_b)
        
        bpy.context.scene.frame_current += int(frame_length * 0.5)
        move_and_keyframe(obj_a, loc_b)
        move_and_keyframe(obj_b, loc_a)

objs = get_selected()
swap_objects(objs)
