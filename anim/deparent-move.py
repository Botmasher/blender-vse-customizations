import bpy

## Deparent-move-reparent
##
## a Blender Python script by GitHub user Botmasher (Joshua R)
##
## Remove object parent, move object either to selected's position or to
## parented's same position globally, then optionally parent to selected.
##
## Motivation: deleting mesh object's parent may translate mesh to undesired
## locations upon removing parent offset.
##

def move(obj, loc):
    """Move the object to the given location"""
    if obj and hasattr(obj, 'location'):
        obj.location = loc
    return loc

def offset_parented_pos(obj):
    """Return the object's current world position if it were unparented"""
    if obj and hasattr(obj, 'parent') and hasattr(obj, 'location'):
        return [obj.location[i] + obj.parent.location[i] for i in range(len(obj.location))]
    return

def unset_parent(obj):
    """Remove the object's parent if it has one"""
    if obj and hasattr(obj, 'parent'):
        obj.parent = None
    return obj

def set_parent(obj, parent):
    """Set the object's parent"""
    obj.parent = parent
    return obj

def get_inactive_selected():
    """Find the first inactive selected object"""
    for object in bpy.context.scene.objects:
        if object.select and not object == bpy.context.scene.objects.active:
            return object
    return

def handle_deparenting(obj=bpy.context.scene.objects.active, to_selected=False, reparent=False):
    """Unset active object parent but maintain current position in world, optionally reparenting to the first inactive selected object"""
    offset_loc = offset_parented_pos(obj)
    unset_parent(obj)
    target = get_inactive_selected()
    if reparent and target:
        move(obj, target.location)
        reparent and set_parent(target)
    else:
        if to_selected and target:
            move(obj, target.location)
        else:
            move(obj, offset_loc)
    return obj

# TODO: offset from target position instead of snapping directly to target

# test deparent + keep world pos
handle_deparenting()
