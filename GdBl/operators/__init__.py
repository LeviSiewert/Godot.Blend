## Example operator from https://github.com/varkenvarken/blenderaddons-ng/blob/main/add_ons/example_simple.py
## for testing

# import bpy
# from bpy.types import Object, Context

# class OBJECT_OT_move_x(bpy.types.Operator):
#     bl_idname = "object.move_x"
#     bl_label = "Move X"
#     bl_options = {"REGISTER", "UNDO"}

#     amount: bpy.props.FloatProperty(
#         name="Amount", description="Amount to move along X axis", default=1.0
#     ) #type:ignore

#     @classmethod
#     def poll(cls, context):
#         return context.active_object is not None and context.mode == "OBJECT"

#     @profile  # type: ignore (if line_profiler is available)
#     def do_execute(self, context: Context) -> None:
#         """Expensive part is moved out of the execute method to allow profiling.

#         Note that no profiling is done if line_profiler is not available or
#         if the environment variable `LINE_PROFILE` is not set to "1".
#         """
#         obj: Object | None = context.active_object
#         obj.location.x += self.amount  # type: ignore (because of the poll() method that ensures obj is not None)

#     def execute(self, context: Context) -> set[str]:  # type: ignore
#         """Move the active object along the X axis."""
#         self.do_execute(context)
#         return {"FINISHED"}


# OPERATOR_NAME: str = OBJECT_OT_move_x.__name__


# def register():
#     bpy.utils.register_class(OBJECT_OT_move_x)
    
# def unregister():
#     bpy.utils.register_class(OBJECT_OT_move_x)
def register():
    pass
    
def unregister():
    pass