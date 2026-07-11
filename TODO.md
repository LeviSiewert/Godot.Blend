# TODO:

Milestones:
- [~] Architecture
- [ ] Blender UI
- [ ] Modular Tranformer Support
- [ ] Diff Tree Generation & Integration 
- [ ] GLTF conversion support

## Milestone Blender UI 
Architecture pre-req!

- [ ] Property Collection Display
- [ ] Gd Info Dislay
- [ ] Operator Exposure
  - [ ] Export per-collection
- [ ] Cache Files
  - Tscn Imported to seperate file for LibOver inst and preview


## Milestone Architecture

### GdBl : Transformer
- [ ] Context Dependencies 
  - [ ] Declaration / Attachment
  - [ ] Trimming 
  - Cases:
    - File | Subresource, Forced and allowable

### GdBl : Environemnt
- [ ] Dependency Resolution
  - [ ] Import
  - [ ] Export
  - [ ] Trimming Non-Usefull
  - Cases: 
    - Collection Instance
    - Collection Instance Lib Override 
    - Sub Resources
    - Sub Resources as File


### GdPy : SubTypes
- Substructure IO
  - [ ] Animation 
  - [ ] Armature
  - ie property series that are like `bones/0/name = ...` 


### GdBl : Types

| BlType | GdType | Has Note | Hooking | Importing | Exporting | Round Trip |
|---|---|---|---|---|---|---|
| Coll | ResourceScene  | | | |
| ... | SubResource | | | |
| ... | ExtResource | | | |
| ... | PropertyCollection | | | |
| Object | Node | | | |
| Mesh | SubResource\[ArrayMesh] * 2  | * | | |
| Mats | SubResource\[Material] | * | | |
| Coll Instance | Node instance  | | | |
| Coll Inst Override | Node Instance Editable  | | | |
| Armature | SubResource\[Armature+++CONSTRAINTS] | * | | |
| Animation(s) | SubResource\[AnimationLibrary/Animations] | * | | |

Materials:
- Initially Mimic / Conform to GLTF scope & IO 
- Can be expanded on later
- FUTURE:
  - Hooking custom Nodes/Shaders -> godot shaders
  - Consider traversal -> Shader glsl again ???

Mesh:
- A second mesh subresource is is created in the GLTF -> tscn import process that acts as a shadow caster. Expose as a modifier or optional second mesh?
- Scoping & exposure of LODs is unknown atm!
  - Godot has a good inbuilt LOD system now, may not be required.

Armature:
- Both blender and Godot's armetures are single objects :D 
- Godot's constraint system is via nested nodes.
- Consider both parent-chain constraint nodes & custom scripted solution
  - Lean towards parent-chain constraints
- As constraints can be "sideways", a general node post-processor or hook will be needed?
  - Inline could be simpler, as transfomers in both directions can easily yield, then apply as req. But sideways makes this harder


Animation:
- Armature is a strong prereq
- Attribute animation is strongly desired
- Scoping of structure IO is currently undefined, IE gathering and reference of animations *where* ??
  - Gltf creates libraries on import w/ all animations
  - Nla tracks -> baked animations as well? 
- Animations have ref to what node(s) they affect
