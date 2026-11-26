"""사용: xvfb-run -a blender -b --factory-startup --python render_thumbnails.py -- <id목록파일|all> [views=34|all] [size]
renders/thumbs/<id>_<view>.png 및 public/assets/thumbnails/<id>.png(3/4 뷰) 생성."""
import bpy, os, sys, json, math, glob, mathutils
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else ['all']
sel = argv[0]; views = argv[1] if len(argv) > 1 else '34'; size = int(argv[2]) if len(argv) > 2 else 256
metas = [json.load(open(f)) for f in sorted(glob.glob(ROOT + '/renders/batch/*.json'))]
if sel != 'all': ids = set(open(sel).read().split()); metas = [m for m in metas if m['id'] in ids]
VIEWS = {'34': (35, 25), 'front': (0, 12), 'side': (90, 12), 'back': (180, 12)}
vlist = list(VIEWS) if views == 'all' else [views]
os.makedirs(ROOT + '/renders/thumbs', exist_ok=True); os.makedirs(ROOT + '/public/assets/thumbnails', exist_ok=True)
for m in metas:
    bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.gltf(filepath=ROOT + '/public/assets/models/' + m['model'])
    objs = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    pts = [o.matrix_world @ mathutils.Vector(c) for o in objs for c in o.bound_box]
    mn = mathutils.Vector([min(p[i] for p in pts) for i in range(3)]); mx = mathutils.Vector([max(p[i] for p in pts) for i in range(3)])
    c = (mn + mx) / 2; r = max((mx - mn).length * 0.5, 0.25)
    s = bpy.context.scene; s.render.engine = 'BLENDER_WORKBENCH'; s.display.shading.light = 'STUDIO'; s.display.shading.color_type = 'MATERIAL'
    s.display.shading.show_cavity = True; s.display.shading.cavity_type = 'BOTH'; s.display.shading.show_shadows = True; s.display.shading.show_specular_highlight = True
    s.display.shading.show_object_outline = True; s.render.film_transparent = True; s.render.resolution_x = s.render.resolution_y = size
    cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); s.collection.objects.link(cam); s.camera = cam; cam.data.lens = 50
    for v in vlist:
        az, el = VIEWS[v]; a = math.radians(az - 90); e = math.radians(el); dist = r / math.tan(math.radians(18)) * 0.85
        # 정면 = -Y(블렌더). az=0 → 정면에서 바라봄
        cam.location = c + mathutils.Vector((dist * math.cos(e) * math.cos(a) * 1, dist * math.cos(e) * math.sin(a), dist * math.sin(e)))
        cam.rotation_euler = (c - cam.location).to_track_quat('-Z', 'Y').to_euler()
        s.render.filepath = f"{ROOT}/renders/thumbs/{m['id']}_{v}.png"; bpy.ops.render.render(write_still=True)
        if v == '34': import shutil; shutil.copy(s.render.filepath, f"{ROOT}/public/assets/thumbnails/{m['id']}.png")
    print('R', m['id'])
