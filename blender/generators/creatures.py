"""크리처(펫·수호자·보스) 빌더. 체형 계열별 골격 → 앵커(머리/등/꼬리) → 특징 부위 → 희귀도 장식."""
import math
from kit import Kit, D
RAR = ['common','uncommon','rare','epic','legendary','mythic','cosmic','secret','eternal','divine']
WHITE, BLACK = (1, 1, 1), (0.02, 0.02, 0.03)
def mix(a, b, t): return tuple(a[i] * (1 - t) + b[i] * t for i in range(3))

def build_creature(spec, boss=False):
    k = Kit(spec.get('seed', 1)); R = k.R
    main, acc, glow = [tuple(c) for c in spec['pal']]
    ri = RAR.index(spec.get('rarity', 'legendary' if boss else 'common'))
    if spec.get('kind') == 'boss': ri = max(ri, 6)
    elif spec.get('kind') == 'guardian': ri = max(ri, 4)
    f = spec['features']; pr = spec.get('proportions', {'body': 1, 'head': 1, 'leg': 1})
    pat = f.get('pattern', 'plain')
    mb = k.M(main, 0.6 if spec['arche'] != 'mech' else 0.35, 0.6 if spec['arche'] in ('mech',) else 0.0)
    mbelly = k.M(mix(main, WHITE, 0.45), 0.7); ma = k.M(acc, 0.45, 0.2); mg = k.M(glow, 0.3, 0, 3.0 + ri * 0.4)
    mhorn = k.M(mix(acc, WHITE, 0.5), 0.35, 0.1); mdark = k.M(BLACK, 0.3); mwhite = k.M(WHITE, 0.2)
    mgold = k.M((1.0, 0.78, 0.25), 0.25, 1.0); mcry = k.M(mix(glow, WHITE, 0.3), 0.08, 0.1, 1.5)
    arche = spec['arche']; sB, sH, sL = pr['body'], pr['head'], pr['leg']
    A = build_body(k, arche, mb, mbelly, ma, mg, mhorn, sB, sH, sL)
    hp, hr, bp, tp, tdir = A['head'], A['hr'], A['back'], A['tail'], A.get('tdir', (0, 1, -0.2))
    # 눈
    n = f.get('eyes', 2); ey, ez = hp[1] - hr * 0.82, hp[2] + hr * 0.18
    xs = [0] if n == 1 else [-hr * 0.42, hr * 0.42] if n == 2 else [-hr * 0.5, 0, hr * 0.5] if n == 3 else [-hr * 0.5, -hr * 0.2, hr * 0.2, hr * 0.5]
    er = hr * (0.34 if n <= 2 else 0.22)
    for i, x in enumerate(xs):
        z = ez + (hr * 0.18 if n == 4 and i in (1, 2) else 0)
        k.ball((x, ey, z), (er, er * 0.55, er * 1.1), mwhite, seg=12)
        k.ball((x, ey - er * 0.42, z - er * 0.1), (er * 0.6, er * 0.3, er * 0.7), mg if ri >= 5 or spec.get('kind') else mdark, seg=10)
        k.ball((x + er * 0.25, ey - er * 0.62, z + er * 0.35), (er * 0.18,) * 3, mwhite, seg=6)
    # 귀
    ears = f.get('ears', 'none'); eo = []
    if ears == 'pointy': eo.append(k.cone((hr * 0.55, hp[1] + hr * 0.1, hp[2] + hr * 0.9), hr * 0.32, hr * 0.9, mb, rot=(D(-10), D(18), 0), seg=4))
    elif ears == 'round': eo.append(k.ball((hr * 0.7, hp[1] + hr * 0.1, hp[2] + hr * 0.75), (hr * 0.3, hr * 0.12, hr * 0.3), mb))
    elif ears == 'long': eo.append(k.ball((hr * 0.4, hp[1] + hr * 0.3, hp[2] + hr * 1.2), (hr * 0.18, hr * 0.1, hr * 0.7), mb, rot=(D(-15), D(10), 0)))
    elif ears == 'fin': eo.append(k.plate((hr * 0.85, hp[1] + hr * 0.2, hp[2] + hr * 0.2), (hr * 0.45, hr * 0.06, hr * 0.3), ma, rot=(0, D(35), D(20))))
    if eo: k.mirror(eo)
    # 뿔
    horns = f.get('horns', 'none'); ho = []
    if horns == 'spike': ho.append(k.cone((hr * 0.35, hp[1], hp[2] + hr * 0.95), hr * 0.13, hr * 0.8, mhorn, rot=(D(-20), D(12), 0)))
    elif horns == 'curved':
        for j in range(4): ho.append(k.ball((hr * (0.45 + j * 0.12), hp[1] + hr * (0.1 + j * 0.22), hp[2] + hr * (0.85 + j * 0.15 - j * j * 0.05)), (hr * (0.13 - j * 0.02),) * 3, mhorn, seg=8))
    elif horns == 'antler':
        ho.append(k.cyl((hr * 0.4, hp[1] + hr * 0.1, hp[2] + hr * 1.2), hr * 0.06, hr * 0.9, mhorn, rot=(0, D(20), 0), seg=6))
        for j in range(3): ho.append(k.cyl((hr * (0.5 + j * 0.15), hp[1] + hr * 0.1, hp[2] + hr * (1.1 + j * 0.2)), hr * 0.04, hr * 0.4, mhorn, rot=(0, D(70), 0), seg=5))
    elif horns == 'crystal': ho.append(k.crystal((hr * 0.3, hp[1], hp[2] + hr * 1.0), hr * 0.16, hr * 0.9, mcry, rot=(D(-10), D(15), 0)))
    elif horns == 'twin_spiral':
        for j in range(5): ho.append(k.ball((hr * (0.35 + 0.1 * math.cos(j * 1.3)), hp[1] + hr * 0.1 * math.sin(j * 1.3), hp[2] + hr * (0.9 + j * 0.22)), (hr * (0.12 - j * 0.017),) * 3, mhorn, seg=8))
    if ho: k.mirror(ho)
    # 등 장식
    back = f.get('back', 'none'); L = A['len']
    for j in range(5 if back != 'none' else 0):
        t = j / 4.0; p = (0, bp[1] + (t - 0.5) * L * 0.8, bp[2] - abs(t - 0.5) * L * 0.12); s = 1 - abs(t - 0.45)
        if back == 'spikes': k.cone(p, 0.08 * s * sB, 0.35 * s * sB, ma, seg=5)
        elif back == 'plates': k.box(p, (0.03, 0.14 * s, 0.16 * s), ma, rot=(D(-15), 0, 0), bevel=0.3)
        elif back == 'crystals': k.crystal(p, 0.07 * s, 0.4 * s, mcry, rot=(D(R.uniform(-20, 20)), D(R.uniform(-20, 20)), 0))
        elif back == 'mushrooms' and j % 2 == 0: k.cyl((p[0], p[1], p[2] + 0.06), 0.025, 0.12, mbelly, seg=6); k.ball((p[0], p[1], p[2] + 0.13), (0.09, 0.09, 0.05), ma, seg=10)
        elif back == 'leaves': k.plate(p, (0.05, 0.14, 0.02), k.M((0.3, 0.7, 0.25), 0.7), rot=(D(40), 0, D(j * 70)))
        elif back == 'gears' and j % 2 == 1: k.torus(p, 0.12, 0.03, mgold, rot=(0, D(90), 0), seg=12, rseg=4)
        elif back == 'fins': k.plate(p, (0.02, 0.12 * s, 0.18 * s), ma, rot=(D(-20), 0, 0))
    # 날개
    wings = f.get('wings', 'none'); wo = []
    if wings != 'none' and arche not in ('slime', 'octo', 'fish'):
        wx, wy, wz = A['wing']; span = 0.9 * sB * (1.4 if boss else 1)
        if wings == 'bat':
            wo.append(k.cyl((wx + span * 0.45, wy, wz + 0.25), 0.03, span, ma, rot=(0, D(70), 0), seg=6))
            for j in range(3): wo.append(k.plate((wx + span * (0.35 + j * 0.15), wy + 0.12 + j * 0.08, wz + 0.05 - j * 0.05), (span * 0.35, 0.02, 0.22 - j * 0.03), k.M(mix(acc, BLACK, 0.3), 0.7), rot=(0, D(-15), D(10 + j * 12))))
        elif wings == 'feather':
            for j in range(5): L_ = span * (0.5 - j * 0.06); wo.append(k.plate((wx + L_ * 0.95, wy + 0.04 + j * 0.07, wz + 0.25 - j * 0.07), (L_, 0.07, 0.022), mbelly if j % 2 else ma, rot=(0, D(-25 + j * 9), D(-8 - j * 3))))
        elif wings == 'insect':
            for j in range(2): wo.append(k.plate((wx + span * 0.4, wy + j * 0.25, wz + 0.15), (span * 0.42, 0.16, 0.01), k.M(mix(glow, WHITE, 0.6), 0.1, 0, 0.3, alpha=0.55), rot=(0, D(-10), D(-20 + j * 40))))
        elif wings == 'crystal':
            for j in range(4): wo.append(k.crystal((wx + span * (0.2 + j * 0.18), wy + j * 0.06, wz + 0.2), 0.06, 0.55 - j * 0.08, mcry, rot=(0, D(60 + j * 8), D(j * 6))))
        elif wings == 'energy':
            for j in range(3): wo.append(k.plate((wx + span * (0.35 + j * 0.1), wy + j * 0.15, wz + 0.25 - j * 0.12), (span * 0.4, 0.015, 0.13), k.M(glow, 0.2, 0, 4, alpha=0.7), rot=(0, D(-25 + j * 15), D(15))))
    if wo: k.mirror(wo)
    # 꼬리
    tail = f.get('tail', 'none'); tx, ty, tz = tp; dx, dy, dz = tdir
    if tail != 'none' and arche not in ('serpent', 'fish', 'slime', 'octo', 'spirit'):
        if tail == 'fluffy': k.ball((tx, ty + 0.35 * dy, tz + 0.25), (0.16, 0.38, 0.17), mb, rot=(D(-35), 0, 0)); k.ball((tx, ty + 0.7 * dy, tz + 0.5), (0.12, 0.15, 0.12), mbelly)
        elif tail in ('segmented', 'whip', 'crystal', 'flame', 'club'):
            nseg = 7 if tail == 'whip' else 5
            for j in range(nseg):
                r = 0.13 * sB * (1 - j / (nseg + 1)); k.ball((tx, ty + dy * (0.2 + j * 0.2), tz + dz * j * 0.2 + 0.03 * math.sin(j)), (r, r * 1.2, r), mb, seg=10)
            end = (tx, ty + dy * (0.25 + nseg * 0.2), tz + dz * nseg * 0.2)
            if tail == 'flame': k.cone(end, 0.12, 0.35, mg, rot=(D(-90 if dy > 0 else 90), 0, 0), seg=6)
            elif tail == 'crystal': k.crystal(end, 0.08, 0.35, mcry, rot=(D(-80), 0, 0))
            elif tail == 'club': k.ico(end, 0.15 * sB, ma, sub=1)
        elif tail == 'fin': k.plate((tx, ty + 0.3 * dy, tz + 0.05), (0.02, 0.28, 0.22), ma, rot=(D(-20), 0, 0))
    # 무늬
    if pat in ('stripes', 'bands'):
        for j in range(4): k.ball((0, A['body'][1] + (j - 1.5) * L * 0.18, A['body'][2] + A['bodyr'][2] * 0.86), (A['bodyr'][0] * 0.7, 0.04, 0.05), k.M(mix(main, BLACK, 0.45), 0.6), seg=10)
    elif pat == 'spots':
        for j in range(6): a = R.uniform(0, math.tau); k.ball((A['bodyr'][0] * 0.8 * math.cos(a), A['body'][1] + R.uniform(-0.4, 0.4) * L, A['body'][2] + A['bodyr'][2] * 0.7), (0.07, 0.07, 0.03), k.M(mix(acc, WHITE, 0.2), 0.6), seg=8)
    rarity_extras(k, ri, hp, hr, A, mg, mgold, mcry, boss)
    if spec.get('special'): special(k, spec['special'], A, mg, mgold, mcry, ma, mb)
    return k

def build_body(k, arche, mb, mbelly, ma, mg, mhorn, sB, sH, sL):
    A = {}
    if arche in ('quadruped', 'dragon', 'mech'):
        L = 1.2 * sB; h = 0.55 * sL + 0.35
        bm = mb if arche != 'mech' else mb
        if arche == 'mech': k.box((0, 0, h), (0.36 * sB, 0.6 * sB, 0.3 * sB), mb, bevel=0.25); k.box((0, -0.05, h - 0.12), (0.3 * sB, 0.5 * sB, 0.12), ma, bevel=0.3)
        else: k.ball((0, 0, h), (0.38 * sB, 0.62 * sB, 0.36 * sB), bm, seg=20); k.ball((0, -0.05, h - 0.12), (0.3 * sB, 0.5 * sB, 0.24 * sB), mbelly, seg=16)
        hr = 0.3 * sH; hy = -0.62 * sB - hr * 0.6; hz = h + 0.3
        k.ball((0, -0.5 * sB, h + 0.15), (0.17, 0.22, 0.25), mb, rot=(D(30), 0, 0))
        if arche == 'mech': k.box((0, hy, hz), (hr, hr * 0.9, hr * 0.8), mb, bevel=0.3); k.box((0, hy - hr * 0.85, hz + hr * 0.1), (hr * 0.8, 0.03, hr * 0.25), mg, bevel=0.2)
        else: k.ball((0, hy, hz), (hr, hr * 1.0, hr * 0.92), mb, seg=18); k.ball((0, hy - hr * 0.75, hz - hr * 0.25), (hr * 0.5, hr * 0.55, hr * 0.4), mbelly, seg=12)
        k.ball((0, hy - hr * 1.28, hz - hr * 0.15), (hr * 0.13, hr * 0.08, hr * 0.1), k.M((0.05, 0.05, 0.05), 0.3), seg=8)
        legs = []
        for y in (-0.38 * sB, 0.38 * sB):
            ll = h - 0.05
            if arche == 'mech': legs += [k.cyl((0.26 * sB, y, ll / 2 + 0.05), 0.07, ll, ma, seg=8), k.ball((0.26 * sB, y, ll * 0.55), (0.1, 0.1, 0.1), mg, seg=8), k.box((0.26 * sB, y - 0.03, 0.04), (0.1, 0.13, 0.04), mb, bevel=0.3)]
            else: legs += [k.ball((0.24 * sB, y, ll * 0.6), (0.11 * sB, 0.13 * sB, ll * 0.55), mb, seg=10), k.ball((0.24 * sB, y - 0.04, 0.05), (0.1, 0.13, 0.06), mhorn if arche == 'dragon' else mbelly, seg=8)]
        k.mirror(legs)
        A.update(head=(0, hy, hz), hr=hr, back=(0, 0, h + 0.36 * sB), tail=(0, 0.6 * sB, h), len=L, body=(0, 0, h), bodyr=(0.38 * sB, 0.62 * sB, 0.36 * sB), wing=(0.25, -0.1, h + 0.3))
    elif arche == 'dino':
        h = 0.7 * sL + 0.3; k.ball((0, 0, h), (0.35 * sB, 0.55 * sB, 0.42 * sB), mb, rot=(D(-25), 0, 0)); k.ball((0, -0.08, h - 0.05), (0.27 * sB, 0.45 * sB, 0.34 * sB), mbelly, rot=(D(-25), 0, 0))
        hr = 0.3 * sH; hy, hz = -0.55 * sB, h + 0.55
        k.ball((0, hy, hz), (hr * 0.9, hr * 1.4, hr * 0.85), mb); k.ball((0, hy - hr * 0.6, hz - hr * 0.45), (hr * 0.75, hr * 0.95, hr * 0.3), mbelly)
        for j in range(5): k.cone((hr * 0.28 * (j - 2) / 2, hy - hr * 1.1, hz - hr * 0.38), 0.025, 0.08, k.M((1, 1, 0.95), 0.3), rot=(D(180), 0, 0), seg=4)
        lg = [k.ball((0.25 * sB, 0.1, h * 0.5), (0.14, 0.2, h * 0.45), mb), k.ball((0.27 * sB, -0.05, 0.05), (0.12, 0.2, 0.06), mhorn), k.ball((0.22 * sB, -0.35 * sB, h + 0.05), (0.05, 0.05, 0.16), mb, rot=(D(40), 0, 0))]
        k.mirror(lg)
        A.update(head=(0, hy - hr * 0.3, hz + hr * 0.1), hr=hr, back=(0, 0.05, h + 0.4 * sB), tail=(0, 0.45 * sB, h - 0.1), tdir=(0, 1, -0.25), len=1.0 * sB, body=(0, 0, h), bodyr=(0.35 * sB, 0.55 * sB, 0.42 * sB), wing=(0.25, 0, h + 0.35))
    elif arche == 'bird':
        h = 0.5 * sL + 0.3; k.ball((0, 0, h), (0.34 * sB, 0.42 * sB, 0.38 * sB), mb); k.ball((0, -0.12, h - 0.05), (0.26 * sB, 0.3 * sB, 0.3 * sB), mbelly)
        hr = 0.25 * sH; hy, hz = -0.3 * sB, h + 0.4 * sB
        k.ball((0, hy, hz), (hr, hr, hr), mb); k.cone((0, hy - hr * 1.15, hz - hr * 0.1), hr * 0.32, hr * 0.8, k.M((1.0, 0.7, 0.15), 0.35), rot=(D(90), 0, 0), seg=6)
        lg = [k.cyl((0.12, 0, h * 0.4), 0.025, h * 0.6, k.M((1.0, 0.7, 0.15), 0.4), seg=6), k.box((0.12, -0.05, 0.02), (0.07, 0.09, 0.02), k.M((1.0, 0.7, 0.15), 0.4), bevel=0.4)]
        k.mirror(lg)
        for j in range(3): k.plate((0.08 * (j - 1), 0.45 * sB, h + 0.05), (0.06, 0.3, 0.02), ma, rot=(D(-25), D((j - 1) * 15), 0))
        A.update(head=(0, hy, hz), hr=hr, back=(0, 0.05, h + 0.36 * sB), tail=(0, 0.4, h), len=0.8 * sB, body=(0, 0, h), bodyr=(0.34 * sB, 0.42 * sB, 0.38 * sB), wing=(0.3 * sB, 0, h + 0.05))
    elif arche in ('serpent', 'fish'):
        if arche == 'serpent':
            n = 11; pts = [(0.22 * math.sin(i * 0.7), -0.6 + i * 0.16 * sB, 0.18 + 0.12 * math.sin(i * 0.5) + (0.35 if i < 2 else 0)) for i in range(n)]
            rad = [0.17 * sB * (1 - i / (n + 3)) for i in range(n)]; k.chain(pts, rad, mb, seg=12)
            for i in range(0, n, 2): k.ball((pts[i][0], pts[i][1], pts[i][2] - rad[i] * 0.5), (rad[i] * 0.75, rad[i] * 0.7, rad[i] * 0.45), mbelly, seg=10)
            hr = 0.26 * sH; hp = (pts[0][0], pts[0][1] - 0.2, pts[0][2] + 0.2); k.ball(hp, (hr * 0.85, hr * 1.25, hr * 0.75), mb)
            A.update(head=hp, hr=hr, back=(0, 0.2, 0.45), tail=pts[-1], len=1.4 * sB, body=(0, 0.2, 0.3), bodyr=(0.2, 0.8, 0.2), wing=(0.15, -0.3, 0.55))
        else:
            h = 0.45; k.ball((0, 0, h), (0.28 * sB, 0.55 * sB, 0.36 * sB), mb, seg=18); k.ball((0, 0, h - 0.12), (0.22 * sB, 0.45 * sB, 0.22 * sB), mbelly)
            k.plate((0, 0.65 * sB, h), (0.02, 0.22, 0.3), ma, rot=(D(-10), 0, 0)); k.plate((0, 0.05, h + 0.38 * sB), (0.02, 0.28, 0.16), ma, rot=(D(-20), 0, 0))
            k.mirror([k.plate((0.28 * sB, -0.1, h - 0.1), (0.16, 0.1, 0.02), ma, rot=(D(10), D(-30), 0))])
            hr = 0.27 * sH; A.update(head=(0, -0.42 * sB, h + 0.05), hr=hr, back=(0, 0, h + 0.3 * sB), tail=(0, 0.6, h), len=1.0 * sB, body=(0, 0, h), bodyr=(0.28 * sB, 0.55 * sB, 0.36 * sB), wing=(0.25, 0, h))
    elif arche == 'slime':
        h = 0.42 * sB; mj = k.M(tuple(mb['rgb']), 0.1, 0, 0.2, alpha=0.78)
        k.ball((0, 0, h), (0.5 * sB, 0.5 * sB, 0.42 * sB), mj, seg=24); k.ball((0, 0, h * 0.3), (0.58 * sB, 0.58 * sB, 0.18), mj, seg=20); k.ico((0, 0.05, h), 0.17 * sB, mg, sub=2)
        for a in (0.5, 2.3, 4.2): k.ball((0.48 * sB * math.cos(a), 0.48 * sB * math.sin(a), 0.1), (0.14, 0.14, 0.11), mj)
        A.update(head=(0, -0.05, h + 0.05), hr=0.45 * sB, back=(0, 0.05, h * 1.9), tail=(0, 0.45, 0.2), len=0.5, body=(0, 0, h), bodyr=(0.5, 0.5, 0.42), wing=(0.4, 0, h))
    elif arche == 'insect':
        h = 0.35 * sL + 0.15; k.ball((0, 0.45 * sB, h + 0.05), (0.3 * sB, 0.42 * sB, 0.27 * sB), mb); k.ball((0, 0, h), (0.2, 0.22, 0.2), ma); hr = 0.22 * sH
        k.ball((0, -0.3, h + 0.05), (hr, hr, hr), mb)
        lg = []
        for j in range(3):
            y = -0.08 + j * 0.12; lg += [k.cyl((0.28, y, h * 0.7), 0.018, 0.38, ma, rot=(0, D(60), D(-20 + j * 20)), seg=5), k.cyl((0.44, y, h * 0.35), 0.016, 0.32, ma, rot=(0, D(-20), 0), seg=5)]
        lg += [k.cyl((0.08, -0.45, h + 0.3), 0.012, 0.35, mdark_(k), rot=(D(30), D(20), 0), seg=4), k.ball((0.13, -0.55, h + 0.46), (0.03,) * 3, k.M((1, 0.9, 0.3), 0.3, 0, 2), seg=6)]
        k.mirror(lg); A.update(head=(0, -0.3, h + 0.05), hr=hr, back=(0, 0.4, h + 0.3), tail=(0, 0.85, h), len=0.9 * sB, body=(0, 0.45 * sB, h), bodyr=(0.3, 0.42, 0.27), wing=(0.1, 0.1, h + 0.15))
    elif arche == 'golem':
        k.box((0, 0, 0.95 * sB), (0.45 * sB, 0.32 * sB, 0.42 * sB), mb, bevel=0.2); k.box((0, -0.05, 0.6 * sB), (0.36 * sB, 0.26 * sB, 0.2), ma, bevel=0.25)
        hr = 0.26 * sH; k.box((0, -0.05, 1.55 * sB), (hr, hr * 0.9, hr * 0.85), mb, bevel=0.25)
        lg = [k.box((0.62 * sB, 0, 0.9 * sB), (0.16, 0.16, 0.42), mb, rot=(0, D(-8), 0), bevel=0.25), k.box((0.66 * sB, -0.02, 0.38 * sB), (0.2, 0.2, 0.16), ma, bevel=0.3),
              k.box((0.22 * sB, 0, 0.3), (0.15, 0.17, 0.3), mb, bevel=0.25), k.ico((0.45 * sB, 0.1, 1.3 * sB), 0.12, ma, sub=0)]
        k.mirror(lg); k.ico((0, -0.33 * sB, 1.0 * sB), 0.12, mg, sub=1)
        A.update(head=(0, -0.05, 1.55 * sB), hr=hr, back=(0, 0.25, 1.35 * sB), tail=(0, 0.35, 0.8), len=0.8 * sB, body=(0, 0, 0.95 * sB), bodyr=(0.45, 0.32, 0.42), wing=(0.4, 0.2, 1.2 * sB))
    elif arche == 'spirit':
        h = 0.9; hr = 0.32 * sH; k.ball((0, 0, h), (hr, hr, hr), mb, seg=20); k.ball((0, 0, h), (hr * 1.3,) * 3, k.M(tuple(mg['rgb']), 0.2, 0, 1.2, alpha=0.3), seg=16)
        for j in range(4): k.cone((0.08 * math.sin(j * 2), 0.18 + j * 0.13, h - 0.3 - j * 0.12), 0.18 - j * 0.035, 0.35, mb, rot=(D(-50 - j * 8), 0, 0), seg=10)
        for j in range(3): a = j * 2.1; k.ico((0.55 * math.cos(a), 0.55 * math.sin(a), h + 0.1 * j), 0.06, mg, sub=1)
        A.update(head=(0, -0.02, h), hr=hr, back=(0, 0.1, h + hr), tail=(0, 0.4, h - 0.4), len=0.5, body=(0, 0, h), bodyr=(hr, hr, hr), wing=(0.25, 0.05, h))
    elif arche == 'crab':
        h = 0.3 * sL + 0.15; k.ball((0, 0, h), (0.45 * sB, 0.35 * sB, 0.18 * sB), mb, seg=18); k.ball((0, 0, h + 0.08), (0.38 * sB, 0.28 * sB, 0.12), ma, seg=14); hr = 0.18 * sH
        lg = []
        for j in range(3): y = -0.12 + j * 0.15; lg += [k.cyl((0.5 * sB, y, h * 0.6), 0.025, 0.4, ma, rot=(0, D(55), D(-15 + j * 15)), seg=5), k.cyl((0.68 * sB, y, h * 0.25), 0.02, 0.3, ma, rot=(0, D(-25), 0), seg=5)]
        lg += [k.ball((0.35 * sB, -0.45 * sB, h + 0.05), (0.07, 0.18, 0.07), mb, rot=(0, 0, D(20))), k.ball((0.42 * sB, -0.68 * sB, h + 0.08), (0.14, 0.16, 0.1), mb), k.cone((0.36 * sB, -0.8 * sB, h + 0.12), 0.04, 0.16, mhorn, rot=(D(90), 0, D(15)), seg=5)]
        k.mirror(lg); A.update(head=(0, -0.3 * sB, h + 0.12), hr=hr, back=(0, 0, h + 0.18), tail=(0, 0.35 * sB, h), tdir=(0, 0.6, 0.6), len=0.7 * sB, body=(0, 0, h), bodyr=(0.45, 0.35, 0.18), wing=(0.3, 0.1, h + 0.15))
    elif arche == 'octo':
        h = 0.75; hr = 0.42 * sH; k.ball((0, 0, h), (hr, hr * 0.95, hr * 1.15), mb, seg=20); k.ball((0, 0, h - hr * 0.6), (hr * 0.85, hr * 0.85, hr * 0.3), mbelly)
        for j in range(8):
            a = j / 8 * math.tau; pts = [(math.cos(a) * (0.25 + i * 0.09), math.sin(a) * (0.25 + i * 0.09), h - 0.4 - i * 0.07 + 0.05 * math.sin(i + j)) for i in range(5)]
            k.chain(pts, [0.09 - i * 0.014 for i in range(5)], mb if j % 2 else ma, seg=8)
        A.update(head=(0, -0.05, h + 0.05), hr=hr, back=(0, 0.05, h + hr), tail=(0, 0.3, 0.3), len=0.6, body=(0, 0, h), bodyr=(hr, hr, hr), wing=(0.3, 0, h))
    return A
def mdark_(k): return k.M((0.05, 0.05, 0.05), 0.4)

def rarity_extras(k, ri, hp, hr, A, mg, mgold, mcry, boss):
    top = A['head'][2] + hr * 1.5
    if ri >= 3:  # 에픽: 발광 보석
        k.ico((0, A['head'][1] - hr * 0.6, A['head'][2] + hr * 0.75), hr * 0.12, mg, sub=1)
    if ri >= 4:  # 레전더리: 금 장갑 / 목걸이
        k.torus((0, A['head'][1] + hr * 0.6, A['head'][2] - hr * 0.6), hr * 0.75, hr * 0.08, mgold, rot=(D(70), 0, 0), seg=18, rseg=5)
    if ri >= 5:  # 신화: 오라 파편
        for j in range(5): a = j / 5 * math.tau; k.crystal((0.6 * math.cos(a), A['body'][1] + 0.6 * math.sin(a), A['body'][2] + 0.4 + 0.1 * math.sin(j * 2)), 0.05, 0.22, mcry, rot=(D(20), D(j * 30), 0))
    if ri >= 6: k.torus((0, A['head'][1], top + 0.1), hr * 0.8, 0.025, mg, seg=24, rseg=5)  # 코스믹: 후광
    if ri >= 7:  # 시크릿: 기울어진 이중 고리
        k.torus((0, A['body'][1], A['body'][2] + 0.1), 0.68, 0.02, mcry, rot=(D(70), D(20), 0), seg=32, rseg=4)
    if ri >= 8:  # 이터널: 다층 오라 고리 + 왕관
        k.torus((0, A['body'][1], A['body'][2] + 0.1), 0.8, 0.018, mg, rot=(D(-60), D(-25), 0), seg=32, rseg=4)
        for j in range(6): a = j / 6 * math.tau; k.cone((hr * 0.5 * math.cos(a), A['head'][1] + hr * 0.5 * math.sin(a), top - 0.05), 0.04, 0.16, mgold, seg=4)
    if ri >= 9:  # 디바인: 태양 원반 후광
        k.torus((0, A['head'][1] + 0.25, top + 0.05), hr * 1.3, 0.04, mgold, rot=(D(80), 0, 0), seg=32, rseg=6)
        for j in range(12): a = j / 12 * math.tau; k.cone((hr * 1.55 * math.cos(a), A['head'][1] + 0.27, top + 0.05 + hr * 1.55 * math.sin(a)), 0.03, 0.18, mgold, rot=(D(90) + 0, a, 0), seg=4)

def special(k, s, A, mg, mgold, mcry, ma, mb):
    b = A['body']
    if s == 'chronos':
        k.torus((0, b[1] - 0.3, b[2] + 0.1), 0.22, 0.04, mgold, rot=(D(90), 0, 0), seg=20); k.ico((0, b[1] - 0.36, b[2] + 0.1), 0.13, mg, sub=2)
        for j in range(12): a = j / 12 * math.tau; k.box((0.22 * math.cos(a), b[1] - 0.36, b[2] + 0.1 + 0.22 * math.sin(a)), (0.02, 0.02, 0.04), mgold, rot=(0, -a, 0), bevel=0)
        for r, t in ((0.9, 30), (1.15, -20), (1.4, 60)): k.torus((0, b[1] + 0.4, b[2] + 0.6), r * 0.5, 0.025, mgold, rot=(D(t), D(90), 0), seg=32, rseg=4)
        for j in range(5): k.box((0, b[1] + j * 0.2 - 0.3, b[2] + 0.38), (0.24 - j * 0.02, 0.08, 0.03), mgold, bevel=0.4)
    elif s == 'voidcrystal':
        for j in range(16): a = j * 2.4; k.crystal((0.3 * math.cos(a), b[1] + 0.5 * math.sin(a), b[2] + 0.3 + (j % 3) * 0.08), 0.05 + (j % 4) * 0.02, 0.3 + (j % 5) * 0.08, mcry, rot=(D(30 * math.cos(a)), D(30 * math.sin(a)), 0))
        for j in range(8): a = j / 8 * math.tau; k.crystal((1.0 * math.cos(a), b[1] + 1.0 * math.sin(a), b[2] + 0.6 + 0.2 * math.sin(j)), 0.06, 0.25, mg, rot=(D(j * 40), 0, 0))
    elif s == 'seraph':
        for j in range(3):
            w = [k.plate((0.6 + j * 0.15, b[1] + 0.1 + j * 0.12, b[2] + 0.5 - j * 0.3 + 0.35), (0.55, 0.03, 0.18 - j * 0.02), k.M((1, 0.97, 0.9), 0.3, 0, 0.6), rot=(0, D(-35 + j * 30), D(10)))]
            k.mirror(w)
        for r in (0.35, 0.5): k.torus((0, A['head'][1] + 0.2, A['head'][2] + 0.55), r, 0.03, mgold, rot=(D(80), 0, 0), seg=32, rseg=5)
        k.ico((0, b[1] - 0.35, b[2] + 0.05), 0.15, k.M((1, 0.85, 0.3), 0.2, 0, 6), sub=2)
    elif s == 'galaxy':
        for j in range(24): k.ico((k.R.uniform(-0.25, 0.25), -0.5 + j * 0.07, 0.3 + k.R.uniform(-0.1, 0.3)), 0.025, mg, sub=0)
        for j in range(4): k.mirror([k.plate((0.35, -0.3 + j * 0.35, 0.3), (0.35, 0.12, 0.02), k.M((0.5, 0.6, 1.0), 0.2, 0, 1.5, alpha=0.5), rot=(D(10), D(-20), D(-10)))])
    elif s == 'kirin':
        for j in range(6): a = j / 6 * math.tau; k.ball((0.2 * math.cos(a), A['head'][1] + 0.2 * math.sin(a), A['head'][2] + 0.65), (0.07, 0.07, 0.03), k.M((1, 0.6, 0.8), 0.5, 0, 0.5), seg=8)
        for j in range(10): k.ball((k.R.uniform(-0.8, 0.8), k.R.uniform(-0.8, 1.2), k.R.uniform(0.3, 1.5)), (0.05, 0.03, 0.01), k.M((1, 0.7, 0.85), 0.5, 0, 0.6), seg=6)
        for j in range(5): k.ball((0, 0.7 + j * 0.12, b[2] + 0.1 - j * 0.04), (0.2 - j * 0.02, 0.18, 0.15 - j * 0.02), k.M((0.75, 0.6, 1.0), 0.4), seg=10)
