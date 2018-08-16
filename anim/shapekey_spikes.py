import bpy

## Shape Key Spikes
##
## Transition shape key to a new value then return back to original value.
## Optionally flattened spike keys in the middle around the target value.
## Example use: blink plane eyes

# NOTE
# - check for shape keys
# - get active shape key
# - take in target value (see props below; create UI slider)
# - keyframe active to current value
# - move ahead frames
# - keyframe active to target value
# - (optional middle frames at top of spike)
#   - move ahead frames
#   - keyframe active to target value again
# - move ahead frames
# - keyframe active to original value

# TODO add props for custom config
# - number of frames on spike sides
# - asymmetrical boolean if spike sides have different frames
# - number of frames on downward side if asymmetrical
# - number of frames at top of spike

# TODO add interface
# - slider for 0.0-1.0 target value
# - number of frames on spike sides
# - checkbox for asymmetrical sides
#   - if checked show number of frames on return side
# - number of spike frames
