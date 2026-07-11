# Godot.Blend

## What
Godot.Blend is a project for supporting a useful majority of Godot's project and data format within blender!

## End Goal
An artist should be able to create a rigged character with animations & constraints, place them in an env generated with geometry nodes and export everything to a cconsistent

## Extrensic Goals
1. Import and Export of godot's text file formats (`.Tscn`,`.Tres`,`.Import`,`.Godot`) to support artists in generating and maintaining 3d art assets within Blender.

2. Versionable modular transformers that allow T.Ds and similar technical roles to develop custom allowences for node transformation on a per-project basis.

3. Long term stability in IO for user-produced transformers.

4. Integrated tests for any modular transformer, user defined and internal.

## Pre-Existing work:
This project is heavily inspired by the Blender Studio's tool for Dogwalk, Paper Engine, and other various GLTF extension focused projects.


## Methodology, Allowences
The core of this addon is a modular tree transformer within the context of a godot project.

Files are imported to an intermediary structure, then transformed into the blender environemnt.

file.tscn <-> GdPy.core... <-> BlendFile (GdBl.Structure...)
This is for future allowences with dif trees, dif integration and non-uniform Tree Transformation (See Transformer:NonUniform)

Thus uniformity between `GdPy`, `GdBl` and all tests is highly desired for simplifying development. 

### GdBl
Blender Collections w/ TSCN export == Godot File
Collection instance w/ Lib Override == Editable file instance

Most data is stored on `BlObject.gd`

Godot Properties are stored as a custom dictionary-like property group, which allows for mutable types & display


### GdPy
The submodule for managing a godot project & all resources
*Most* behavior should be held within GdPy, and tied to GdBl's behavior via `Signals` (and similar)

The core is `Collections` that manage `context` objects

Module support for environments is also held here, as I want to integrate this submodule into other environemnts into the future.

### Transformer
The `Transformer` evalates any individual node against a series of `TransfomerRulesets`, which may produce a `TransfomerModule` which yields children, and returns a converted node.

Yielding children within a transformer is required in this project due to different data structures needing both "root-first" and "leaf-first" transformations.

Additionally a context object is passed in for "escaping" yielded children back into the function, and other contextual information. 

... TODO: 
- Expand on non-uniform tree structures
- Updates
- Dif and dif integration

## Contributions
Contributions are currently closed due to a focus on architecture and clean code.

After milestones of `architecture verification` and `plugin transformer support` are passed the repo will be moved to a public open source repo and contributions will be opened.

Most non-major version contributions should focus on 
- Bugs
- Internal conversions

## Licenses:
The blender addon is licensed under GPL-3.0 as required by blender's addon TOS
The submodule ./GdPy is licensed under MIT inline with Godot's liscensing

## Commericial Support
Developement is currently fully self-funded

## AI Policy
AI will not used in creating or writing anything in this codebase to the point of 1.0 release, but has been used in soft research and trawling for relevent information.

Future prs from trusted contributors must be strictly evaluated for tight scope, quality and uniformity to existing standards.

Bulk low quality PRs, AI generated or otherwise are troubling to all maintainers and people passionate about software and supporting art. In this any suspected agentic system will be blocked from contributing.

Life is too short to deal with bullshit and far too long to be half assed with the work we create :D