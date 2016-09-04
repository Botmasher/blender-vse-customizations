#!/usr/bin/env python
import bpy
import bpy.ops

#### RUN ALL YOUR SCRIPTS IN ONE GO
## 0. Import this script as a text object within your .blend file
## 1. Verify that all scripts have a first-line shebang that matches the variable below
## 2. Verify that no non-script texts have that same shebang on the first line
## 3. "Run Script" to read through all text objects included in the same .blend
## 4. This script will execute all texts that are scripts but are not this script
####

# recursion-blocking string unique to this file
ignore_k = '!!4GaSdF51$723%604&8qZ9h4typ#!!'
# initial line found in all of your script files but only in your script files
shebang_line = '#!/usr/bin/'

# switch to the CONSOLE
area = bpy.context.area.type
bpy.context.area.type = 'CONSOLE'

# iterate through and run lines in each file
for txt in bpy.data.texts:
    # toggle to avoid running non-code or rerunning this file
    ignore_this_file = False
    if shebang_line not in txt.lines[0].body:
        ignore_this_file = True
    # read through file and execute lines
    for ln in txt.lines:
        if ignore_this_file:
            pass
        # avoid rerunning this file
        elif ignore_k in ln.body:
            ignore_this_file = True
        elif ln.body == txt.lines[-1].body:
            bpy.ops.console.insert (text=ln.body)
            bpy.ops.console.execute()
            bpy.ops.console.insert (text="")
            bpy.ops.console.execute()
        else:
            bpy.ops.console.insert (text=ln.body)
            bpy.ops.console.execute()

# switch back to the TEXT_EDITOR
bpy.context.area.type = area

# OLD TESTS
# txt = bpy.data.texts.new (my_new_text_name)
# txt.clear()
# txt.write("print('Hi!')")