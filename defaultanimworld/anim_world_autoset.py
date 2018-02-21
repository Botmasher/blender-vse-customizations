import bpy
from defaultanimworld import Autoconfig_Anim
from defaultanimworld import settings

## Automatically set up default anim world
## script by GitHub user Botmasher (Joshua R)
##
## Apply all of my custom world and render settings when starting up a new animation.
## Used for setting up, keyframing and rendering my core animations (my anim.blend files),
## but not for cutting rendered sequences (my project.blend files).

autoconfig = Autoconfig_Anim()
autoconfig.setup(settings)
