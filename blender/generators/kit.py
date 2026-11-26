"""VOXEL 스타일 모델링 키트 (Starlight Kitsune 레퍼런스 스타일).
모든 기본형을 베벨 박스로 표현: 구=계단식 십자 박스, 원뿔=축소 박스 계단, 원통=박스, 토러스=박스 고리.
머티리얼=16px 픽셀 텍스처(Closest), 월드 좌표 박스 UV(픽셀 크기 통일), 큰 부위에만 inverted-hull 외곽선. 정면 = Blender -Y."""
import bpy, bmesh, math, random
from mathutils import Vector, Euler, Matrix
D = math.radians
PX = 16
def _srgb2lin(x): return x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4
def _lin2srgb(x): x = max(0.0, min(1.0, x)); return x * 12.92 if x <= 0.0031308 else 1.055 * x ** (1 / 2.4) - 0.055
class Kit:
    def __init__(self, seed=0):
        bpy.ops.wm.read_factory_settings(use_empty=True); self.R = random.Random(seed); self.mats = {}; self.parts = []  # (bm-data verts, faces, mat, outline)
        self.ink = None
    # ---- 픽셀 텍스처 머티리얼 ----
    def M(self, rgb, rough=0.75, metal=0.0, emit=0.0, alpha=1.0):
        key = (tuple(round(c, 3) for c in rgb), round(rough, 2), round(metal, 2), round(emit, 2), alpha)
        if key in self.mats: return self.mats[key]
        i = len(self.mats); s = [_lin2srgb(c) for c in rgb]; R = random.Random(hash(key) & 0xffff)
        L = [min(1, c * 1.12 + 0.04) for c in s]; Dk = [c * 0.86 for c in s]
        grid = [[s] * PX for _ in range(PX)]
        for _ in range(9):
            x, y = R.randrange(PX - 1), R.randrange(PX - 1); c = L if R.random() < 0.5 else Dk
            for dx in (0, 1):
                for dy in (0, 1): grid[y + dy][x + dx] = c
        for _ in range(12): grid[R.randrange(PX)][R.randrange(PX)] = L if R.random() < 0.5 else Dk
        img = bpy.data.images.new('px%d' % i, PX, PX, alpha=alpha < 1); img.pixels = [v for row in grid for c in row for v in (*c, alpha)]; img.pack()
        m = bpy.data.materials.new('m%d' % i); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']
        t = nt.nodes.new('ShaderNodeTexImage'); t.image = img; t.interpolation = 'Closest'; nt.links.new(t.outputs['Color'], b.inputs['Base Color'])
        b.inputs['Roughness'].default_value = 0.35 if metal > 0.3 else rough; b.inputs['Metallic'].default_value = min(metal, 0.7)
        if emit > 0: nt.links.new(t.outputs['Color'], b.inputs['Emission Color']); b.inputs['Emission Strength'].default_value = min(emit, 5.0)
        if alpha < 1: b.inputs['Alpha'].default_value = alpha; m.blend_method = 'BLEND'
        m['rgb'] = list(rgb); self.mats[key] = m; return m
    # ---- 핵심: 베벨 박스 ----
    def vb(self, c, s, m, rot=(0, 0, 0), outline=None, bevel=True):
        s = (max(abs(s[0]), 0.004), max(abs(s[1]), 0.004), max(abs(s[2]), 0.004))
        if outline is None: outline = min(s) > 0.07 and max(s) > 0.16
        self.parts.append((tuple(c), s, m, Euler(rot), outline, bevel and min(s) > 0.05)); return [len(self.parts) - 1]
    # ---- 기존 인터페이스(복셀화) ----
    def ball(self, loc, sc, m, seg=16, rot=(0, 0, 0)):
        x, y, z = (abs(v) * 2 for v in sc)
        if max(x, y, z) < 0.12: return self.vb(loc, (x * 0.85, y * 0.85, z * 0.85), m, rot)
        if max(x, y, z) > 0.55:  # 큰 구: 계단식 층 타원체(복셀 실루엣)
            R = Euler(rot).to_matrix(); n = 7 if z > x * 1.15 else 5; egg = z > x * 1.15; out = []
            for i in range(n):
                t = -1 + (2 * i + 1) / n; w = math.sqrt(max(0.0, 1 - t * t)) * 1.04 + 0.04
                if egg: w *= (1.0 - 0.16 * max(0.0, t))  # 달걀형: 위쪽이 더 좁게
                out += self.vb(Vector(loc) + R @ Vector((0, 0, t * z / 2)), (x * w, y * w, z / n * 1.04), m, rot, outline=(i in (0, n - 1)) or None)
            return out
        return self.vb(loc, (x * 0.74, y * 0.74, z), m, rot) + self.vb(loc, (x, y * 0.74, z * 0.74), m, rot, outline=False) + self.vb(loc, (x * 0.74, y, z * 0.74), m, rot, outline=False)
    def ico(self, loc, r, m, sub=1, rot=(0, 0, 0), sc=None):
        s = sc or (r, r, r); x, y, z = (abs(v) * 1.7 for v in s)
        if max(x, y, z) < 0.15: return self.vb(loc, (x, y, z), m, (rot[0], rot[1], rot[2] + D(45)))
        return self.vb(loc, (x, y * 0.8, z * 0.8), m, rot) + self.vb(loc, (x * 0.8, y, z), m, (rot[0], rot[1], rot[2] + D(20)), outline=False)
    def cone(self, loc, r1, h, m, rot=(0, 0, 0), seg=8, r2=0.0, smooth=True):
        n = 1 if h < 0.12 else 2 if h < 0.35 else 3; R = Euler(rot).to_matrix(); last = []
        for i in range(n):
            t0, t1 = i / n, (i + 1) / n; r = r1 + (r2 - r1) * (t0 + t1) / 2 * (1 if r2 > 0 else 0.92)
            if r2 == 0: r = r1 * (1 - (t0 + t1) / 2 * 0.9)
            zc = -h / 2 + h * (t0 + t1) / 2; last += self.vb(Vector(loc) + R @ Vector((0, 0, zc)), (r * 1.7, r * 1.7, h / n * 1.02), m, rot, outline=(i == 0 and r1 > 0.08) or None)
        return last
    def cyl(self, loc, r, h, m, rot=(0, 0, 0), seg=10, smooth=True):
        return self.vb(loc, (r * 1.8, r * 1.8, h), m, rot)
    def box(self, loc, sc, m, rot=(0, 0, 0), bevel=0.15):
        return self.vb(loc, (sc[0] * 2, sc[1] * 2, sc[2] * 2), m, rot, bevel=bevel > 0)
    def torus(self, loc, R_, r, m, rot=(0, 0, 0), seg=24, rseg=6):
        n = max(8, min(20, int(R_ * 28))); Rm = Euler(rot).to_matrix(); last = []
        for i in range(n):
            a = i / n * math.tau; p = Vector((R_ * math.cos(a), R_ * math.sin(a), 0)); tg = Vector((-math.sin(a), math.cos(a), 0))
            q = (Rm @ tg).to_track_quat('Y', 'Z')
            last += self.vb(Vector(loc) + Rm @ p, (r * 2.2, R_ * math.tau / n * 1.08, r * 2.2), m, q.to_euler(), outline=r > 0.03, bevel=False)
        return last
    def plate(self, loc, sc, m, rot=(0, 0, 0)):
        return self.vb(loc, (abs(sc[0]) * 1.8, abs(sc[1]) * 1.8, abs(sc[2]) * 1.8), m, rot)
    def crystal(self, loc, r, h, m, rot=(0, 0, 0)):
        R = Euler(rot).to_matrix()
        return self.vb(Vector(loc) + R @ Vector((0, 0, -h * 0.15)), (r * 1.5, r * 1.5, h * 0.7), m, (rot[0], rot[1], rot[2] + D(45))) + self.vb(Vector(loc) + R @ Vector((0, 0, h * 0.32)), (r * 0.9, r * 0.9, h * 0.4), m, (rot[0], rot[1], rot[2] + D(45)), outline=False)
    def mirror(self, idxs):
        out = []; flat = []
        def fl(x):
            if x is None: return
            if isinstance(x, (list, tuple)) and not (len(x) and isinstance(x[0], float)):
                for y in x: fl(y)
            elif isinstance(x, int): flat.append(x)
        fl(idxs)
        for i in flat:
            c, s, m, e, o, b = self.parts[i]; self.parts.append(((-c[0], c[1], c[2]), s, m, Euler((e.x, -e.y, -e.z)), o, b)); out.append(len(self.parts) - 1)
        return out
    def chain(self, pts, radii, m, seg=10):
        return [i for p, r in zip(pts, radii) for i in self.ball(p, (r, r, r), m)]
    # ---- 미러가 직전에 생성된 복수 박스를 모두 포함하도록: 생성 범위 기록 ----
    def mark(self): return len(self.parts)
    def since(self, k): return list(range(k, len(self.parts)))
    # ---- 내보내기 ----
    def export(self, path):
        mats = list(self.mats.values()); idx = {m.name: i for i, m in enumerate(mats)}
        ink = bpy.data.materials.new('Outline_Ink'); ink.use_nodes = True; bb = ink.node_tree.nodes['Principled BSDF']; bb.inputs['Base Color'].default_value = (0.004, 0.004, 0.006, 1); bb.inputs['Roughness'].default_value = 1; ink.use_backface_culling = True
        bm = bmesh.new(); dl = bm.verts.layers.deform.new(); allz = []
        for (c, s, m, e, o, bev) in self.parts:
            tmp = bmesh.new(); bmesh.ops.create_cube(tmp, size=1)
            for v in tmp.verts: v.co = Vector((v.co.x * s[0], v.co.y * s[1], v.co.z * s[2]))
            if bev: bmesh.ops.bevel(tmp, geom=tmp.edges[:], offset=0.07 * min(s), segments=1, affect='EDGES')
            Rm = e.to_matrix(); vm = {}
            for v in tmp.verts:
                nv = bm.verts.new(Rm @ v.co + Vector(c)); nv[dl][0] = 1.0 if o else 0.0; vm[v] = nv; allz.append(nv.co.z)
            for f in tmp.faces:
                nf = bm.faces.new([vm[v] for v in f.verts]); nf.material_index = idx[m.name]
            tmp.free()
        mn = Vector((min(v.co.x for v in bm.verts), min(v.co.y for v in bm.verts), min(v.co.z for v in bm.verts))); mx = Vector((max(v.co.x for v in bm.verts), max(v.co.y for v in bm.verts), max(v.co.z for v in bm.verts)))
        off = Vector(((mn.x + mx.x) / 2, (mn.y + mx.y) / 2, mn.z))
        for v in bm.verts: v.co -= off
        dims = tuple(mx - mn); H = max(dims); unit = max(0.25, H / 7.0)  # 텍스처 반복 길이(모델 크기에 비례, 픽셀 밀도 일정)
        bm.normal_update(); uv = bm.loops.layers.uv.new()
        for f in bm.faces:
            n = f.normal; ax = max(range(3), key=lambda i: abs(n[i]))
            for l in f.loops: co = l.vert.co; a, b = [(co.y, co.z), (co.x, co.z), (co.x, co.y)][ax]; l[uv].uv = (a / unit, b / unit)
        me = bpy.data.meshes.new('model'); bm.to_mesh(me); bm.free(); o = bpy.data.objects.new('model', me); bpy.context.collection.objects.link(o)
        for m in mats: me.materials.append(m)
        me.materials.append(ink)
        vg = o.vertex_groups.new(name='outline'); vg.add([v.index for v in me.vertices if v.groups and v.groups[0].weight > 0.5], 1.0, 'REPLACE')
        # deform layer 이름 연결
        sm = o.modifiers.new('Outline', 'SOLIDIFY'); sm.thickness = max(0.012, H * 0.011); sm.offset = 1; sm.use_flip_normals = True; sm.use_rim = False
        sm.material_offset = len(mats); sm.vertex_group = 'outline'; sm.thickness_vertex_group = 0.0
        bpy.context.view_layer.objects.active = o; o.select_set(True)
        dg = bpy.context.evaluated_depsgraph_get(); ev = o.evaluated_get(dg); tris = sum(len(p.vertices) - 2 for p in ev.data.polygons)
        bpy.ops.export_scene.gltf(filepath=path, export_format='GLB', use_selection=True, export_yup=True, export_apply=True, export_texcoords=True, export_normals=True)
        return tris, dims
