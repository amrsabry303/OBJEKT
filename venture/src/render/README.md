# Blender renders from approved drawings

Free route, no Magnific credits. Needs `pip install bpy==5.2.4` (Python 3.13).

    python make_obj173_blender.py OUTDIR grey     # grey geometry model views
    python make_obj173_blender.py OUTDIR steel    # brushed stainless test render

Geometry is built from the approved drawing (OBJ-173 rev 2: 150 mm cube, 2 mm walls, top plate with a 102 mm opening). Output goes in `venture/models/` which stays out of git while the repo is public. The `steel` mode as saved renders one view; edit the `shoot(...)` lines to add more.
