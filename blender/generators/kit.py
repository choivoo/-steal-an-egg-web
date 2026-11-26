"""Blender 모델링 키트: 프리미티브 가공·머티리얼·배치·내보내기. 정면 = Blender -Y (glTF +Z)."""
import bpy, bmesh, math, random
from mathutils import Vector, Euler
D = math.radians
class Kit:
    def __init__(self, seed=0):
        bpy.ops.wm.read_factory_settings(use_empty=True); self.R = random.Random(seed); self.mats = {}; self.objs = []
    # ---- materials ----
    def M(self, rgb, rough=0.55, metal=0.0, emit=0.0, alpha=1.0):
        key = (tuple(round(c, 3) for c in rgb), round(rough, 2), round(metal, 2), round(emit, 2), alpha)
        if key in self.mats: return self.mats[key]
        m = bpy.data.materials.new('m%d' % len(self.mats)); m.use_nodes = True; b = m.node_tree.nodes['Principled BSDF']
        b.inputs['Base Color'].default_value = (*rgb, 1); b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal
        if emit > 0: b.inputs['Emission Color'].default_value = (*rgb, 1); b.inputs['Emission Strength'].default_value = emit
        if alpha < 1: b.inputs['Alpha'].default_value = alpha; m.blend_method = 'BLEND'
        self.mats[key] = m; return m
    def _add(self, o, m, smooth=True):
        o.data.materials.append(m)
        if smooth:
            for p in o.data.polygons: p.use_smooth = True
        self.objs.append(o); return o
    def _xf(self, o, loc, rot, sc):
        o.location = loc; o.rotation_euler = Euler(rot); o.scale = sc
    # ---- primitives (bmesh, 빠름) ----
    def _mesh(self, name, build):
        me = bpy.data.meshes.new(name); bm = bmesh.new(); build(bm); bm.to_mesh(me); bm.free()
        o = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(o); return o
    def ball(self, loc, sc, m, seg=16, rot=(0, 0, 0)):
        o = self._mesh('ball', lambda bm: bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=max(6, seg // 2), radius=1)); self._xf(o, loc, rot, sc); return self._add(o, m)
    def ico(self, loc, r, m, sub=1, rot=(0, 0, 0), sc=None):
        o = self._mesh('ico', lambda bm: bmesh.ops.create_icosphere(bm, subdivisions=sub, radius=1)); self._xf(o, loc, rot, sc or (r, r, r)); return self._add(o, m, smooth=False)
    def cone(self, loc, r1, h, m, rot=(0, 0, 0), seg=8, r2=0.0, smooth=True):
        o = self._mesh('cone', lambda bm: bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=True, segments=seg, radius1=r1, radius2=r2, depth=h)); self._xf(o, loc, rot, (1, 1, 1)); return self._add(o, m, smooth)
    def cyl(self, loc, r, h, m, rot=(0, 0, 0), seg=10, smooth=True):
        return self.cone(loc, r, h, m, rot, seg, r2=r, smooth=smooth)
    def box(self, loc, sc, m, rot=(0, 0, 0), bevel=0.15):
        def b(bm):
            bmesh.ops.create_cube(bm, size=2)
            if bevel > 0: bmesh.ops.bevel(bm, geom=bm.verts[:] + bm.edges[:], offset=bevel, segments=2, affect='EDGES')
        o = self._mesh('box', b); self._xf(o, loc, rot, sc); return self._add(o, m, smooth=False)
    def torus(self, loc, R, r, m, rot=(0, 0, 0), seg=24, rseg=6):
        def b(bm):
            vs = []
            for i in range(seg):
                a = i / seg * math.tau; ring = []
                for j in range(rseg):
                    t = j / rseg * math.tau; ring.append(bm.verts.new(((R + r * math.cos(t)) * math.cos(a), (R + r * math.cos(t)) * math.sin(a), r * math.sin(t))))
                vs.append(ring)
            for i in range(seg):
                for j in range(rseg): bm.faces.new((vs[i][j], vs[(i + 1) % seg][j], vs[(i + 1) % seg][(j + 1) % rseg], vs[i][(j + 1) % rseg]))
        o = self._mesh('torus', b); self._xf(o, loc, rot, (1, 1, 1)); return self._add(o, m)
    def plate(self, loc, sc, m, rot=(0, 0, 0)):  # 얇은 날개막/지느러미/잎
        return self.ball(loc, sc, m, seg=10, rot=rot)
    def crystal(self, loc, r, h, m, rot=(0, 0, 0)):
        return self.cone(loc, r, h, m, rot, seg=6, smooth=False)
    def mirror(self, objs):
        out = []
        for o in objs:
            c = o.copy(); c.data = o.data; bpy.context.collection.objects.link(c)
            c.location.x = -o.location.x; c.rotation_euler = Euler((o.rotation_euler.x, -o.rotation_euler.y, -o.rotation_euler.z)); self.objs.append(c); out.append(c)
        return out
    def chain(self, pts, radii, m, seg=10):
        objs = []
        for (p, r) in zip(pts, radii): objs.append(self.ball(p, (r, r, r), m, seg=seg))
        return objs
    # ---- export ----
    def export(self, path):
        objs = [o for o in self.objs if o.name in bpy.data.objects]
        bpy.ops.object.select_all(action='DESELECT')
        for o in objs: o.select_set(True)
        bpy.context.view_layer.objects.active = objs[0]
        bpy.ops.object.make_single_user(object=True, obdata=True)
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        bpy.ops.object.join(); o = bpy.context.active_object
        bm = bmesh.new(); bm.from_mesh(o.data); bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5); bm.to_mesh(o.data); bm.free()
        # 바닥을 z=0, 중심을 원점으로
        zs = [v.co.z for v in o.data.vertices]; xs = [v.co.x for v in o.data.vertices]; ys = [v.co.y for v in o.data.vertices]
        off = Vector(((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, min(zs)))
        for v in o.data.vertices: v.co -= off
        o.location = (0, 0, 0)
        bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT'); bpy.ops.uv.smart_project(angle_limit=D(66), island_margin=0.02); bpy.ops.object.mode_set(mode='OBJECT')
        tris = sum(len(p.vertices) - 2 for p in o.data.polygons)
        bpy.ops.export_scene.gltf(filepath=path, export_format='GLB', use_selection=True, export_yup=True, export_apply=True, export_texcoords=True, export_normals=True)
        return tris, (max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs))
