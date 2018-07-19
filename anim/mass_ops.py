import bpy

## Mass Ops Runner
## Blender Python script
## by GitHub user Botmasher (Joshua R)
##
## Run one operation across array of objects

def select(obj):
    obj.select = True
    return obj.select

def deselect(obj):
    obj.select = False
    return obj.select

def toggle(obj):
    obj.select = not obj.select
    return obj.select

def run_op(op_chain=[], args=[], objs=bpy.context.scene.objects, selected_only=True):
    """Execute an operation on multiple objects"""
    if type(objs) is not list or not op_chain: return
    selected_objects = []
    # deseselect and create selected list
    for o in objs:
        if o.select:
            selected_objects.append(o)
        deselect(o)
    target_objects = selected_objects if selected_only else objs

    bpy.context.scene.active_object = None

    # run op on object
    for o in target_objects:
        # focus objects
        bpy.context.scene.active_object = o
        select(o)

        # build callable operation
        op_exec = bpy.ops
        for op in op_chain:
            if hasattr(op_exec, op):
                op_exec = getattr(op_exec, op)
            else:
                print("Building operation - unable to chain {0} to {1}".format(op, op_exec))
                break
        # call op
        try:
            if not args:
                op_exec()
            else:
                op_exec(*args)
        except:
            raise Exception("Unable to run operation {0} on object {1}".format(op_exec, o))

        # clear objects
        deselect(o)
        bpy.context.scene.active_object = None

    # reselect
    for o in selected_objects:
        o and select(o)

    return target_objects

# test
run_op(op_chain=['text', 'run_script'])
