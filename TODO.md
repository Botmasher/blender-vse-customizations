# Task List

## Help for users
- [ ] a helpful test project
	- [ ] design a `test.blend` for users to try out the scripts
	- [ ] decide: one overall or one per tool?
	- [ ] update the section on getting started in the README to point users to the test

## Maintenance
- [ ] go through TODOs in various files and list them here

## Future plans
- [X] pull out extend and separate already cut substrips from subcutter (useful for manually cut ones)
- [ ] center object in viewport
- [ ] make text editor keypress <kbd>OPT + A</kbd> default to animate instead of "å" unless held
- [X] auto set alpha tex img to have nontransparent solid color bg
- [X] auto blend texture setup (including blend direction side-to-side, top-to-bottom, ...)
- [X] scene popin objects (scale-overshoot-settle keyframes)
- [ ] fancy animated text (make array of letters/words, set fx, chain fx, allow random)
	- check out work from [other authors](https://gitlab.com/bkurdali/blender-addon-experiments/blob/master/text_fx.py)
- [ ] every other cutter: like framesplitter but removes (vec blurred) intermediate frames
- [X] create materials from common color names
- [ ] save loc/rot/scale points and animate between them over n frames (allow push XOR pull anims)
	- even togglable mode where you move/rot/scale object, it sets kfs n frames apart
	- you can reverse for in/out
- [ ] shape key cycles initial > final > initial values
	- in/out (close-open,open-close)
	- continuous (unblink-blink-unblink)
- [ ] auto stretch/squash
- [ ] overshoot i% over n frames before settling into final anim value
- [ ] project completion meter and hour tracker
- [ ] blender auto setup vse project file/assets
