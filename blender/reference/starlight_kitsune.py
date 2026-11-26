"""STARLIGHT KITSUNE — 레퍼런스 재현 (VOXEL 스타일). 재실행 가능한 단일 스크립트.
blender -b --factory-startup --python starlight_kitsune.py -- [render]"""
import bpy, bmesh, math, os, sys, random
from mathutils import Vector, Euler, Matrix
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
D = math.radians; RND = random.Random(7)
PX = 16; TEX_UNIT = 0.8      # 16px 텍스처 1장이 0.8 유닛 → 모든 부위 픽셀 크기 동일
OUTLINE = 0.045              # 높이(약 4.3)의 1%
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
def srgb(h): h = h.lstrip('#'); return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
def lin(c): return tuple(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c)
# ---------- 픽셀 텍스처 머티리얼 ----------
MATS = {}
def pixel_image(name, base, light, dark, speck=None, speck_n=0):
    img = bpy.data.images.new('tex_' + name, PX, PX); px = []
    B, L, Dk = srgb(base), srgb(light), srgb(dark); grid = [[B] * PX for _ in range(PX)]
    for _ in range(10):  # 블록 패치(2x2)
        x, y = RND.randrange(0, PX - 1), RND.randrange(0, PX - 1); c = L if RND.random() < 0.5 else Dk
        for dx in (0, 1):
            for dy in (0, 1): grid[(y + dy) % PX][(x + dx) % PX] = c
    for _ in range(14): grid[RND.randrange(PX)][RND.randrange(PX)] = L if RND.random() < 0.5 else Dk  # 단일 스펙
    if speck:
        S = srgb(speck)
        for _ in range(speck_n): grid[RND.randrange(PX)][RND.randrange(PX)] = S
    for row in grid:
        for c in row: px += [*c, 1.0]
    img.pixels = px; img.pack(); return img
def mat(name, base, light, dark, glow=0.0, metal=0.0, rough=0.75, speck=None, speck_n=0):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']
    t = nt.nodes.new('ShaderNodeTexImage'); t.image = pixel_image(name, base, light, dark, speck, speck_n); t.interpolation = 'Closest'
    nt.links.new(t.outputs['Color'], b.inputs['Base Color']); b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal
    if glow > 0: nt.links.new(t.outputs['Color'], b.inputs['Emission Color']); b.inputs['Emission Strength'].default_value = glow
    MATS[name] = m; return m
INK = bpy.data.materials.new('Outline_Ink'); INK.use_nodes = True; INK.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0.006, 0.005, 0.01, 1)
INK.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = 1; INK.use_backface_culling = True
FUR = mat('Fur', '#F3ECFA', '#FFFFFF', '#E2D6F1'); FUR2 = mat('Fur_Shade', '#E6DAF5', '#F3ECFA', '#D3C2EC')
RUMP = mat('Rump_Lilac', '#CDB2EE', '#DCC6F6', '#B999E3'); PAW = mat('Paw', '#6B2FC8', '#8448DE', '#4F1E9E')
GAL = mat('Tail_Galaxy', '#6A2FC9', '#8E52EC', '#4A1E98', speck='#F3E4FF', speck_n=6); TIP = mat('Tail_Tip', '#EFE7FA', '#FFFFFF', '#D8C8F2')
GOLD = mat('Gold', '#F6C532', '#FFE07A', '#D99A16', glow=0.6, metal=0.6, rough=0.35); EAR = mat('Ear_Inner', '#6E36C2', '#7E46D2', '#552398')
GEM = mat('Gem_Glow', '#E64DF5', '#F48CFF', '#C42EE0', glow=2.0, rough=0.2); EYE = mat('Eye_Glow', '#B347F2', '#C76BFF', '#9A2FDC', glow=1.6, rough=0.2)
WGLOW = mat('White_Glow', '#FFFFFF', '#FFFFFF', '#F6EEFF', glow=5.0, rough=0.2); SGLOW = mat('Star_Lilac_Glow', '#C89BFF', '#DDBBFF', '#AE7AF5', glow=3.5, rough=0.2)
DARK = mat('Dark', '#2A1838', '#3A2448', '#1C0F26', rough=0.6); EARTIP = mat('Ear_Tip', '#C8B0F0', '#D8C4F6', '#B49AE6')
EYEDK = mat('Eye_Rim', '#4B1E8A', '#5A2A9E', '#3A1570', rough=0.6); SPIRAL = mat('Spiral_Glow', '#F5D9FF', '#FFFFFF', '#E6B8FF', glow=3.0, rough=0.2)
# ---------- 그룹 ----------
def empty(name, parent=None):
    e = bpy.data.objects.new(name, None); sc.collection.objects.link(e); e.parent = parent; return e
ROOTE = empty('StarlightKitsune_Root'); G = {n: empty(n, ROOTE) for n in ('Head_Grp', 'Torso_Grp', 'Legs_Grp', 'Tail_Grp', 'Extras_Grp')}
COUNT = {}
def vbox(name, c, s, m, grp, rot=(0, 0, 0), bevel=0.07, outline=True):
    """베벨 박스. 월드좌표 기반 박스 UV → 모든 박스의 픽셀 크기가 동일."""
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * s[0], v.co.y * s[1], v.co.z * s[2]))
    bmesh.ops.bevel(bm, geom=bm.edges[:], offset=bevel * min(s), segments=1, affect='EDGES')
    R = Euler(rot).to_matrix()
    for v in bm.verts: v.co = R @ v.co + Vector(c)
    uv = bm.loops.layers.uv.new()
    for f in bm.faces:
        n = f.normal; ax = max(range(3), key=lambda i: abs(n[i]))
        for l in f.loops:
            co = l.vert.co; a, b = [(co.y, co.z), (co.x, co.z), (co.x, co.y)][ax]; l[uv].uv = (a / TEX_UNIT, b / TEX_UNIT)
    COUNT[name] = COUNT.get(name, 0) + 1; nm = f'{name}_{COUNT[name]:02d}'
    me = bpy.data.meshes.new(nm); bm.to_mesh(me); bm.free(); o = bpy.data.objects.new(nm, me); sc.collection.objects.link(o)
    me.materials.append(m)
    if outline:
        me.materials.append(INK); md = o.modifiers.new('Outline', 'SOLIDIFY'); md.thickness = OUTLINE; md.offset = 1; md.use_flip_normals = True; md.use_rim = False; md.material_offset = 1
    o.parent = G[grp]; return o
def mirror(fn):  # 대칭 부위: s=±1 로 두 번 생성
    for s in (1, -1): fn(s)
# ================= LEGS =================
LEGY = (-0.45, 0.85)
for y in LEGY:
    def leg(s, y=y):
        vbox('Leg_Upper', (s * 0.36, y, 0.6), (0.5, 0.5, 0.6), FUR, 'Legs_Grp')
        vbox('Leg_Cuff_Gold', (s * 0.36, y, 0.82), (0.56, 0.56, 0.08), GOLD, 'Legs_Grp')
        vbox('Paw', (s * 0.36, y - 0.05, 0.17), (0.6, 0.68, 0.34), PAW, 'Legs_Grp')
        vbox('Paw_Toe', (s * 0.36, y - 0.4, 0.09), (0.56, 0.12, 0.18), PAW, 'Legs_Grp', outline=False)
    mirror(leg)
# ================= TORSO =================
vbox('Torso_Main', (0, 0.25, 1.32), (1.05, 1.9, 0.86), FUR, 'Torso_Grp')
vbox('Torso_Back_Step', (0, 0.25, 1.78), (0.92, 1.6, 0.12), FUR, 'Torso_Grp')
vbox('Rump', (0, 0.88, 1.32), (1.12, 0.74, 0.96), RUMP, 'Torso_Grp')
SPIRAL_PIX = [(0, 0), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1), (2, -1), (2, 0), (2, 1), (2, 2), (1, 2), (0, 2), (-1, 2), (-2, 2), (-2, 1), (-2, 0), (-2, -1), (-2, -2), (-1, -2), (0, -2), (1, -2), (2, -2), (3, -2)]
for i, (a, b) in enumerate(SPIRAL_PIX[:22]):
    mirror(lambda s, a=a, b=b: vbox('Hip_Spiral_Glyph', (s * 0.565, 0.9 + a * 0.075, 1.3 + b * 0.075), (0.02, 0.07, 0.07), SPIRAL, 'Torso_Grp', bevel=0, outline=False))
# 가슴 러프(계단식 털)
vbox('Ruff_Main', (0, -0.68, 1.55), (1.5, 0.66, 0.98), FUR, 'Torso_Grp')
vbox('Ruff_Lower', (0, -0.86, 1.22), (1.12, 0.5, 0.56), FUR2, 'Torso_Grp')
vbox('Ruff_Bottom', (0, -0.9, 0.98), (0.74, 0.34, 0.3), FUR2, 'Torso_Grp')
vbox('Ruff_Neck', (0, -0.86, 2.02), (1.24, 0.56, 0.38), FUR, 'Torso_Grp')
mirror(lambda s: vbox('Ruff_Side', (s * 0.74, -0.62, 1.62), (0.36, 0.64, 0.8), FUR, 'Torso_Grp'))
mirror(lambda s: vbox('Ruff_Side_Tuft', (s * 0.76, -0.56, 1.94), (0.22, 0.44, 0.36), FUR2, 'Torso_Grp'))
mirror(lambda s: vbox('Ruff_Side_Low', (s * 0.62, -0.72, 1.2), (0.24, 0.42, 0.38), FUR2, 'Torso_Grp'))
# 금 하네스 + 가슴 보석
mirror(lambda s: vbox('Harness_V', (s * 0.3, -1.0, 1.66), (0.1, 0.06, 0.6), GOLD, 'Extras_Grp', rot=(0, s * D(-38), 0), outline=False))
vbox('Chest_Gem_Frame', (0, -1.12, 1.42), (0.4, 0.07, 0.4), GOLD, 'Extras_Grp', rot=(0, D(45), 0))
vbox('Chest_Gem', (0, -1.16, 1.42), (0.26, 0.06, 0.26), GEM, 'Extras_Grp', rot=(0, D(45), 0), outline=False)
vbox('Chest_Gem_Shine', (0, -1.19, 1.47), (0.07, 0.03, 0.07), WGLOW, 'Extras_Grp', outline=False)
for y in (0.48,):
    mirror(lambda s: vbox('Belt_Side', (s * 0.545, y, 1.31), (0.04, 0.1, 0.86), GOLD, 'Extras_Grp', outline=False))
    vbox('Belt_Top', (0, y, 1.85), (0.94, 0.1, 0.04), GOLD, 'Extras_Grp', outline=False)
mirror(lambda s: vbox('Trim_Belly', (s * 0.545, -0.1, 0.93), (0.04, 1.1, 0.07), GOLD, 'Extras_Grp', outline=False))
vbox('Tail_Root_Collar', (0, 1.22, 1.58), (0.84, 0.14, 0.56), GOLD, 'Extras_Grp')
# ================= HEAD =================
HC = Vector((0, -1.0, 2.48)); HEAD_SCALE = 1.26
vbox('Head', HC, (1.1, 0.9, 0.95), FUR, 'Head_Grp')
vbox('Head_Top_Step', (0, -0.95, 3.0), (0.9, 0.74, 0.12), FUR, 'Head_Grp')
mirror(lambda s: vbox('Cheek_Fluff', (s * 0.62, -0.98, 2.25), (0.24, 0.62, 0.5), FUR2, 'Head_Grp'))
mirror(lambda s: vbox('Cheek_Fluff_Tip', (s * 0.74, -0.92, 2.1), (0.16, 0.4, 0.28), FUR2, 'Head_Grp'))
vbox('Muzzle', (0, -1.58, 2.2), (0.56, 0.36, 0.36), FUR, 'Head_Grp')
vbox('Muzzle_Chin', (0, -1.52, 2.0), (0.44, 0.28, 0.12), FUR2, 'Head_Grp')
vbox('Nose', (0, -1.77, 2.3), (0.17, 0.06, 0.1), DARK, 'Head_Grp', outline=False)
vbox('Mouth', (0, -1.765, 2.13), (0.12, 0.02, 0.03), DARK, 'Head_Grp', outline=False)
def eye(s):
    vbox('Eye_Rim', (s * 0.28, -1.455, 2.46), (0.31, 0.03, 0.28), EYEDK, 'Head_Grp', outline=False)
    vbox('Eye_Glow', (s * 0.28, -1.47, 2.46), (0.21, 0.03, 0.19), EYE, 'Head_Grp', outline=False)
    vbox('Eye_Highlight', (s * 0.28 + s * 0.04, -1.49, 2.5), (0.07, 0.02, 0.07), WGLOW, 'Head_Grp', bevel=0, outline=False)
    vbox('Brow', (s * 0.3, -1.47, 2.64), (0.34, 0.04, 0.07), EYEDK, 'Head_Grp', rot=(0, s * D(-20), 0), outline=False)
mirror(eye)
def ear(s):
    r = (0, s * D(14), 0)
    vbox('Ear_Base', (s * 0.4, -0.88, 3.1), (0.48, 0.52, 0.36), FUR, 'Head_Grp', rot=r)
    vbox('Ear_Mid', (s * 0.45, -0.9, 3.4), (0.38, 0.38, 0.3), FUR, 'Head_Grp', rot=r)
    vbox('Ear_Tip', (s * 0.51, -0.92, 3.66), (0.24, 0.24, 0.26), EARTIP, 'Head_Grp', rot=r)
    vbox('Ear_Inner', (s * 0.39, -1.07, 3.24), (0.32, 0.04, 0.54), EAR, 'Head_Grp', rot=r, outline=False)
mirror(ear)
mirror(lambda s: vbox('Tiara_V', (s * 0.2, -1.47, 2.86), (0.42, 0.05, 0.1), GOLD, 'Head_Grp', rot=(0, s * D(28), 0), outline=False))
vbox('Tiara_Gem_Frame', (0, -1.47, 2.83), (0.34, 0.06, 0.34), GOLD, 'Head_Grp', rot=(0, D(45), 0))
vbox('Tiara_Gem', (0, -1.5, 2.83), (0.22, 0.05, 0.22), GEM, 'Head_Grp', rot=(0, D(45), 0), outline=False)
vbox('Tiara_Gem_Shine', (0, -1.53, 2.87), (0.06, 0.02, 0.06), WGLOW, 'Head_Grp', bevel=0, outline=False)
vbox('Crown_Prong', (0, -1.2, 3.2), (0.09, 0.09, 0.36), GOLD, 'Head_Grp')
mirror(lambda s: vbox('Crown_Prong', (s * 0.17, -1.16, 3.14), (0.08, 0.08, 0.3), GOLD, 'Head_Grp', rot=(0, s * D(18), 0)))
mirror(lambda s: vbox('Crown_Prong', (s * 0.3, -1.04, 3.08), (0.07, 0.07, 0.24), GOLD, 'Head_Grp', rot=(0, s * D(30), 0)))
# ================= EXTRAS: 후광 + 별 =================
HALO_C = Vector((0, -1.0, 3.82))
HR = 0.72; TILT = D(28)
def halo_pt(a): return HALO_C + Vector((HR * math.cos(a), HR * math.sin(a) * math.cos(TILT), HR * math.sin(a) * math.sin(TILT)))
for i in range(26):
    a = i / 26 * math.tau; p = halo_pt(a); tg = (halo_pt(a + 0.05) - halo_pt(a - 0.05)).normalized()
    vbox('Halo_Seg', p, (0.08, 0.2, 0.08), GOLD, 'Extras_Grp', rot=tg.to_track_quat('Y', 'Z').to_euler(), bevel=0.1)
STAR_C = Vector((0, -1.0, 4.02))
def star(c, scale, m, yoff, outline):
    vbox('Star_Core', c + Vector((0, yoff, 0)), (0.2 * scale, 0.05, 0.2 * scale), m, 'Extras_Grp', rot=(0, D(45), 0), outline=outline)
    for dx, dz in ((0, 1), (0, -1), (1, 0), (-1, 0)):
        for j, (w, l) in enumerate(((0.13, 0.16), (0.09, 0.16), (0.05, 0.12))):
            d = 0.13 + j * 0.13 + (0.1 if dz == 1 else 0) * j * 0.5
            vbox('Star_Arm', c + Vector((dx * d * scale, yoff, dz * d * scale)), ((w if dz else l) * scale, 0.05, (l if dz else w) * scale), m, 'Extras_Grp', bevel=0.1, outline=outline)
star(STAR_C, 1.0, SGLOW, 0, True); star(STAR_C, 0.62, WGLOW, -0.04, False)
# ================= TAILS (9) =================
TROOT = Vector((0, 1.22, 1.62))
TAILS = [(0, 50), (26, 40), (-26, 40), (46, 24), (-46, 24), (58, 8), (-58, 8), (62, -8), (-62, -8)]
TH = [0.66, 0.98, 1.2, 1.26, 1.16, 0.92, 0.62]
for k, (yaw, el) in enumerate(TAILS):
    d = Vector((math.sin(D(yaw)) * math.cos(D(el)), math.cos(D(yaw)) * math.cos(D(el)), math.sin(D(el))))
    pts = [TROOT + d * (0.35 + 0.56 * i) + Vector((0, 0, 0.022 * i * i)) for i in range(len(TH))]
    for i, p in enumerate(pts):
        tan = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized(); q = tan.to_track_quat('Y', 'Z'); e = q.to_euler(); M = q.to_matrix()
        t = TH[i]; m = GAL if i < 4 else TIP
        vbox('Tail%d_Seg' % k, p, (t, 0.58, t * 0.92), m, 'Tail_Grp', rot=e)
        if i == 4: vbox('Tail%d_Gold_Trim' % k, p - tan * 0.2, (t * 1.1, 0.09, t * 1.02), GOLD, 'Tail_Grp', rot=e)
        if i in (1, 2, 3):  # 별 문양(양쪽 면)
            for sgn in (1, -1):
                n = M @ Vector((sgn * (t / 2 + 0.012), 0, 0))
                vbox('Tail%d_Star' % k, p + n, (0.02, 0.07, 0.3), WGLOW, 'Tail_Grp', rot=e, bevel=0, outline=False)
                vbox('Tail%d_Star' % k, p + n, (0.02, 0.3, 0.07), WGLOW, 'Tail_Grp', rot=e, bevel=0, outline=False)
# ---------- 비율 보정(1차 비교 후) ----------
def xform_group(grp, pivot, scale, offset):
    for o in sc.objects:
        if o.parent is G[grp] and o.type == 'MESH':
            for v in o.data.vertices: v.co = Vector(pivot) + (v.co - Vector(pivot)) * scale + Vector(offset)
for g in ('Torso_Grp', 'Head_Grp', 'Extras_Grp', 'Tail_Grp'): xform_group(g, (0, 0, 0), 1.0, (0, 0, -0.14))
xform_group('Head_Grp', (0, -0.85, 2.0), HEAD_SCALE, (0, -0.05, 0)); xform_group('Extras_Grp', (0, -0.85, 2.0), 1.0, (0, -0.05, 0.25 * (HEAD_SCALE - 1) * 4))
# ---------- 접지 검사: 최저점 z=0 ----------
bpy.context.view_layer.update()
minz = min((o.matrix_world @ v.co).z for o in sc.objects if o.type == 'MESH' for v in o.data.vertices)
ROOTE.location.z -= minz; bpy.context.view_layer.update()
print('GROUND_MIN_Z_BEFORE', round(minz, 4), 'PARTS', sum(1 for o in sc.objects if o.type == 'MESH'))
# ---------- 스튜디오 ----------
sc.render.engine = 'BLENDER_EEVEE'; sc.view_settings.view_transform = 'Standard'; sc.view_settings.look = 'None'
sc.eevee.use_bloom = True; sc.eevee.bloom_threshold = 1.2; sc.eevee.bloom_radius = 2.5; sc.eevee.bloom_intensity = 0.04
sc.eevee.use_soft_shadows = True; sc.eevee.use_gtao = True; sc.eevee.gtao_distance = 0.6; sc.eevee.taa_render_samples = 32
w = bpy.data.worlds.new('Studio'); w.use_nodes = True; w.node_tree.nodes['Background'].inputs['Color'].default_value = (*lin(srgb('#2B2D31')), 1); w.node_tree.nodes['Background'].inputs['Strength'].default_value = 1.0; sc.world = w
bpy.ops.mesh.primitive_plane_add(size=40); fl = bpy.context.active_object; fl.name = 'Studio_Floor'
fm = bpy.data.materials.new('Floor_Grid'); fm.use_nodes = True; nt = fm.node_tree; b = nt.nodes['Principled BSDF']; b.inputs['Roughness'].default_value = 0.9
br = nt.nodes.new('ShaderNodeTexBrick'); br.inputs['Scale'].default_value = 20; br.inputs['Mortar Size'].default_value = 0.008; br.offset = 0
br.inputs['Color1'].default_value = br.inputs['Color2'].default_value = (*lin(srgb('#7A7F86')), 1); br.inputs['Mortar'].default_value = (*lin(srgb('#888D95')), 1)
nt.links.new(br.outputs['Color'], b.inputs['Base Color']); fl.data.materials.append(fm)
bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 14, 10), rotation=(D(90), 0, 0)); bd = bpy.context.active_object; bd.name = 'Studio_Backdrop'
bm_ = bpy.data.materials.new('Backdrop'); bm_.use_nodes = True; bm_.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (*lin(srgb('#34373C')), 1); bd.data.materials.append(bm_)
def light(name, loc, rot, power, size, col=(1, 1, 1)):
    l = bpy.data.lights.new(name, 'AREA'); l.energy = power; l.size = size; l.color = col; o = bpy.data.objects.new(name, l); sc.collection.objects.link(o); o.location = loc; o.rotation_euler = rot; return o
light('Key_Overhead', (0.5, -3.5, 8), (D(25), 0, 0), 1400, 6)
light('Front_Fill', (0, -9, 3), (D(85), 0, 0), 480, 8)
light('Side_Fill', (9, 0, 3), (D(80), 0, D(90)), 520, 8)
light('Rim_Cool', (-3, 6, 5), (D(-55), D(-25), 0), 700, 4, (0.72, 0.82, 1.0))
light('Fill_Soft', (-6, -5, 3), (D(70), 0, D(-50)), 300, 6)
light('Fill_Right', (6, -4, 3), (D(70), 0, D(50)), 200, 6)
cam = bpy.data.objects.new('Camera', bpy.data.cameras.new('Camera')); sc.collection.objects.link(cam); sc.camera = cam; cam.data.lens = 70
def shoot(name, loc, target, res=900):
    cam.location = loc; cam.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    sc.render.resolution_x = res; sc.render.resolution_y = res; sc.render.filepath = os.path.join(ROOT, 'renders/kitsune', name + '.png'); bpy.ops.render.render(write_still=True)
os.makedirs(os.path.join(ROOT, 'renders/kitsune'), exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, 'starlight_kitsune.blend'))
if 'render' in sys.argv:
    shoot('front', (0, -14, 3.4), (0, 0.3, 2.15)); shoot('side', (17, 1.0, 3.6), (0, 1.0, 2.35)); shoot('back34', (12, 14, 8), (0, 0.8, 2.1))
if 'export' in sys.argv:
    for o in sc.objects: o.select_set(o.type == 'MESH' and not o.name.startswith('Studio'))
    out = os.path.join(ROOT, 'public/assets/models/pets/starlight_kitsune.glb')
    bpy.ops.export_scene.gltf(filepath=out, export_format='GLB', use_selection=True, export_apply=True, export_yup=True); print('EXPORTED', os.path.getsize(out))
