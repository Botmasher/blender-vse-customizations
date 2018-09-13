# Video Build-Animate-Cut Tools in Blender

A collection of scripts to automate various parts of the production process behind my animations.

## About This Code

These tools perform various bits of the job of putting together Blender animations for an edutainment web series. I've been developing these scripts with my own needs in mind. I have adjusted them as I've worked with other creators with different needs.

### First Words of Caution

Most scripts focus on tasks that I find repetitive or useful. I do not expect them to fit anyone else's needs. Still, maybe some of your needs match mine. If so, maybe you'll find it useful to test these tools and mold them to fit your projects. You can compare "**My typical uses**" down below.

### Project Background

The open source 3D modeling/animation/and-the-kitchen-sink software called [Blender](https://www.blender.org/) has a capable non-linear editor out of the box. In Blender terminology, this is the `Video Sequence Editor` (the `VSE`). For Blender Python, it is the `sequencer` (for operations) or `sequence_editor` (within scene data).

After experiencing how tethered the VSE was to the rest of Blender's animation and rendering systems and how much automated access the console and scripting offered, I slowly transitioned away from industry standard software to the VSE. As I did that I found myself leveraging Python more and more to run commands in the console and scripts in the editor. When some of that scripting applied to more than one project, I set up this repo, and it became my place for storing my most-tinkered-with scripts.

## Getting Started

Follow these basic steps to start trying these tools out:

1. make sure you have [Blender](https://www.blender.org/) installed (I'm on 2.79)
2. run a new Blender instance from your shell (to see caught exceptions)
3. start a new `.blend` project (or use the Blender default if loaded)
4. grab one or more scripts you'd like to test
	- either download, fork or clone this repository
	- or get a copy of a single script that interests you
5. change the type of one of your new project's areas to a Text Editor
6. inside the Text Editor, open the script in your project
	- select the **Open** button
	- use the file manager to search for and select a `.py` file
	- press **Open Text Block** in the file manager
7. press the **Run Script** button in the Text Editor

(Note that any package add-ons have their own process. They are added through `User Preferences`.)

### Handle with Care

Please test all scripts outside of your production projects thoroughly, then modify them for your needs, before running them inside a valuable project. At the very least, back up a copy of your project before importing any of these scripts.

### Understanding Dependencies

Most of these `.py` files only depend on standard Python and Blender libraries. To experiment more with Python, or to test Python outside of Blender, start with the [Python](https://www.python.org/downloads/) and the [pip](https://pip.pypa.io/en/stable/) websites.

Some scripts do check for the presence of other scripts, such as the automatic script runner. Few depend on the import of other scripts from this repo, like some of the `defaultanimworld` package.

## Naming

### Repo Name
This project began life as a couple scripts that kept being useful across multiple video editing projects, so the label `vse-customizations` stuck around in local folders and became part of the repo name. Scripting quickly reached into other parts of Blender, making the name increasingly inadequate, but it's a link so it stays.

### Directory Names
Naming got more representative as the file structure changed within the repo to acommodate various projects. Here's how the catalog of budding addons is currently  split:
- `anim/` for scripts that deal with any aspect of animation outside of the VSE
- `demo/` for `.blend` projects meant to test current scripts or tangent ideas
- `vse/` for scripts that deal with the sequencer

### Filenames
Conventions have been followed lightly. Script files contain lowercase human readable words separated by underscores and suffixed with the expected `.py` extension. Nothing groundbreaking, but note the deviations with dashes or multiple words smashed together with no separators.

Each script's name means to capture its primary goal. This often includes an action or description and the object or attribute it applies to: `popin_object` keyframes a popin (or popout) animation for a single object, `camanim` animates the scene camera. It's often imperfect and imprecise: `autocolor_strips` or `color_balance_strips` would be a more informative name than `auto_color`, but the directory and filename `vse/auto_color` do suggest that this is about sequencer strips.

## Motivation

I do a lot of Python scripting in Blender for each of my projects. Much of the time, I bring up Blender's Python console and execute commands directly. Some tasks grow complicated or repetitive, so I pull them out into their own `.py` scripts. That's especially true for tasks that cross projects. That's what this repo is for: storing those useful scripts so they're available to myself and others. When a script gets useful enough and stable enough, it deserves to be pulled out into its own package stored in a separate repo.

## My Typical Uses

Above I mentioned that the closer your needs are to mine, the more likely you are to get some use out of these. Here are things I normally do when making a video in Blender. Roughly in order, and without getting into the details, I do these things:

- create mesh models for scene objects
- create mesh models for some characters
- import many creative commons / fair use images as planes
	- often cut them or add vertices for finer control over animations
- also import hand-drawn characters as img planes (split for head, body, etc.)
	- each character uses textures for a limited number of hand-drawn keyframes
	- hand-drawn inbetweens are rare in my style, so using textures as keyframes works
- add mesh eyes, mouth, etc. to characters for finer control of facial movement
- use NPR to render my meshes to fit with my drawing/inking
- follow the storyboard to arrange all objects sequentially against a fixed background
- keyframe sequentially focusing mostly on three sets of values
	- location/rotation/scale on meshes/images or camera
	- rotation on bones
	- shape keys
	- primary movements focus on camera transitions between scenes
	- secondary movements focus on objects transitioning into, out of or within frustum
- render the animated footage as an image sequence
- import the sequence into a separate Blender project for NLE
- cut strips into scenes, combine strips, add other image and movie strips
- subcut animation frames and stretch, mask, layer or make meta strips out of these frames
- add audio, music, sound effects and other strips to the NLE project
- render the final cut out as an uploadable video

## Contributing

The tools here are tailored to the needs of a small number of creators, mainly my own. That said, they're in various states of usefulness and aiming for better things. If you spot something to fix or add, you're welcome to submit an issue or pull request with the specifics. Please do document reproducible steps for fixes. Give as much relevant context as possible for enhancements.
