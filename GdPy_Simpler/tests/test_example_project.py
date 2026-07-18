from ._resources.project_py import complex_tscn, blender_glb_tscn, blender_glb, icon_svg, script_gd, script_global_gd, test_a_tres, tscn_tscn

def test_make():
    _file,_res,_src = complex_tscn.make() 
    _file,_res,_src = blender_glb_tscn.make() 
    _file,_res,_src = blender_glb.make() 
    _file,_res,_src = blender_glb.make_import() 
    _file,_res,_src = icon_svg.make() 
    _file,_res,_src = icon_svg.make_import() 
    _file,_res,_src = script_gd.make() 
    _file,_res,_src = script_gd.make_uid() 
    _file,_res,_src = script_global_gd.make() 
    _file,_res,_src = script_global_gd.make_uid() 
    _file,_res,_src = test_a_tres.make() 
    _file,_res,_src = tscn_tscn.make()