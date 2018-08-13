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

def move(obj, x=0.0, y=0.0, z=0.0):
    loc = (x, y, z)
    if obj and hasattr(obj, 'location'):
        obj.location = loc
    return loc

def offset_parented_pos(obj):
    if obj and hasattr(obj, 'parent') and hasattr(obj, 'location'):
        return [obj.location[i] + obj.parent.location[i] for i in range(len(obj.location))]
    return

def unset_parent(obj):
    if obj and hasattr(obj, 'parent'):
        obj.parent = None
    return obj

def set_parent(obj, parent):
    obj.parent = parent
    return obj

def get_inactive_selected():
    for object in bpy.context.scene.objects:
        if object.select and not object == bpy.context.scene.objects.active:
            return object
    return

def handle_deparenting(obj=bpy.context.scene.objects.active, to_selected=True, reparent=False):
    unset_parent(obj)
    target = get_inactive_selected()
    offset_loc = offset_parented_pos(obj)
    if to_selected and target:
        move(obj, x=target.location.x, y=target.location.y, z=target.location.z)
        reparent and set_parent(target)
    else:
        move(obj, x=offset_loc.x, y=offset_loc.y, z=offset_loc.z)
    return obj
