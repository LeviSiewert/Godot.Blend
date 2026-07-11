# TODO:

Milestones::
- [ ] Architecture
- [ ] Modular Tranformer Support
- [ ] Diff Tree Generation & Integration 


## Milestone Architecture

### GdBl : Transformer
- [ ] Context Dependencies 
  - [ ] Declaration / Attachment
  - [ ] Trimming 
  - Cases:
    - File | Subresource, Forced and allowable
- [ ] Module sub classes
- [ ] Dif Structure (Generic)
    ! Unknown exact exposure and scope. Plan !

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

BlType | GdType | Has Note | Hooking | Importing | Exporting | Round Trip
Coll | ResourceScene  | |
... | SubResource | |
... | ExtResource | |
... | PropertyCollection | |
Object | Node | |
Mesh | SubResource\[ArrayMesh] * 2  | * |
Coll Instance | Node instance  | |
Coll Inst Override | Node Instance Editable  | |
Animation(s) | SubResource\[AnimationLibrary/Animations] | * |
Armature | SubResource\[Armature+++CONSTRAINTS] | * | 

Armature:
- Both blender and Godot's armetures are single objects :D 
- Godot's constraint system is via nested nodes.
- Consider both parent-chain constraint nodes & custom scripted solution
  - Lean towards parent-chain constraints
- As constraints can be "sideways", a general node post-processor or hook will be needed?
  - Inline could be simpler, as transfomers in both directions can easily yield, then apply as req. But sideways makes this harder

Mesh:
- A second mesh subresource is is created in the GLTF -> tscn import process that acts as a shadow caster. Expose as a modifier or optional second mesh?
- Scoping & exposure of LODs is unknown atm!
  - Godot has a good inbuilt LOD system now, may not be required.

Animation:
- Scoping of structure IO is currently undefined, IE gathering and reference of animations *where* ??
  - Gltf creates libraries on import w/ all animations
  - Nla tracks -> baked animations as well? 
- Animations have ref to what node(s) they affect
