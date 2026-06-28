
Blender architecture explanation:

The Godot architecture is based around:
- Project
    - Resources
        | Project.Godot
        | Assets
        |   - Data
        |   - Import Data
        | Tres
        |   - Primary Resource
        |   - Subresources
        |   + References
        | Scenes
            - Nodes (Recursive)
                -? Script ++ Properties ++ Signals
            - Subresources
            - Signals
            - Asset Instances
            + References

The blender architectures is based around the use of collections as proxies for Scene data && 3d model asset data, and storage of optional additional script information.

Conversion between GdPy and Blender is done via a recursive tree walk.
Properties in bulk are stored in a PointerCollection PropertyGroup due to blender's non Variant allowences. 

Storage of data is relevent to each type and context.

Class allowences for properties, ect are planned to be dyanmic based on an exported structure loaded in GdPy

Blender
    - Settings Project Interface -> GdPyProject
    
    - Txt "Singleton"
        - ResourcesCollection (PointerCollection) ->>
          - generic Tscn
          - generic Tres
          - generic Import
          - generic project.godot 

    - Collection == Tscn &| Gltf
        .Gd
            .Mode : Tscn &| Gtlf
            .export_only : bool = True
            .sub_resources
            .editable
            .signals
            .tscn
                .uid 
                .Path
                .root -> Node
            .gltf
                .uid 
                .Path 
                .import_settings
                .root -> Node
            .custom_ruleset #DEFER
        ~.[objects] 
            .Gd
                .unique_id (Gd Provided)
                .gdtype
                .script (uid | name | inbuilt | None | Defaulted)
                .properties

A bit thing in this tool is the allowence for non-uniform tree creation
The (Bl <-> GdPy | Gltf) transformer should allow for equivilent effect without equvilent structures or implimentation.

For instance a node should be allowed to be a hitbox mesh, and auto transform based on criteria via a given ruleset evaluating any object.
The hitbox in blender vs in godot are two different objects, possibly with different names and possibly with sub-objects.

Rulesets being used may affect direction allowences.

The bl<->py transformer will be using a zipped tree to allow for both GLTF objects & GdPy objects in an "identical" tree. Tree splitting can be done through filtered yielding, but should be avoided as all objects with scripts & properties that are *not empty / default* should be nodes in the gltf format

Another big thing is the allowencec for instance & refernce structures.
By default the criteria for an instance for a file is a collection instance.
An external Collecction with a library overide adds to the editable tree, which will be a different ruleset. There is an unknown discrepency here where overrides may not be accurately reproduced if the tree changes shape on export.
Thus to be accurate the lib overrided collection *may* require a transformation towards export, and diffed.

External references to gltf w/out a blender representation will be imported to cache collections/files.

Blender rep for UIDs will have to be searched for and maintained via file evaluation. If addon properties cannot be streamed when evaluating a file, import, evaluation and deletion of a central list will be required. 
This rep for UIDs could be maintained in 3 places, preferences (not desirable), a cache folder in the project, or a file that can be pushed.
The best option is the cache folder, not pushed to git

the blender addon would then have to maintain and update the list with the path the collection, asc with the UID & Filepath.

It's tempting to make this information "bidirectional", and have the ccache be the source of truth for all mapping.

This will be a later conversation