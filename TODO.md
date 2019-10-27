# Task List

## Versions
- [ ] experiment with API changes to 2.8
- [ ] add user notes that 2.79 > 2.8 changes break these scripts

## Help for users
- [ ] a helpful test project
	- [ ] design a `test.blend` for users to try out the scripts
	- [ ] decide: one overall or one per tool?
	- [ ] update the section on getting started in the README to point users to the test

## Maintenance
- [ ] go through TODOs in various files and list them here

## Future plans
- [ ] 2.8/EEVEE
	- [ ] mat img swapper to animate changing cel
- [ ] auto roll up and drive, crossfade, etc. multiple shape keys
- [ ] music/audio visualization (envelopes?)
- [ ] shape keyer menu that manages and combines keys
	- multiple key values at once for a kind of meta shape
	- pulse or long action, one-way or return
- [ ] objects swap places (like semicircle over/under swap motion) with options on motion type
- [ ] tool for circling/uncircling, underlining, highlighting/unhighlighting target object
- [ ] automate papery furling
	- image plane -> two-sided paper with plain/other img back
	- crease edges, loop cut, subdivision subsurface, curve
- [X] existing keyframe shifter
- [ ] listener framework for catching events
- [ ] nonuniform transform strip scale slider to rescale factor both values and maintain scale
	- currently x, y must be calculated and set manually to keep non 1:1 ratios
- [ ] center object in viewport
- [X] shape key spikes for keyframing initial-final-initial values
- [ ] chain popin effect with frame offset (hurdle: preserving object selection order)
- [X] blurless frame button for quickly toggling motion blur during animation
- [ ] copy parented object, unparent, resize, move to selected object, optionally parent to selected
- [X] every other cutter: like framesplitter but removes (vec blurred) intermediate frames
- [X] print all fonts used in anim text objects
- [X] shuffle selected strips and change lengths (for randomizing animations like typing, bg talking)
- [X] pull out extend and separate already cut substrips from subcutter (useful for manually cut ones)
- [X] auto set alpha tex img to have nontransparent solid color bg
- [X] auto blend texture setup (including blend direction side-to-side, top-to-bottom, ...)
- [X] scene popin objects (scale-overshoot-settle keyframes)
- [X] fancy animated text (make array of letters/words, set fx, chain fx, allow random)
	- check out work from [other authors](https://gitlab.com/bkurdali/blender-addon-experiments/blob/master/text_fx.py)
- [X] allow for automatic manipulation (with unpacking then repacking) of metastrips
- [X] create materials from common color names
- [ ] save loc/rot/scale points and animate between them over n frames (allow push XOR pull anims)
	- even togglable mode where you move/rot/scale object, it sets kfs n frames apart
	- you can reverse for in/out
- [ ] auto stretch/squash
- [ ] overshoot i% over n frames before settling into final anim value
- [ ] project completion meter and hour tracker
- [ ] blender auto setup vse project file/assets
