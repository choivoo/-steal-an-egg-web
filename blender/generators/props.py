"""알·러닝머신·환경·건축·장비·기타·플레이어 빌더. 각 kind는 전용 형태 함수 → 색상만 다른 중복이 아님."""
import math
from kit import Kit, D
RAR = ['common','uncommon','rare','epic','legendary','mythic','cosmic','secret','eternal','divine']
def mix(a, b, t): return tuple(a[i] * (1 - t) + b[i] * t for i in range(3))
WHITE = (1, 1, 1)
GOLD = (1.0, 0.78, 0.25)
# ---------------- 알 ----------------
def build_egg(s):
    k = Kit(s['seed']); R = k.R; main, acc, glow = [tuple(c) for c in s['pal']]; ri = RAR.index(s['rarity'])
    shell = k.M(main, 0.45 - ri * 0.03, 0.05 * ri); ma = k.M(acc, 0.4, 0.15); mg = k.M(glow, 0.25, 0, 2 + ri * 0.5); mgold = k.M(GOLD, 0.25, 1.0); mcry = k.M(mix(glow, WHITE, 0.3), 0.08, 0.1, 1.3)
    sh = s['shape']; H = 0.5
    if sh == 'classic': k.ball((0, 0, H), (0.38, 0.38, 0.5), shell, seg=28)
    elif sh == 'tall': k.ball((0, 0, H + 0.05), (0.31, 0.31, 0.56), shell, seg=28); H += 0.05
    elif sh == 'round': k.ball((0, 0, 0.44), (0.42, 0.42, 0.44), shell, seg=28); H = 0.44
    elif sh == 'faceted': k.ico((0, 0, H), 0.42, shell, sub=2, sc=(0.38, 0.38, 0.5))
    elif sh == 'twisted':
        for j in range(6): k.ball((0, 0, 0.12 + j * 0.15), (0.36 - abs(j - 2.2) * 0.06,) * 2 + (0.12,), shell if j % 2 else ma, seg=20, rot=(0, 0, D(j * 15)))
    rz = lambda z: max(0.05, 0.38 * math.sqrt(max(0, 1 - ((z - H) / 0.5) ** 2)))  # 높이별 반경
    for d in s['decos']:
        if d == 'leaves':
            for j in range(6): a = j / 6 * math.tau; z = 0.2 + (j % 2) * 0.15; r = rz(z); k.plate((r * math.cos(a), r * math.sin(a), z), (0.05, 0.14, 0.015), k.M((0.3, 0.7, 0.25), 0.6), rot=(D(60), 0, a + D(90)))
        elif d == 'crystals':
            for j in range(5): a = j / 5 * math.tau + 0.3; z = 0.3 + (j % 3) * 0.15; r = rz(z); k.crystal((r * math.cos(a), r * math.sin(a), z), 0.05, 0.25, mcry, rot=(D(60) * math.sin(a), -D(60) * math.cos(a), 0))
        elif d == 'rings':
            for z in (0.32, 0.62): k.torus((0, 0, z), rz(z) + 0.01, 0.025, mgold if ri >= 4 else ma, seg=28, rseg=5)
        elif d == 'spikes':
            for j in range(8): a = j / 8 * math.tau; z = 0.25 + (j % 2) * 0.35; r = rz(z); k.cone((r * math.cos(a), r * math.sin(a), z), 0.04, 0.16, ma, rot=(D(90) * math.sin(a) * -1, D(90) * math.cos(a), 0), seg=5)
        elif d == 'rocks':
            for j in range(5): a = j * 1.3; z = 0.12 + j * 0.12; r = rz(z); k.ico((r * math.cos(a), r * math.sin(a), z), 0.07, k.M(mix(acc, (0.2, 0.2, 0.2), 0.5), 0.9), sub=0)
        elif d == 'cracks':
            for j in range(6): a = j * 1.05; z = 0.2 + (j % 3) * 0.2; r = rz(z) + 0.005; k.box((r * math.cos(a), r * math.sin(a), z), (0.012, 0.012, 0.09), mg, rot=(D(20 * (j % 2 * 2 - 1)), 0, a), bevel=0)
        elif d == 'bands':
            for j, z in enumerate((0.25, 0.5, 0.75)): k.torus((0, 0, z), rz(z) + 0.003, 0.012, mg if j == 1 else ma, seg=28, rseg=4)
        elif d == 'gems':
            for j in range(4): a = j / 4 * math.tau; z = H; r = rz(z); k.ico((r * math.cos(a), r * math.sin(a), z), 0.05, mg, sub=1)
        elif d == 'wings':
            k.mirror([k.plate((0.42, 0.05, H + 0.1), (0.22, 0.03, 0.1), k.M(mix(glow, WHITE, 0.5), 0.3, 0, 0.8), rot=(0, D(-30), 0)), k.plate((0.4, 0.08, H - 0.02), (0.16, 0.03, 0.07), k.M(mix(glow, WHITE, 0.5), 0.3, 0, 0.8), rot=(0, D(-10), 0))])
        elif d == 'halo': k.torus((0, 0, 1.15), 0.22, 0.025, mgold, seg=28, rseg=5)
        elif d == 'tentacles':
            for j in range(5): a = j / 5 * math.tau; k.chain([(0.36 * math.cos(a) * (1 + i * 0.15), 0.36 * math.sin(a) * (1 + i * 0.15), 0.12 - i * 0.03) for i in range(4)], [0.05 - i * 0.01 for i in range(4)], ma, seg=8)
        elif d == 'flowers':
            for j in range(4):
                a = j / 4 * math.tau + 0.4; z = 0.45 + (j % 2) * 0.2; r = rz(z)
                for q in range(5): b = q / 5 * math.tau; k.ball((r * math.cos(a) + 0.04 * math.cos(b), r * math.sin(a) + 0.04 * math.sin(b), z + 0.03 * math.sin(b)), (0.03, 0.03, 0.012), k.M((1, 0.6, 0.8), 0.5), seg=6)
        elif d == 'gears':
            for j in range(3): a = j * 2.1; z = 0.35 + j * 0.15; r = rz(z); k.torus((r * math.cos(a), r * math.sin(a), z), 0.07, 0.02, mgold, rot=(0, D(90), a), seg=10, rseg=4)
        elif d == 'stars':
            for j in range(10): a = R.uniform(0, math.tau); z = R.uniform(0.15, 0.85); r = rz(z) + 0.004; k.ico((r * math.cos(a), r * math.sin(a), z), 0.022, k.M((1, 1, 0.85), 0.2, 0, 4), sub=0)
        elif d == 'scales':
            for j in range(12): a = (j % 6) / 6 * math.tau + (j // 6) * 0.5; z = 0.3 + (j // 6) * 0.25; r = rz(z); k.ball((r * math.cos(a), r * math.sin(a), z), (0.06, 0.06, 0.02), ma, rot=(D(90) - D(30), 0, a + D(90)), seg=8)
        elif d == 'runes':
            for j in range(6): a = j / 6 * math.tau; z = H; r = rz(z) + 0.004; k.box((r * math.cos(a), r * math.sin(a), z + 0.05 * (j % 2)), (0.008, 0.04, 0.06), mg, rot=(0, 0, a), bevel=0)
    if ri >= 7: k.torus((0, 0, H), 0.55, 0.015, mcry, rot=(D(70), D(15), 0), seg=32, rseg=4)
    if ri >= 9: k.torus((0, 0, 1.2), 0.26, 0.035, mgold, seg=32, rseg=6); k.ball((0, 0, H), (0.3, 0.3, 0.42), k.M((1, 0.9, 0.5), 0.2, 0, 2.5, alpha=0.35), seg=20)
    k.cyl((0, 0, 0.02), 0.22, 0.04, k.M(mix(acc, (0.1, 0.1, 0.1), 0.5), 0.8), seg=16)  # 둥지 받침
    return k
# ---------------- 러닝머신 ----------------
def build_treadmill(s):
    k = Kit(s['seed']); t = s['tier']; hue = [(0.35, 0.38, 0.42), (0.55, 0.56, 0.6), (0.7, 0.45, 0.25), (0.8, 0.82, 0.86), (1, 0.78, 0.25), (0.2, 0.75, 0.4), (0.2, 0.4, 0.9), (0.85, 0.15, 0.2), (0.6, 0.3, 0.85), (0.6, 0.85, 1.0),
                                              (1.0, 0.4, 0.05), (0.1, 0.6, 0.7), (0.6, 0.5, 0.35), (0.45, 0.3, 0.9), (1, 0.65, 0.8), (0.4, 1, 0.75), (0.5, 0.9, 0.3), (1, 0.95, 0.4), (0.35, 0.2, 0.8), (1, 0.85, 0.4)][t]
    frame = k.M(hue, 0.35, 0.7); dark = k.M((0.08, 0.08, 0.1), 0.6); glow = k.M(mix(hue, WHITE, 0.3), 0.2, 0, 2 + t * 0.2); gold = k.M(GOLD, 0.25, 1)
    L, W = 2.4 + t * 0.03, 1.0
    k.box((0, 0, 0.12), (W * 0.6, L * 0.5, 0.12), frame, bevel=0.2); k.box((0, 0, 0.26), (W * 0.45, L * 0.46, 0.03), dark, bevel=0.3)
    for j in range(9): k.box((0, -L * 0.42 + j * L * 0.105, 0.295), (W * 0.44, 0.012, 0.005), glow if t >= 3 else k.M((0.2, 0.2, 0.22), 0.7), bevel=0)
    for y in (-L * 0.46, L * 0.46): k.cyl((0, y, 0.24), 0.07, W * 0.9, frame, rot=(0, D(90), 0), seg=12)
    rails = [k.cyl((W * 0.5, -L * 0.35, 0.75), 0.04, 1.0, frame, rot=(D(12), 0, 0), seg=8), k.cyl((W * 0.5, -L * 0.15, 1.15), 0.035, L * 0.4, frame, rot=(D(90), 0, 0), seg=8)]
    k.mirror(rails)
    k.box((0, -L * 0.44, 1.3), (W * 0.45, 0.06, 0.18), frame, rot=(D(-20), 0, 0), bevel=0.3); k.box((0, -L * 0.47, 1.31), (W * 0.35, 0.01, 0.12), glow, rot=(D(-20), 0, 0), bevel=0)
    if t >= 2: k.ico((0, -L * 0.5, 0.25), 0.12, glow, sub=1)  # 전원 코어
    if t >= 4:
        for j in range(4): k.cone((W * 0.62 * (1 if j % 2 else -1), -L * 0.3 + (j // 2) * L * 0.6, 0.3), 0.06, 0.4, glow, seg=6, smooth=False)
    if t >= 8: k.torus((0, L * 0.1, 1.3), 0.6, 0.03, glow, rot=(D(90), 0, 0), seg=32, rseg=5)
    if t >= 12: k.mirror([k.plate((W * 0.9, L * 0.2, 0.9), (0.5, 0.03, 0.2), k.M(mix(hue, WHITE, 0.5), 0.3, 0, 1.0), rot=(0, D(-30), D(15)))])
    if t >= 16: k.torus((0, -L * 0.44, 1.7), 0.25, 0.03, gold, rot=(D(70), 0, 0), seg=28, rseg=5)
    if t == 19:
        for j in range(8): a = j / 8 * math.tau; k.cone((0.9 * math.cos(a), 0.9 * math.sin(a), 0.1), 0.05, 0.3, gold, seg=4)
    return k
# ---------------- 환경 ----------------
def build_env(s):
    k = Kit(s['seed']); R = k.R; kind = s['kind']; main, acc, glow = [tuple(c) for c in s['pal']]
    mm = k.M(main, 0.8); ma = k.M(acc, 0.75); mg = k.M(glow, 0.25, 0, 2.5); wood = k.M((0.42, 0.28, 0.16), 0.9); stone = k.M(mix(acc, (0.5, 0.5, 0.5), 0.6), 0.9); mcry = k.M(mix(glow, WHITE, 0.25), 0.08, 0.1, 1.5)
    def tree(trunk_m, crown_m, style):
        h = R.uniform(2.6, 3.6); k.cyl((0, 0, h / 2), 0.18, h, trunk_m, seg=8); k.cone((0, 0, 0.12), 0.32, 0.25, trunk_m, seg=8)
        if style == 'pine':
            for j in range(4): k.cone((0, 0, h * 0.55 + j * 0.55), 1.1 - j * 0.22, 1.0, crown_m, seg=9)
        elif style == 'round':
            for j in range(5): k.ball((R.uniform(-0.5, 0.5), R.uniform(-0.5, 0.5), h + R.uniform(-0.2, 0.5)), (0.8, 0.8, 0.65), crown_m, seg=10)
        elif style == 'willow':
            k.ball((0, 0, h + 0.2), (1.1, 1.1, 0.6), crown_m, seg=12)
            for j in range(10): a = j / 10 * math.tau; k.cyl((0.95 * math.cos(a), 0.95 * math.sin(a), h - 0.5), 0.05, 1.2, crown_m, seg=5)
        elif style == 'palm':
            for j in range(7): a = j / 7 * math.tau; k.plate((0.8 * math.cos(a), 0.8 * math.sin(a), h - 0.05), (0.85, 0.18, 0.03), crown_m, rot=(0, D(18), a))
        elif style == 'bare':
            for j in range(5): a = j * 1.3; k.cyl((0.35 * math.cos(a), 0.35 * math.sin(a), h * 0.75 + j * 0.1), 0.06, 0.9, trunk_m, rot=(D(45) * math.sin(a), D(45) * math.cos(a), 0), seg=5)
        elif style == 'glow':
            k.ball((0, 0, h + 0.3), (1.0, 1.0, 0.8), crown_m, seg=12)
            for j in range(8): k.ico((R.uniform(-0.9, 0.9), R.uniform(-0.9, 0.9), h + R.uniform(-0.3, 0.8)), 0.09, mg, sub=1)
        elif style == 'spiral':
            for j in range(8): a = j * 0.9; k.ball((0.5 * math.cos(a), 0.5 * math.sin(a), h + j * 0.2), (0.4 - j * 0.03,) * 3, crown_m, seg=10)
    def rock(n=4, m=None, sc=1.0):
        for j in range(n): k.ico((R.uniform(-0.5, 0.5) * sc, R.uniform(-0.5, 0.5) * sc, R.uniform(0.2, 0.5) * sc), R.uniform(0.35, 0.7) * sc, m or stone, sub=1, sc=(R.uniform(0.4, 0.8) * sc, R.uniform(0.4, 0.8) * sc, R.uniform(0.3, 0.6) * sc))
    def crystals(m, n=6, h=1.4):
        for j in range(n): a = j / n * math.tau; k.crystal((0.25 * math.cos(a), 0.25 * math.sin(a), h * 0.3), 0.14, h * R.uniform(0.5, 1.0), m, rot=(D(25) * math.sin(a), -D(25) * math.cos(a), 0))
        k.crystal((0, 0, h * 0.5), 0.2, h * 1.1, m)
    def mushroom(cap_m, glow_=False):
        for j in range(3): x, y, h = R.uniform(-0.4, 0.4), R.uniform(-0.4, 0.4), R.uniform(0.4, 1.1); k.cyl((x, y, h / 2), 0.07 + h * 0.05, h, k.M((0.95, 0.9, 0.8), 0.7), seg=8); k.ball((x, y, h), (0.3 + h * 0.2, 0.3 + h * 0.2, 0.18), mg if glow_ else cap_m, seg=14)
    def pillar(m, broken=False, h=2.5):
        k.box((0, 0, 0.12), (0.5, 0.5, 0.12), m, bevel=0.2); k.cyl((0, 0, h / 2), 0.3, h * (0.7 if broken else 1), m, seg=12); k.box((0, 0, h + 0.1), (0.45, 0.45, 0.1), m, bevel=0.2) if not broken else k.ico((0.5, 0.2, 0.2), 0.25, m, sub=0)
    def arch(m, h=2.4):
        k.box((-1, 0, h / 2), (0.25, 0.3, h / 2), m, bevel=0.15); k.box((1, 0, h / 2), (0.25, 0.3, h / 2), m, bevel=0.15); k.box((0, 0, h + 0.15), (1.4, 0.35, 0.18), m, bevel=0.15)
    def plant(m, n=6, h=1.2, w=0.12):
        for j in range(n): a = j / n * math.tau; k.plate((0.25 * math.cos(a), 0.25 * math.sin(a), h * 0.5), (w, 0.03, h * 0.55), m, rot=(D(15) * math.sin(a), -D(15) * math.cos(a), a))
    def flower(cm):
        for j in range(5):
            x, y = R.uniform(-0.5, 0.5), R.uniform(-0.5, 0.5); h = R.uniform(0.3, 0.6); k.cyl((x, y, h / 2), 0.02, h, k.M((0.3, 0.6, 0.25), 0.7), seg=5)
            for q in range(5): b = q / 5 * math.tau; k.ball((x + 0.07 * math.cos(b), y + 0.07 * math.sin(b), h), (0.06, 0.06, 0.02), cm, seg=6)
            k.ball((x, y, h + 0.01), (0.04,) * 3, k.M((1, 0.85, 0.2), 0.5), seg=6)
    K = kind
    if K in ('tree_pine', 'tree_snowpine'): tree(wood, k.M((0.15, 0.45, 0.25), 0.8), 'pine'); (K == 'tree_snowpine') and [k.cone((0, 0, 2.3 + j * 0.55), 0.85 - j * 0.2, 0.25, k.M(WHITE, 0.6), seg=9) for j in range(3)]
    elif K == 'tree_oak': tree(wood, mm, 'round')
    elif K == 'tree_willow': tree(wood, mm, 'willow')
    elif K in ('tree_jungle', 'palm'): tree(wood, k.M((0.2, 0.6, 0.2), 0.7), 'palm')
    elif K in ('charred_tree', 'storm_tree'): tree(k.M((0.12, 0.1, 0.1), 0.9), mm, 'bare'); K == 'storm_tree' and k.ico((0, 0, 3.6), 0.25, mg, sub=1)
    elif K == 'tree_sakura': tree(k.M((0.35, 0.22, 0.2), 0.9), k.M((1, 0.72, 0.85), 0.7), 'round')
    elif K in ('glow_tree', 'nebula_tree'): tree(k.M((0.2, 0.2, 0.35), 0.8), mm, 'glow')
    elif K == 'spore_tree': tree(ma, mm, 'spiral')
    elif K in ('rock', 'snow_rock', 'dune_rock', 'basalt', 'amber_rock', 'big_rock', 'sky_rock', 'lava_rock'):
        rock(4 if K != 'big_rock' else 6, {'snow_rock': k.M((0.85, 0.9, 0.95), 0.7), 'dune_rock': k.M((0.8, 0.62, 0.38), 0.9), 'basalt': k.M((0.12, 0.12, 0.14), 0.8), 'amber_rock': k.M((1, 0.6, 0.15), 0.2, 0, 0.5, alpha=0.85), 'lava_rock': k.M((0.15, 0.08, 0.06), 0.9)}.get(K), 1.6 if K == 'big_rock' else 1.0)
        if K == 'lava_rock':
            for j in range(4): k.box((R.uniform(-0.3, 0.3), R.uniform(-0.3, 0.3), 0.5), (0.02, 0.2, 0.02), mg, rot=(0, 0, R.uniform(0, 3)), bevel=0)
        if K == 'sky_rock': k.cone((0, 0, -0.4), 0.7, 1.0, stone, rot=(D(180), 0, 0), seg=7, smooth=False)
    elif K in ('crystal', 'ice_crystal', 'ember_crystal', 'star_crystal', 'alien_crystal', 'storm_crystal', 'glow_crystal'): crystals(mcry, 6 + (len(K) % 4), 1.2 + (len(K) % 3) * 0.3)
    elif K in ('mushroom', 'glow_mushroom'): mushroom(ma, K == 'glow_mushroom')
    elif K == 'bush' or K == 'bush_dry':
        for j in range(5): k.ball((R.uniform(-0.4, 0.4), R.uniform(-0.4, 0.4), 0.35), (0.45, 0.45, 0.38), k.M((0.55, 0.45, 0.25), 0.9) if K == 'bush_dry' else mm, seg=10)
    elif K in ('flower',): flower(k.M(mix(acc, (1, 0.4, 0.6), 0.5), 0.5))
    elif K in ('fern', 'giant_fern', 'reed', 'kelp', 'bamboo', 'giant_leaf', 'cycad'):
        cfg = {'fern': (8, 0.9, 0.12), 'giant_fern': (9, 2.4, 0.3), 'reed': (10, 1.6, 0.03), 'kelp': (7, 2.2, 0.1), 'bamboo': (6, 2.8, 0.06), 'giant_leaf': (4, 1.6, 0.6), 'cycad': (10, 1.4, 0.18)}[K]
        if K == 'bamboo':
            for j in range(6): a = j; x, y = 0.35 * math.cos(a), 0.35 * math.sin(a); k.cyl((x, y, 1.4), 0.06, 2.8, k.M((0.45, 0.7, 0.3), 0.6), seg=8); [k.torus((x, y, 0.5 + q * 0.6), 0.065, 0.012, k.M((0.35, 0.55, 0.2), 0.6), seg=10, rseg=3) for q in range(4)]
        else:
            if K == 'cycad': k.cyl((0, 0, 0.5), 0.25, 1.0, wood, seg=10)
            plant(k.M((0.2, 0.55, 0.25), 0.7) if K != 'kelp' else k.M((0.2, 0.5, 0.3), 0.6), *cfg)
    elif K in ('log', 'driftwood', 'frozen_log', 'stump'):
        if K == 'stump': k.cyl((0, 0, 0.3), 0.4, 0.6, wood, seg=12); k.cyl((0, 0, 0.61), 0.36, 0.02, k.M((0.75, 0.6, 0.4), 0.8), seg=12)
        else: k.cyl((0, 0, 0.3), 0.3, 2.0, k.M((0.75, 0.85, 0.95), 0.4) if K == 'frozen_log' else wood, rot=(0, D(90), D(20)), seg=12); [k.cyl((0.3, 0.1, 0.55), 0.06, 0.4, wood, rot=(D(40), 0, 0), seg=6)]
    elif K in ('ruin_pillar', 'sunken_pillar', 'obelisk', 'vine_pillar', 'cloud_pillar', 'totem'):
        if K == 'obelisk': k.box((0, 0, 1.4), (0.3, 0.3, 1.4), stone, bevel=0.1); k.cone((0, 0, 2.95), 0.42, 0.3, mg, seg=4, smooth=False); [k.box((0.31, 0, 0.6 + j * 0.5), (0.005, 0.12, 0.12), mg, bevel=0) for j in range(4)]
        elif K == 'totem':
            for j in range(4): k.box((0, 0, 0.35 + j * 0.62), (0.35, 0.35, 0.3), [stone, ma, wood, mm][j], bevel=0.25); k.ball((0.18, -0.34, 0.45 + j * 0.62), (0.07, 0.03, 0.07), mg, seg=6); k.ball((-0.18, -0.34, 0.45 + j * 0.62), (0.07, 0.03, 0.07), mg, seg=6)
        elif K == 'cloud_pillar':
            for j in range(6): k.ball((R.uniform(-0.3, 0.3), R.uniform(-0.3, 0.3), 0.4 + j * 0.45), (0.6, 0.6, 0.4), k.M((0.92, 0.94, 1), 0.9), seg=10)
        else: pillar(stone, K in ('ruin_pillar', 'sunken_pillar')); (K == 'vine_pillar') and [k.torus((0, 0, 0.4 + j * 0.45), 0.32, 0.04, k.M((0.2, 0.55, 0.2), 0.7), rot=(D(10), D(j * 9), 0), seg=16, rseg=4) for j in range(5)]
    elif K in ('rock_arch', 'ice_arch', 'root_arch', 'ring_arch', 'torii'):
        if K == 'ring_arch': k.torus((0, 0, 1.6), 1.4, 0.15, mm, rot=(D(90), 0, 0), seg=32, rseg=8); [k.ico((1.4 * math.cos(a), 0, 1.6 + 1.4 * math.sin(a)), 0.16, mg, sub=1) for a in (0.5, 1.6, 2.6)]
        elif K == 'torii': k.cyl((-1, 0, 1.3), 0.12, 2.6, k.M((0.85, 0.15, 0.12), 0.5), seg=10); k.cyl((1, 0, 1.3), 0.12, 2.6, k.M((0.85, 0.15, 0.12), 0.5), seg=10); k.box((0, 0, 2.7), (1.6, 0.18, 0.1), k.M((0.85, 0.15, 0.12), 0.5), bevel=0.2); k.box((0, 0, 2.25), (1.25, 0.1, 0.07), k.M((0.85, 0.15, 0.12), 0.5), bevel=0.2)
        else: arch({'ice_arch': k.M((0.75, 0.9, 1), 0.1, 0, 0.3), 'root_arch': wood}.get(K, stone))
    elif K in ('ice_spike', 'obsidian_spike', 'antenna_rock', 'lightning_rod'):
        if K == 'lightning_rod': k.cyl((0, 0, 1.6), 0.06, 3.2, k.M((0.7, 0.7, 0.75), 0.3, 1), seg=8); k.ico((0, 0, 3.3), 0.15, mg, sub=1); k.box((0, 0, 0.12), (0.35, 0.35, 0.12), stone, bevel=0.2)
        else:
            m = {'ice_spike': k.M((0.75, 0.9, 1), 0.08, 0, 0.3), 'obsidian_spike': k.M((0.08, 0.05, 0.1), 0.1, 0.3), 'antenna_rock': stone}[K]
            for j in range(5): a = j * 1.25; k.cone((0.35 * math.cos(a), 0.35 * math.sin(a), 0.6), 0.25, 1.5 - j * 0.15, m, rot=(D(12) * math.sin(a), -D(12) * math.cos(a), 0), seg=6, smooth=False)
            if K == 'antenna_rock': k.ico((0, 0, 1.5), 0.15, mg, sub=1)
    elif K in ('coral_branch', 'coral_fan', 'anemone'):
        if K == 'coral_fan': k.plate((0, 0, 0.9), (0.8, 0.05, 0.8), mm, rot=(0, 0, 0)); k.cyl((0, 0, 0.2), 0.06, 0.4, mm, seg=6)
        elif K == 'anemone': k.cyl((0, 0, 0.2), 0.3, 0.4, mm, seg=12); [k.cyl((0.22 * math.cos(j * 0.6), 0.22 * math.sin(j * 0.6), 0.55), 0.03, 0.35, mg, rot=(D(20) * math.sin(j), D(20) * math.cos(j), 0), seg=5) for j in range(10)]
        else:
            for j in range(7): a = j * 0.9; k.cyl((0.15 * math.cos(a), 0.15 * math.sin(a), 0.6), 0.06, 1.2 - j * 0.08, k.M(mix(glow, (1, 0.4, 0.5), 0.4), 0.6), rot=(D(25) * math.sin(a), -D(25) * math.cos(a), 0), seg=6)
    elif K in ('shell', 'skull', 'fossil_bone', 'anchor', 'urn', 'lantern', 'snowman', 'meteor', 'planet_orb', 'asteroid', 'floating_rock', 'pebbles', 'petal_pile', 'lily', 'egg_sac', 'alien_pod', 'dino_egg_nest', 'bubble_rock', 'wisp_lamp', 'rune_stone', 'fairy_ring', 'igloo_block', 'vent', 'magma_pool', 'goo_pool', 'temple_block', 'volcano_cone', 'tentacle_plant', 'windmill', 'bridge_small', 'cactus'):
        prop_special(k, K, mm, ma, mg, stone, wood, mcry)
    else: prop_special(k, K, mm, ma, mg, stone, wood, mcry)
    return k
def prop_special(k, K, mm, ma, mg, stone, wood, mcry):
    R = k.R
    if K == 'cactus': k.cyl((0, 0, 0.9), 0.25, 1.8, k.M((0.3, 0.6, 0.3), 0.7), seg=10); k.ball((0, 0, 1.8), (0.25,) * 3, k.M((0.3, 0.6, 0.3), 0.7)); k.cyl((0.4, 0, 1.0), 0.13, 0.6, k.M((0.3, 0.6, 0.3), 0.7), seg=8); k.cyl((0.25, 0, 0.75), 0.12, 0.4, k.M((0.3, 0.6, 0.3), 0.7), rot=(0, D(90), 0), seg=8); k.ball((0, 0, 1.95), (0.1, 0.1, 0.06), k.M((1, 0.4, 0.6), 0.5))
    elif K == 'shell': k.ball((0, 0, 0.25), (0.5, 0.45, 0.25), mm, seg=16); [k.box((0, 0, 0.3), (0.02, 0.45, 0.25), ma, rot=(0, 0, D(-50 + j * 25)), bevel=0) for j in range(5)]
    elif K == 'skull': k.ball((0, 0, 0.4), (0.4, 0.45, 0.38), k.M((0.92, 0.88, 0.8), 0.7)); k.ball((0.15, -0.38, 0.45), (0.1, 0.05, 0.1), k.M((0.05, 0.05, 0.05), 0.8)); k.ball((-0.15, -0.38, 0.45), (0.1, 0.05, 0.1), k.M((0.05, 0.05, 0.05), 0.8)); k.cone((0.35, 0, 0.6), 0.08, 0.6, k.M((0.92, 0.88, 0.8), 0.7), rot=(0, D(60), 0)); k.cone((-0.35, 0, 0.6), 0.08, 0.6, k.M((0.92, 0.88, 0.8), 0.7), rot=(0, D(-60), 0))
    elif K == 'fossil_bone':
        for j in range(6): k.cyl((0, -0.6 + j * 0.25, 0.15), 0.04, 0.8, k.M((0.9, 0.85, 0.7), 0.7), rot=(0, D(90), 0), seg=6)
        k.cyl((0, 0, 0.15), 0.07, 1.6, k.M((0.9, 0.85, 0.7), 0.7), rot=(D(90), 0, 0), seg=8)
    elif K == 'anchor': m = k.M((0.35, 0.33, 0.3), 0.5, 0.8); k.cyl((0, 0, 1.0), 0.08, 1.8, m, seg=8); k.torus((0, 0, 1.95), 0.15, 0.04, m, rot=(D(90), 0, 0), seg=12, rseg=4); k.torus((0, 0, 0.45), 0.5, 0.06, m, rot=(D(90), 0, 0), seg=16, rseg=5); k.box((0, 0, 1.6), (0.35, 0.05, 0.05), m, bevel=0.2)
    elif K == 'urn': k.ball((0, 0, 0.45), (0.35, 0.35, 0.42), ma); k.cyl((0, 0, 0.9), 0.16, 0.2, ma, seg=12); k.torus((0, 0, 0.5), 0.35, 0.03, k.M((1, 0.78, 0.25), 0.3, 1), seg=20, rseg=4)
    elif K == 'lantern': k.cyl((0, 0, 0.9), 0.05, 1.8, wood, seg=6); k.box((0, 0, 1.9), (0.22, 0.22, 0.3), k.M((0.85, 0.15, 0.12), 0.5), bevel=0.3); k.ball((0, 0, 1.9), (0.15,) * 3, mg)
    elif K == 'snowman': w = k.M((0.97, 0.98, 1), 0.7); k.ball((0, 0, 0.45), (0.45,) * 3, w); k.ball((0, 0, 1.1), (0.32,) * 3, w); k.ball((0, 0, 1.55), (0.22,) * 3, w); k.cone((0, -0.28, 1.55), 0.05, 0.25, k.M((1, 0.5, 0.1), 0.6), rot=(D(90), 0, 0), seg=6)
    elif K in ('meteor', 'asteroid'): k.ico((0, 0, 0.7), 0.7, stone, sub=2, sc=(0.8, 0.7, 0.6)); [k.ball((R.uniform(-0.5, 0.5), R.uniform(-0.5, 0.5), 0.9), (0.15, 0.15, 0.05), k.M((0.2, 0.2, 0.2), 0.9), seg=8) for _ in range(4)]; K == 'meteor' and k.cone((0, 0.8, 1.1), 0.5, 1.4, mg, rot=(D(-70), 0, 0), seg=8)
    elif K == 'planet_orb': k.ball((0, 0, 1.0), (0.7,) * 3, mm, seg=24); k.torus((0, 0, 1.0), 1.1, 0.06, ma, rot=(D(70), D(15), 0), seg=32, rseg=4); k.cyl((0, 0, 0.15), 0.3, 0.3, stone, seg=10)
    elif K == 'floating_rock': k.ico((0, 0, 1.3), 0.7, stone, sub=1, sc=(0.9, 0.8, 0.45)); k.cone((0, 0, 0.75), 0.6, 0.9, stone, rot=(D(180), 0, 0), seg=7, smooth=False); k.ball((0, 0, 1.6), (0.7, 0.6, 0.12), mm)
    elif K == 'pebbles': [k.ico((R.uniform(-0.8, 0.8), R.uniform(-0.8, 0.8), 0.08), R.uniform(0.08, 0.18), stone, sub=1, sc=(0.2, 0.15, 0.08)) for _ in range(12)]
    elif K == 'petal_pile': [k.ball((R.uniform(-0.8, 0.8), R.uniform(-0.8, 0.8), 0.03), (0.07, 0.05, 0.012), k.M((1, 0.7, 0.85), 0.6), rot=(0, 0, R.uniform(0, 3)), seg=6) for _ in range(30)]
    elif K == 'lily': k.cyl((0, 0, 0.02), 0.6, 0.03, k.M((0.3, 0.6, 0.3), 0.6), seg=16); [k.ball((0.1 * math.cos(j), 0.1 * math.sin(j), 0.1), (0.1, 0.04, 0.08), k.M((1, 0.8, 0.9), 0.5), rot=(0, 0, j), seg=8) for j in range(6)]
    elif K in ('egg_sac', 'alien_pod'): [k.ball((0.3 * math.cos(j * 1.2), 0.3 * math.sin(j * 1.2), 0.3 + (j % 2) * 0.2), (0.25, 0.25, 0.3), k.M((0.6, 0.9, 0.4), 0.2, 0, 0.6, alpha=0.75), seg=12) for j in range(5 if K == 'egg_sac' else 1)]; K == 'alien_pod' and (k.ball((0, 0, 0.8), (0.5, 0.5, 0.8), ma), k.ico((0, 0, 0.9), 0.25, mg, sub=1))
    elif K == 'dino_egg_nest': k.torus((0, 0, 0.15), 0.6, 0.18, wood, seg=20, rseg=6); [k.ball((0.2 * math.cos(j * 2.1), 0.2 * math.sin(j * 2.1), 0.3), (0.15, 0.15, 0.2), k.M((0.9, 0.85, 0.7), 0.6)) for j in range(3)]
    elif K == 'bubble_rock': k.ico((0, 0, 0.4), 0.5, stone, sub=1); [k.ball((R.uniform(-0.2, 0.2), R.uniform(-0.2, 0.2), 0.9 + j * 0.3), (0.08 + j * 0.02,) * 3, k.M((0.8, 0.95, 1), 0.05, 0, 0.3, alpha=0.4), seg=8) for j in range(4)]
    elif K == 'wisp_lamp': k.cyl((0, 0, 0.8), 0.05, 1.6, wood, seg=6); k.ico((0, 0, 1.75), 0.18, mg, sub=2); k.torus((0, 0, 1.75), 0.28, 0.02, ma, rot=(D(60), 0, 0), seg=16, rseg=4)
    elif K == 'rune_stone': k.box((0, 0, 0.8), (0.35, 0.2, 0.8), stone, bevel=0.25); [k.box((0, -0.21, 0.4 + j * 0.3), (0.12 + 0.06 * (j % 2), 0.005, 0.03), mg, bevel=0) for j in range(4)]
    elif K == 'fairy_ring': [k.cyl((0.8 * math.cos(j / 10 * math.tau), 0.8 * math.sin(j / 10 * math.tau), 0.1), 0.04, 0.2, k.M((0.95, 0.9, 0.8), 0.7), seg=6) or k.ball((0.8 * math.cos(j / 10 * math.tau), 0.8 * math.sin(j / 10 * math.tau), 0.2), (0.1, 0.1, 0.05), mg, seg=8) for j in range(10)]
    elif K == 'igloo_block': w = k.M((0.9, 0.95, 1), 0.5); [k.box((math.cos(j / 8 * math.tau) * 0.8, math.sin(j / 8 * math.tau) * 0.8, 0.2 + (j % 2) * 0.4), (0.25, 0.25, 0.18), w, rot=(0, 0, j / 8 * math.tau), bevel=0.2) for j in range(8)]
    elif K in ('vent', 'volcano_cone'): k.cone((0, 0, 0.6), 1.0 if K == 'volcano_cone' else 0.6, 1.2, k.M((0.15, 0.1, 0.08), 0.9), r2=0.3, seg=10, smooth=False); k.cyl((0, 0, 1.2), 0.28, 0.04, mg, seg=10); K == 'vent' and k.ball((0, 0, 1.7), (0.3, 0.3, 0.5), k.M((0.4, 0.4, 0.4), 0.9, 0, 0, alpha=0.5), seg=10)
    elif K in ('magma_pool', 'goo_pool'): k.torus((0, 0, 0.08), 0.9, 0.15, stone, seg=24, rseg=5); k.cyl((0, 0, 0.06), 0.9, 0.04, mg, seg=24)
    elif K == 'temple_block': k.box((0, 0, 0.5), (0.7, 0.7, 0.5), stone, bevel=0.1); k.box((0, -0.71, 0.5), (0.4, 0.01, 0.3), mg, bevel=0); k.box((0, 0, 1.1), (0.55, 0.55, 0.1), ma, bevel=0.2)
    elif K == 'tentacle_plant': [k.chain([(0.2 * math.cos(j * 1.6) + 0.05 * i * math.cos(j), 0.2 * math.sin(j * 1.6), 0.1 + i * 0.22) for i in range(7)], [0.1 - i * 0.012 for i in range(7)], ma, seg=8) for j in range(4)]; k.ico((0, 0, 0.15), 0.25, mg, sub=1)
    elif K == 'windmill': k.cone((0, 0, 1.3), 0.5, 2.6, k.M((0.9, 0.88, 0.82), 0.7), r2=0.3, seg=8); [k.plate((0, -0.45, 2.4), (0.12, 0.02, 0.9), wood, rot=(0, D(j * 90), 0)) for j in range(4)]
    elif K == 'bridge_small': k.box((0, 0, 0.35), (1.6, 0.5, 0.06), wood, rot=(0, D(0), 0), bevel=0.2); [k.cyl((x, y, 0.55), 0.04, 0.5, k.M((0.85, 0.15, 0.12), 0.5), seg=6) for x in (-1.4, 0, 1.4) for y in (-0.45, 0.45)]
    elif K == 'goo_pool': pass
    else:  # common extras
        if K == 'sky_island': k.ball((0, 0, 1.2), (2.0, 2.0, 0.3), mm, seg=16); k.cone((0, 0, 0.5), 1.8, 1.4, stone, rot=(D(180), 0, 0), seg=9, smooth=False)
        elif K == 'hill_tile': k.ball((0, 0, 0), (2.5, 2.5, 0.8), mm, seg=16)
        elif K == 'fence_post': k.box((0, 0, 0.5), (0.08, 0.08, 0.5), wood, bevel=0.2); k.box((0, 0, 0.75), (1.0, 0.04, 0.06), wood, bevel=0.2); k.box((0, 0, 0.4), (1.0, 0.04, 0.06), wood, bevel=0.2)
        elif K == 'sign_post': k.box((0, 0, 0.7), (0.06, 0.06, 0.7), wood, bevel=0.2); k.box((0.25, 0, 1.25), (0.4, 0.04, 0.16), wood, bevel=0.2); k.box((-0.2, 0, 1.0), (0.35, 0.04, 0.13), wood, rot=(0, 0, D(8)), bevel=0.2)
        elif K == 'bench': k.box((0, 0, 0.45), (0.8, 0.25, 0.04), wood, bevel=0.2); k.box((0, 0.24, 0.75), (0.8, 0.03, 0.18), wood, bevel=0.2); [k.box((x, 0, 0.22), (0.04, 0.22, 0.22), k.M((0.2, 0.2, 0.22), 0.4, 0.8), bevel=0.2) for x in (-0.7, 0.7)]
        elif K == 'street_lamp': k.cyl((0, 0, 1.4), 0.06, 2.8, k.M((0.2, 0.2, 0.22), 0.4, 0.8), seg=8); k.ball((0, 0, 2.9), (0.2, 0.2, 0.25), k.M((1, 0.9, 0.6), 0.2, 0, 3)); k.cone((0, 0, 3.1), 0.25, 0.15, k.M((0.2, 0.2, 0.22), 0.4, 0.8), seg=8)
        else: k.ico((0, 0, 0.4), 0.5, stone, sub=1)
# ---------------- 건축 ----------------
def build_building(s):
    k = Kit(s['seed']); K = s['kind']; R = k.R
    wood = k.M((0.55, 0.38, 0.22), 0.85); stone = k.M((0.62, 0.62, 0.66), 0.85); roof = k.M((0.85, 0.3, 0.25), 0.6); metal = k.M((0.6, 0.62, 0.68), 0.3, 0.9); gold = k.M(GOLD, 0.25, 1); glow = k.M((0.4, 1, 0.85), 0.2, 0, 3); white = k.M((0.95, 0.95, 0.92), 0.6)
    if K == 'portal':
        main, acc, gl = [tuple(c) for c in s['pal']]; m = k.M(mix(acc, (0.5, 0.5, 0.5), 0.4), 0.7)
        for j in range(12): a = j / 12 * math.pi; k.box((1.5 * math.cos(a), 0, 0.2 + 1.5 * math.sin(a) + 0.3), (0.28, 0.35, 0.22), m, rot=(0, -a + D(90), 0), bevel=0.2)
        k.ball((0, 0, 1.1), (1.25, 0.06, 1.25), k.M(gl, 0.1, 0, 3, alpha=0.65), seg=24); k.box((0, 0, 0.08), (1.9, 0.6, 0.08), stone, bevel=0.2); k.ico((0, 0, 2.15), 0.18, k.M(gl, 0.2, 0, 4), sub=1)
    elif K == 'base_platform': k.cyl((0, 0, 0.2), 6, 0.4, stone, seg=40); k.cyl((0, 0, 0.42), 5.6, 0.04, k.M((0.45, 0.75, 0.45), 0.8), seg=40); [k.box((5.8 * math.cos(j / 16 * math.tau), 5.8 * math.sin(j / 16 * math.tau), 0.5), (0.25, 0.25, 0.12), stone, bevel=0.2) for j in range(16)]
    elif K == 'hatch_pedestal': k.cyl((0, 0, 0.3), 0.6, 0.6, stone, seg=16); k.torus((0, 0, 0.62), 0.5, 0.06, gold, seg=24, rseg=5); k.cyl((0, 0, 0.63), 0.45, 0.04, glow, seg=20); [k.crystal((0.62 * math.cos(j * 1.57), 0.62 * math.sin(j * 1.57), 0.75), 0.05, 0.3, glow) for j in range(4)]
    elif K == 'pet_pen': [k.box((2 * math.cos(j / 12 * math.tau), 2 * math.sin(j / 12 * math.tau), 0.4), (0.07, 0.07, 0.4), wood, bevel=0.3) for j in range(12)]; k.torus((0, 0, 0.6), 2, 0.04, wood, seg=36, rseg=4); k.torus((0, 0, 0.3), 2, 0.04, wood, seg=36, rseg=4); k.cyl((0, 0, 0.03), 1.9, 0.06, k.M((0.5, 0.75, 0.4), 0.9), seg=30)
    elif K == 'fence': [k.box((x, 0, 0.45), (0.06, 0.06, 0.45), wood, bevel=0.3) or k.cone((x, 0, 0.95), 0.07, 0.12, wood, seg=4) for x in (-1.5, -0.75, 0, 0.75, 1.5)]; k.box((0, 0, 0.65), (1.6, 0.03, 0.05), wood, bevel=0.2); k.box((0, 0, 0.3), (1.6, 0.03, 0.05), wood, bevel=0.2)
    elif K == 'gate': k.box((-1.5, 0, 1.2), (0.25, 0.25, 1.2), stone, bevel=0.2); k.box((1.5, 0, 1.2), (0.25, 0.25, 1.2), stone, bevel=0.2); k.box((0, 0, 2.55), (1.9, 0.3, 0.2), wood, bevel=0.2); k.box((0, -0.32, 2.55), (0.8, 0.02, 0.16), k.M((0.2, 0.5, 0.9), 0.5), bevel=0); [k.cone((x, 0, 2.6), 0.3, 0.5, roof, seg=4) for x in (-1.5, 1.5)]
    elif K == 'safe_arch': k.torus((0, 0, 0.2), 2.3, 0.08, glow, rot=(D(90), 0, 0), seg=40, rseg=6); [k.box((2.3 * math.cos(a), 0, 2.3 * math.sin(a) + 0.2), (0.2, 0.2, 0.2), white, rot=(0, -a, 0), bevel=0.3) for a in [j / 6 * math.pi for j in range(7)]]
    elif K == 'shop_stall': k.box((0, 0, 0.5), (1.2, 0.5, 0.5), wood, bevel=0.15); [k.cyl((x, y, 1.3), 0.05, 1.6, wood, seg=6) for x in (-1.1, 1.1) for y in (-0.45, 0.45)]; [k.box((0, -0.2 + j * 0.16, 2.15), (1.35, 0.08, 0.04), roof if j % 2 else white, rot=(D(-20), 0, 0), bevel=0.1) for j in range(5)]; [k.ico((x, -0.2, 1.1), 0.12, k.M((1, 0.8, 0.2), 0.3, 0.6), sub=1) for x in (-0.6, 0, 0.6)]
    elif K == 'index_kiosk': k.box((0, 0, 0.9), (0.4, 0.3, 0.9), metal, bevel=0.2); k.box((0, -0.31, 1.35), (0.32, 0.01, 0.3), glow, bevel=0); k.box((0, 0, 1.9), (0.45, 0.35, 0.1), gold, bevel=0.3); k.ball((0, 0, 2.2), (0.18,) * 3, k.M((0.9, 0.85, 0.6), 0.4))
    elif K == 'money_counter': k.box((0, 0, 0.6), (0.7, 0.3, 0.6), metal, bevel=0.15); k.box((0, -0.31, 0.9), (0.6, 0.01, 0.2), k.M((0.2, 1, 0.4), 0.2, 0, 3), bevel=0); [k.cyl((x, 0, 1.25 + (j % 2) * 0.05), 0.12, 0.05 + j * 0.03, gold, seg=12) for j, x in enumerate((-0.4, -0.15, 0.15, 0.4))]
    elif K == 'tower': k.cyl((0, 0, 2), 0.9, 4, stone, seg=14); k.cyl((0, 0, 4.15), 1.1, 0.3, stone, seg=14); [k.box((1.05 * math.cos(j / 8 * math.tau), 1.05 * math.sin(j / 8 * math.tau), 4.45), (0.18, 0.18, 0.18), stone, bevel=0.2) for j in range(8)]; k.cone((0, 0, 5.2), 1.1, 1.5, roof, seg=14); k.box((0, -0.91, 2.6), (0.15, 0.01, 0.3), glow, bevel=0)
    elif K == 'bridge': k.box((0, 0, 0.6), (0.9, 3.0, 0.1), wood, bevel=0.15); [k.box((x, y, 0.95), (0.05, 0.05, 0.35), wood, bevel=0.3) for x in (-0.85, 0.85) for y in (-2.8, -1.4, 0, 1.4, 2.8)]; [k.box((x, 0, 1.25), (0.04, 3.0, 0.04), wood, bevel=0.3) for x in (-0.85, 0.85)]; [k.cyl((0, y, 0.3), 0.15, 0.6, stone, seg=8) for y in (-2.6, 2.6)]
    elif K == 'banner': k.cyl((0, 0, 1.6), 0.05, 3.2, wood, seg=6); k.plate((0.45, 0, 2.6), (0.42, 0.02, 0.6), k.M((0.6, 0.2, 0.8), 0.6)); k.ico((0.45, -0.03, 2.65), 0.15, gold, sub=1); k.ball((0, 0, 3.25), (0.08,) * 3, gold)
    elif K == 'lamp_post': k.cyl((0, 0, 1.3), 0.07, 2.6, metal, seg=8); k.box((0.35, 0, 2.5), (0.35, 0.03, 0.03), metal, bevel=0.3); k.ball((0.65, 0, 2.3), (0.15, 0.15, 0.2), k.M((1, 0.9, 0.6), 0.2, 0, 4)); k.cone((0.65, 0, 2.45), 0.2, 0.15, metal, seg=8)
    elif K == 'stairs': [k.box((0, j * 0.35, 0.1 + j * 0.2), (1.0, 0.18, 0.1 + j * 0.0), stone, bevel=0.15) for j in range(6)]
    elif K == 'upgrade_station': k.cyl((0, 0, 0.15), 1.0, 0.3, metal, seg=20); k.cyl((0, 0, 1.0), 0.15, 1.5, metal, seg=10); k.torus((0, 0, 1.2), 0.5, 0.05, glow, seg=24, rseg=5); k.torus((0, 0, 1.6), 0.35, 0.05, gold, seg=24, rseg=5); k.cone((0, 0, 2.0), 0.2, 0.4, glow, seg=6)
    elif K == 'fishing_dock': k.box((0, 0, 0.5), (1.0, 2.5, 0.08), wood, bevel=0.15); [k.cyl((x, y, 0.2), 0.08, 0.8, wood, seg=6) for x in (-0.9, 0.9) for y in (-2.3, 0, 2.3)]; k.box((0, -2.3, 0.9), (0.4, 0.3, 0.35), wood, bevel=0.2)
    elif K == 'event_stage': k.cyl((0, 0, 0.3), 3, 0.6, stone, seg=32); k.torus((0, 0, 0.62), 2.9, 0.06, gold, seg=40, rseg=5); [k.cyl((2.6 * math.cos(a), 2.6 * math.sin(a), 1.8), 0.15, 2.4, white, seg=10) for a in (0, 2.1, 4.2)]; k.torus((0, 0, 3.1), 2.6, 0.1, glow, seg=40, rseg=5)
    elif K == 'spawn_pad': k.cyl((0, 0, 0.1), 1.5, 0.2, stone, seg=24); [k.box((0, 0, 0.21), (1.2, 0.08, 0.01), glow, rot=(0, 0, j * math.pi / 4), bevel=0) for j in range(4)]; k.torus((0, 0, 0.22), 1.3, 0.04, glow, seg=32, rseg=4)
    elif K == 'expansion_floor': k.box((0, 0, 0.15), (3, 3, 0.15), stone, bevel=0.05); [k.box((x, y, 0.31), (0.7, 0.7, 0.01), k.M((0.7, 0.72, 0.75), 0.8) if (int(x + y) % 2) else stone, bevel=0) for x in (-1.5, 0, 1.5) for y in (-1.5, 0, 1.5)]
    elif K == 'storage_crate': k.box((0, 0, 0.45), (0.45, 0.45, 0.45), wood, bevel=0.15); [k.box((0, 0, 0.45), (0.47, 0.47, 0.05), metal, rot=r, bevel=0) for r in ((0, 0, 0), (D(90), 0, 0))]
    elif K == 'fountain': k.cyl((0, 0, 0.3), 1.6, 0.6, stone, seg=28); k.cyl((0, 0, 0.58), 1.45, 0.04, k.M((0.4, 0.7, 1), 0.05, 0, 0.3, alpha=0.7), seg=28); k.cyl((0, 0, 1.0), 0.2, 1.0, stone, seg=12); k.cyl((0, 0, 1.5), 0.7, 0.15, stone, seg=20); k.ball((0, 0, 1.9), (0.2, 0.2, 0.4), k.M((0.6, 0.85, 1), 0.05, 0, 0.5, alpha=0.6))
    elif K == 'mailbox': k.cyl((0, 0, 0.5), 0.05, 1.0, wood, seg=6); k.box((0, 0, 1.1), (0.25, 0.4, 0.2), roof, bevel=0.3); k.box((0.27, 0.1, 1.25), (0.02, 0.03, 0.15), k.M((1, 0.85, 0.2), 0.4), bevel=0)
    return k
# ---------------- 장비 ----------------
def build_equipment(s):
    k = Kit(s['seed']); K, t = s['kind'], s['tier']; tc = [(0.55, 0.38, 0.22), (0.6, 0.62, 0.68), (0.2, 0.7, 0.4), (0.2, 0.45, 0.95), (0.6, 0.3, 0.9), (1, 0.6, 0.1), (0.9, 0.2, 0.3), (1, 0.85, 0.35)][t % 8]
    m = k.M(tc, 0.4, 0.5 if t > 0 else 0); g = k.M(mix(tc, WHITE, 0.3), 0.2, 0, 2.5); gold = k.M(GOLD, 0.25, 1); dark = k.M((0.1, 0.1, 0.12), 0.6)
    if K == 'rod':
        k.cyl((0, 0, 1.1), 0.03 - t * 0.001, 2.2, m, rot=(D(-15), 0, 0), seg=8); k.cyl((0, 0.07, 0.25), 0.045, 0.5, dark, rot=(D(-15), 0, 0), seg=8); k.torus((0.07, 0.12, 0.45), 0.08, 0.02, k.M((0.7, 0.7, 0.72), 0.3, 1), rot=(0, D(90), 0), seg=12, rseg=4)
        for j in range(4): k.torus((0, -0.04 - j * 0.12, 0.7 + j * 0.42), 0.03, 0.006, gold, rot=(D(75), 0, 0), seg=8, rseg=3)
        if t >= 3: k.ico((0, 0.12, 0.05), 0.07, g, sub=1)
        if t >= 5: k.crystal((0, -0.3, 2.2), 0.05, 0.2, g, rot=(D(-15), 0, 0))
        if t >= 7: k.torus((0, -0.28, 2.1), 0.15, 0.015, gold, rot=(D(75), 0, 0), seg=16, rseg=4)
    elif K == 'bobber': k.ball((0, 0, 0.15), (0.12, 0.12, 0.12), k.M((0.9, 0.1, 0.1), 0.4)); k.ball((0, 0, 0.2), (0.12, 0.12, 0.08), k.M(WHITE, 0.4)); k.cyl((0, 0, 0.36), 0.015, 0.15, dark, seg=6); t >= 1 and k.ico((0, 0, 0.45), 0.04, g, sub=1); t >= 3 and k.torus((0, 0, 0.15), 0.15, 0.015, gold, seg=16, rseg=4)
    elif K == 'net': k.cyl((0, 0, 0.6), 0.025, 1.2, m, seg=6); k.torus((0, 0, 1.4), 0.3, 0.02, m, rot=(D(90), 0, 0), seg=20, rseg=4); k.ball((0, 0.05, 1.3), (0.28, 0.25, 0.32), k.M((0.9, 0.9, 0.85), 0.8, 0, 0, alpha=0.5), seg=10)
    elif K == 'backpack': k.box((0, 0, 0.45), (0.3, 0.18, 0.4), m, bevel=0.3); k.box((0, -0.2, 0.35), (0.22, 0.05, 0.18), k.M(mix(tc, (0, 0, 0), 0.3), 0.6), bevel=0.3); k.box((0, 0, 0.88), (0.3, 0.19, 0.06), k.M(mix(tc, (0, 0, 0), 0.3), 0.6), bevel=0.4); [k.box((x, 0.2, 0.5), (0.04, 0.02, 0.35), dark, bevel=0.3) for x in (-0.18, 0.18)]; t >= 2 and k.ico((0, -0.26, 0.35), 0.05, g, sub=1); t >= 4 and k.mirror([k.plate((0.35, 0.1, 0.65), (0.3, 0.02, 0.12), g, rot=(0, D(-20), 0))])
    elif K == 'hat':
        if t == 0: k.cyl((0, 0, 0.05), 0.35, 0.03, m, seg=20); k.cyl((0, 0, 0.18), 0.2, 0.25, m, seg=16)
        elif t == 1: k.cone((0, 0, 0.3), 0.25, 0.6, k.M((0.3, 0.2, 0.6), 0.6), seg=12); k.cyl((0, 0, 0.02), 0.38, 0.03, k.M((0.3, 0.2, 0.6), 0.6), seg=20); k.ico((0.1, -0.1, 0.4), 0.04, g, sub=1)
        elif t == 2: k.ball((0, 0, 0.05), (0.25, 0.28, 0.15), m, seg=14); k.box((0, -0.28, 0.02), (0.15, 0.12, 0.01), m, bevel=0.4)
        elif t == 3: [k.cone((0.18 * math.cos(j / 5 * math.tau), 0.18 * math.sin(j / 5 * math.tau), 0.12), 0.05, 0.18, gold, seg=4) for j in range(5)]; k.torus((0, 0, 0.04), 0.2, 0.04, gold, seg=20, rseg=5); [k.ico((0.2 * math.cos(j / 5 * math.tau), 0.2 * math.sin(j / 5 * math.tau), 0.05), 0.03, k.M((0.9, 0.1, 0.2), 0.2, 0.2), sub=0) for j in range(5)]
        else: k.torus((0, 0, 0.35), 0.22, 0.03, gold, seg=24, rseg=5); k.ball((0, 0, 0.05), (0.24, 0.26, 0.14), k.M(WHITE, 0.4), seg=14); k.mirror([k.plate((0.25, 0.05, 0.12), (0.18, 0.02, 0.08), k.M(WHITE, 0.3, 0, 0.5), rot=(0, D(-30), 0))])
    return k
# ---------------- 기타 ----------------
def build_misc(s):
    k = Kit(s['seed']); K, t = s['kind'], s['tier']; R = k.R; gold = k.M(GOLD, 0.25, 1); wood = k.M((0.5, 0.33, 0.18), 0.85)
    if K == 'coin': k.cyl((0, 0, 0.06), 0.25, 0.06, gold, rot=(D(90), 0, 0), seg=24); k.box((0, -0.035, 0.06), (0.05, 0.01, 0.12), k.M((0.9, 0.65, 0.15), 0.3, 1), bevel=0)
    elif K == 'gem': c = [(0.2, 0.9, 0.5), (0.3, 0.5, 1), (0.9, 0.2, 0.5)][t]; k.cone((0, 0, 0.15), 0.18, 0.3, k.M(c, 0.05, 0.1, 1.2), rot=(D(180), 0, 0), seg=6 + t * 2, smooth=False); k.cone((0, 0, 0.35), 0.18, 0.1, k.M(c, 0.05, 0.1, 1.2), r2=0.1, seg=6 + t * 2, smooth=False)
    elif K == 'chest':
        c = [(0.5, 0.33, 0.18), (0.6, 0.62, 0.68), GOLD, (0.5, 0.3, 0.9), (0.2, 0.9, 0.8)][t]; m = k.M(c, 0.4, 0.3 + t * 0.15)
        k.box((0, 0, 0.3), (0.45, 0.3, 0.28), m, bevel=0.15); k.ball((0, 0, 0.6), (0.45, 0.3, 0.18), m, seg=12); [k.box((x, 0, 0.45), (0.04, 0.31, 0.3), gold if t < 2 else k.M((0.2, 0.2, 0.2), 0.4, 0.8), bevel=0.2) for x in (-0.3, 0.3)]
        k.box((0, -0.31, 0.5), (0.07, 0.02, 0.09), gold, bevel=0.3); t >= 3 and k.ico((0, 0, 0.85), 0.1, k.M(mix(c, WHITE, 0.3), 0.2, 0, 3), sub=1); t >= 4 and k.torus((0, 0, 1.0), 0.2, 0.02, gold, seg=20, rseg=4)
    elif K == 'key': k.torus((0, 0, 0.5), 0.12, 0.03, gold, rot=(D(90), 0, 0), seg=16, rseg=4); k.cyl((0, 0, 0.22), 0.025, 0.4, gold, seg=6); k.box((0.05, 0, 0.08), (0.05, 0.02, 0.025), gold, bevel=0.2); k.box((0.05, 0, 0.16), (0.04, 0.02, 0.02), gold, bevel=0.2)
    elif K == 'crown': k.torus((0, 0, 0.08), 0.25, 0.05, gold, seg=24, rseg=5); [k.cone((0.25 * math.cos(j / 6 * math.tau), 0.25 * math.sin(j / 6 * math.tau), 0.22), 0.06, 0.25, gold, seg=4) for j in range(6)]; [k.ico((0.27 * math.cos(j / 6 * math.tau), 0.27 * math.sin(j / 6 * math.tau), 0.1), 0.035, k.M((0.9, 0.1, 0.25), 0.1, 0.2), sub=0) for j in range(6)]
    elif K == 'trophy': k.box((0, 0, 0.08), (0.2, 0.2, 0.08), k.M((0.15, 0.1, 0.08), 0.6), bevel=0.2); k.cyl((0, 0, 0.3), 0.04, 0.3, gold, seg=8); k.cone((0, 0, 0.6), 0.1, 0.35, gold, r2=0.22, seg=16); k.mirror([k.torus((0.24, 0, 0.62), 0.08, 0.015, gold, rot=(D(90), 0, 0), seg=10, rseg=3)]); t and k.ico((0, 0, 0.9), 0.07, k.M((0.4, 0.8, 1), 0.1, 0, 2), sub=1)
    elif K == 'lantern': k.box((0, 0, 0.25), (0.15, 0.15, 0.2), k.M((0.2, 0.2, 0.22), 0.4, 0.8), bevel=0.2); k.ball((0, 0, 0.25), (0.12, 0.12, 0.16), k.M((1, 0.7, 0.3), 0.2, 0, 4)); k.torus((0, 0, 0.52), 0.06, 0.012, k.M((0.2, 0.2, 0.22), 0.4, 0.8), rot=(D(90), 0, 0), seg=10, rseg=3)
    elif K == 'candy': k.ball((0, 0, 0.12), (0.12, 0.12, 0.12), k.M((1, 0.4, 0.6), 0.3)); k.mirror([k.cone((0.2, 0, 0.12), 0.08, 0.12, k.M((1, 0.9, 0.95), 0.4), rot=(0, D(-90), 0), seg=6)])
    elif K == 'star_fragment': [k.cone((0, 0, 0.25), 0.07, 0.4, k.M((1, 0.95, 0.5), 0.2, 0, 3), rot=(0, D(j * 72), 0), seg=4, smooth=False) for j in range(5)]
    elif K == 'potion': c = [(0.9, 0.2, 0.3), (0.3, 0.5, 1)][t]; k.ball((0, 0, 0.2), (0.16,) * 3, k.M(c, 0.05, 0, 0.8, alpha=0.75)); k.cyl((0, 0, 0.42), 0.05, 0.12, k.M((0.8, 0.9, 1), 0.05, 0, 0, alpha=0.6), seg=10); k.cyl((0, 0, 0.5), 0.055, 0.05, wood, seg=10)
    elif K == 'scroll': k.cyl((0, 0, 0.08), 0.06, 0.5, k.M((0.95, 0.88, 0.7), 0.8), rot=(0, D(90), 0), seg=10); [k.cyl((x, 0, 0.08), 0.03, 0.08, wood, rot=(0, D(90), 0), seg=8) for x in (-0.28, 0.28)]; k.torus((0, 0, 0.08), 0.065, 0.01, k.M((0.8, 0.1, 0.1), 0.5), rot=(0, D(90), 0), seg=12, rseg=3)
    elif K == 'rune': k.box((0, 0, 0.18), (0.15, 0.05, 0.18), k.M((0.5, 0.5, 0.55), 0.8), bevel=0.4); k.box((0, -0.051, 0.18), (0.08, 0.002, 0.1), k.M((0.4, 0.8, 1), 0.2, 0, 3), bevel=0)
    elif K == 'fish':
        cs = [(0.9, 0.5, 0.1), (0.3, 0.6, 0.9), (0.8, 0.8, 0.85), (0.2, 0.8, 0.4), (0.9, 0.2, 0.3), (0.7, 0.4, 0.9), (1, 0.85, 0.3), (0.1, 0.2, 0.35), (0.4, 1, 0.8), (1, 0.6, 0.8), (0.3, 0.3, 0.3), (1, 0.95, 0.6)]
        c = cs[t]; L = 0.4 + (t % 4) * 0.12; m = k.M(c, 0.4, 0.2 if t in (2, 6, 11) else 0, 1.5 if t in (8, 11) else 0)
        k.ball((0, 0, 0.15), (0.1 + (t % 3) * 0.04, L, 0.13 + (t % 2) * 0.05), m, seg=14); k.plate((0, L * 1.05, 0.15), (0.015, 0.12, 0.13 + (t % 3) * 0.03), m, rot=(D(-10 if t % 2 else 10), 0, 0)); k.plate((0, 0, 0.3), (0.012, L * 0.5, 0.07), m)
        k.mirror([k.ball((0.08, -L * 0.6, 0.18), (0.03, 0.015, 0.03), k.M((0.02, 0.02, 0.02), 0.2), seg=6)])
        if t >= 9: k.ico((0, -L * 1.1, 0.35), 0.04, k.M((1, 1, 0.6), 0.2, 0, 4), sub=1); k.cyl((0, -L * 0.9, 0.28), 0.008, 0.2, m, rot=(D(-40), 0, 0), seg=4)
    elif K == 'egg_crack_shell': [k.ball((0.3 * math.cos(j * 1.3), 0.3 * math.sin(j * 1.3), 0.06), (0.15, 0.12, 0.05), k.M((0.95, 0.92, 0.85), 0.5), rot=(D(R.uniform(-40, 40)), D(R.uniform(-40, 40)), 0), seg=8) for j in range(6)]
    elif K == 'halo_prop': k.torus((0, 0, 0.1), 0.35, 0.04, gold, seg=32, rseg=6); [k.ico((0.35 * math.cos(j / 8 * math.tau), 0.35 * math.sin(j / 8 * math.tau), 0.1), 0.03, k.M((1, 1, 0.7), 0.2, 0, 4), sub=0) for j in range(8)]
    elif K == 'rift_shard': [k.crystal((R.uniform(-0.15, 0.15), R.uniform(-0.15, 0.15), 0.3), 0.08, 0.6 - j * 0.08, k.M((0.6, 0.2, 1), 0.05, 0.2, 3), rot=(D(R.uniform(-25, 25)), D(R.uniform(-25, 25)), 0)) for j in range(5)]
    return k
# ---------------- 플레이어 ----------------
def build_player(s):
    k = Kit(s['seed']); v = s['variant']
    outfit = [(0.95, 0.65, 0.2), (0.25, 0.55, 0.95), (0.9, 0.3, 0.4), (0.3, 0.8, 0.5), (0.55, 0.35, 0.85)][v]
    skin = k.M([(1, 0.85, 0.7), (0.85, 0.65, 0.5), (0.6, 0.42, 0.3), (1, 0.88, 0.78), (0.75, 0.55, 0.42)][v], 0.6); cloth = k.M(outfit, 0.6); dark = k.M((0.15, 0.15, 0.2), 0.7); hair = k.M([(0.25, 0.15, 0.08), (0.95, 0.85, 0.4), (0.1, 0.1, 0.12), (0.8, 0.35, 0.15), (0.6, 0.6, 0.9)][v], 0.7)
    k.ball((0, 0, 1.05), (0.32, 0.22, 0.38), cloth, seg=16); k.ball((0, 0, 0.72), (0.3, 0.21, 0.14), dark, seg=14)
    k.ball((0, 0, 1.68), (0.3, 0.29, 0.3), skin, seg=18)
    for x in (-0.11, 0.11): k.ball((x, -0.26, 1.7), (0.055, 0.03, 0.075), k.M((0.05, 0.05, 0.08), 0.2), seg=8); k.ball((x + 0.02, -0.285, 1.73), (0.018,) * 3, k.M(WHITE, 0.2), seg=6)
    k.ball((0, -0.28, 1.58), (0.05, 0.02, 0.02), k.M((0.7, 0.3, 0.3), 0.5), seg=6)
    if v in (0, 3): k.ball((0, 0.03, 1.85), (0.32, 0.31, 0.2), hair, seg=16)
    elif v == 1: k.ball((0, 0.05, 1.82), (0.33, 0.32, 0.24), hair, seg=16); k.ball((0, 0.25, 1.55), (0.2, 0.12, 0.28), hair, seg=12)
    elif v == 2: [k.cone((0.15 * math.cos(j), 0.1 * math.sin(j) + 0.03, 1.95), 0.08, 0.2, hair, rot=(D(20) * math.sin(j), -D(20) * math.cos(j), 0), seg=5) for j in range(7)]
    else: k.cyl((0, 0, 1.95), 0.33, 0.06, k.M((0.4, 0.25, 0.7), 0.6), seg=18); k.cone((0, 0, 2.25), 0.22, 0.55, k.M((0.4, 0.25, 0.7), 0.6), seg=14)
    lim = [k.ball((0.38, 0, 1.08), (0.09, 0.09, 0.3), cloth, rot=(0, D(-12), 0), seg=10), k.ball((0.44, 0, 0.75), (0.08,) * 3, skin, seg=8),
           k.ball((0.13, 0, 0.42), (0.1, 0.1, 0.3), dark, seg=10), k.box((0.13, -0.05, 0.08), (0.1, 0.16, 0.07), k.M((0.95, 0.95, 0.95), 0.5), bevel=0.4)]
    k.mirror(lim)
    k.box((0, 0.24, 1.05), (0.22, 0.1, 0.26), k.M(mix(outfit, (0, 0, 0), 0.35), 0.7), bevel=0.3)  # 등 가방
    return k
