"""전체 에셋 카탈로그(설계 데이터) 생성. 고정 시드 → 재현 가능. Blender 없이 실행 가능.
각 크리처는 (체형 계열, 부위 조합) 시그니처가 서로 달라야 함 — 색상만 다른 중복 금지."""
import json, random, os, sys
R = random.Random(20261126)
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
RARITIES = ['common','uncommon','rare','epic','legendary','mythic','cosmic','secret','eternal','divine']
RAR_KO = ['커먼','언커먼','레어','에픽','레전더리','신화','코스믹','시크릿','이터널','디바인']
RAR_COLOR = ['#9aa0a6','#4caf50','#2196f3','#9c27b0','#ff9800','#e53935','#3f51b5','#eceff1','#64ffda','#ffd700']
BIOMES = [
 # id, ko, en, palette(main, accent, glow), ground, sky, required speed (독자 설정)
 ('forest','숲','Forest',[(0.30,0.55,0.25),(0.55,0.35,0.18),(0.75,1.0,0.4)],'#3f7d3a','#9fd3ff',0),
 ('lake','호수','Lake',[(0.25,0.55,0.85),(0.85,0.95,1.0),(0.4,0.9,1.0)],'#4f8f7a','#a8e0ff',900),
 ('desert','사막','Desert',[(0.85,0.70,0.40),(0.55,0.30,0.15),(1.0,0.75,0.3)],'#d9b56b','#ffd9a0',2.5e4),
 ('jungle','정글','Jungle',[(0.15,0.50,0.20),(0.80,0.55,0.10),(0.6,1.0,0.2)],'#2d5e2a','#b8e6a0',6e5),
 ('snow','설원','Snowland',[(0.85,0.92,1.0),(0.35,0.55,0.85),(0.6,0.9,1.0)],'#e8f0f7','#cfe6ff',1.5e7),
 ('volcano','화산','Volcano',[(0.20,0.10,0.08),(0.95,0.35,0.05),(1.0,0.45,0.05)],'#3a2420','#ff9a6b',4e8),
 ('deepsea','심해','Deep Sea',[(0.05,0.15,0.35),(0.20,0.85,0.75),(0.3,1.0,0.9)],'#14324a','#0b2a4a',1e10),
 ('prehistoric','선사시대','Prehistoric',[(0.55,0.45,0.30),(0.35,0.55,0.25),(1.0,0.8,0.4)],'#6e7a3e','#f2d8a7',3e11),
 ('cosmic','코스믹','Cosmic',[(0.12,0.08,0.30),(0.55,0.35,0.95),(0.8,0.6,1.0)],'#1c1438','#0d0826',8e12),
 ('blossom','벚꽃','Blossom',[(1.0,0.75,0.85),(0.55,0.35,0.30),(1.0,0.6,0.8)],'#f2c6d6','#ffe3ee',2e14),
 ('enchanted','마법숲','Enchanted Forest',[(0.20,0.25,0.45),(0.40,0.95,0.70),(0.5,1.0,0.8)],'#20304a','#2b3d6b',5e10),
 ('alien','에일리언','Alien',[(0.30,0.85,0.40),(0.60,0.20,0.80),(0.6,1.0,0.3)],'#3b2a52','#5a2f7a',2.5e11),
 ('storm','스톰랜드','Stormland',[(0.45,0.50,0.60),(0.95,0.90,0.30),(1.0,1.0,0.5)],'#4b5566','#596a80',1e15),
]
# 중요: 위 required speed는 독자 설정(원작 수치 아님). 마법숲 50B·에일리언 250B는 CLASSIC_CUSTOM과 유사 값 사용.
ARCHE = {  # 체형 계열 → 종 이름 후보
 'quadruped':['여우|Fox','늑대|Wolf','고양이|Cat','사슴|Stag','곰|Bear','멧돼지|Boar','토끼|Hare','코뿔소|Rhino','표범|Panther','양|Ram'],
 'dragon':['드레이크|Drake','와이번|Wyvern','드래곤|Dragon','용|Wyrm'],
 'bird':['참새|Finch','올빼미|Owl','독수리|Eagle','펭귄|Penguin','공작|Peacock','까마귀|Raven','불사조|Phoenix'],
 'serpent':['뱀|Serpent','장어|Eel','레비아탄|Leviathan','나가|Naga'],
 'fish':['물고기|Fish','복어|Puffer','가오리|Ray','상어|Shark','아귀|Angler'],
 'slime':['슬라임|Slime','젤리|Jelly','점액|Ooze'],
 'insect':['딱정벌레|Beetle','나비|Moth','개미|Ant','사마귀|Mantis','벌|Bee'],
 'golem':['골렘|Golem','거상|Colossus','토템|Totem'],
 'spirit':['정령|Spirit','위습|Wisp','혼령|Wraith'],
 'mech':['기계수|Mech','오토마톤|Automaton','드론|Drone'],
 'crab':['게|Crab','전갈|Scorpion','가재|Crayfish'],
 'octo':['문어|Octopus','해파리|Medusa','오징어|Squid'],
 'dino':['랩터|Raptor','트리케라|Trikera','렉스|Rex','스테고|Stego'],
}
BIOME_ARCHE = {
 'forest':['quadruped','bird','insect','slime','golem','spirit','dragon'], 'lake':['fish','bird','serpent','slime','octo','quadruped','crab'],
 'desert':['crab','serpent','quadruped','golem','insect','bird','dragon'], 'jungle':['insect','serpent','quadruped','bird','dino','slime','dragon'],
 'snow':['quadruped','bird','golem','spirit','fish','dragon','slime'], 'volcano':['dragon','golem','crab','insect','slime','spirit','dino'],
 'deepsea':['fish','octo','serpent','crab','slime','spirit','mech'], 'prehistoric':['dino','insect','bird','quadruped','serpent','golem','dragon'],
 'cosmic':['spirit','dragon','mech','serpent','octo','slime','bird'], 'blossom':['quadruped','bird','insect','spirit','dragon','slime','serpent'],
 'enchanted':['spirit','quadruped','insect','golem','slime','bird','dragon'], 'alien':['octo','insect','mech','slime','crab','serpent','spirit'],
 'storm':['bird','dragon','spirit','golem','mech','serpent','quadruped'],
}
ADJ = {'forest':'이끼|Moss','lake':'물결|Ripple','desert':'모래|Sand','jungle':'덩굴|Vine','snow':'서리|Frost','volcano':'용암|Magma','deepsea':'심연|Abyss','prehistoric':'화석|Fossil','cosmic':'성운|Nebula','blossom':'꽃잎|Petal','enchanted':'루멘|Lumen','alien':'제노|Xeno','storm':'뇌운|Thunder'}
ADJ2 = ['작은|Tiny','빛나는|Shining','고대|Ancient','수정|Crystal','그림자|Shade','황금|Golden','왕관|Crowned','별빛|Starlit','쌍뿔|Twinhorn','날쌘|Swift','거대|Grand','신성|Holy','폭풍|Tempest','영원|Eternal']
FEAT = {
 'horns':['none','spike','curved','antler','crystal','twin_spiral'], 'ears':['none','pointy','round','long','fin'],
 'tail':['none','fluffy','segmented','flame','club','fin','whip','crystal'], 'back':['none','spikes','plates','crystals','mushrooms','leaves','gears','fins'],
 'wings':['none','bat','feather','insect','crystal','energy'], 'eyes':[2,2,2,1,3,4], 'pattern':['plain','stripes','spots','bands','gradient'],
}
TOP = [  # PART 93 지정 최고 등급 독립 디자인
 dict(id='eternal_chronos_rex',ko='이터널 크로노스 렉스',en='Eternal Chronos Rex',biome='cosmic',rarity='eternal',arche='dragon',special='chronos',pal=[(0.08,0.10,0.30),(0.95,0.75,0.25),(1.0,0.85,0.4)]),
 dict(id='void_crystal_beast',ko='보이드 크리스탈 비스트',en='Void Crystal Beast',biome='cosmic',rarity='secret',arche='quadruped',special='voidcrystal',pal=[(0.15,0.05,0.25),(0.65,0.30,0.95),(0.8,0.4,1.0)]),
 dict(id='divine_solar_seraph',ko='디바인 솔라 세라프',en='Divine Solar Seraph',biome='storm',rarity='divine',arche='dragon',special='seraph',pal=[(0.97,0.95,0.90),(1.0,0.80,0.25),(1.0,0.9,0.5)]),
 dict(id='abyssal_galaxy_leviathan',ko='어비설 갤럭시 레비아탄',en='Abyssal Galaxy Leviathan',biome='deepsea',rarity='eternal',arche='serpent',special='galaxy',pal=[(0.05,0.08,0.25),(0.40,0.30,0.95),(0.5,0.8,1.0)]),
 dict(id='eternal_blossom_kirin',ko='이터널 블로섬 기린',en='Eternal Blossom Kirin',biome='blossom',rarity='eternal',arche='quadruped',special='kirin',pal=[(0.60,0.95,0.85),(1.0,0.65,0.85),(0.75,0.6,1.0)]),
]
def split(s): a, b = s.split('|'); return a, b
def jitter(c, r=0.08): return [max(0, min(1, x + R.uniform(-r, r))) for x in c]
def rarity_for(i, n):  # 지역 내 등급 분포: 아래가 많고 위가 적음
    t = i / max(1, n - 1); idx = min(9, int((t ** 1.6) * 8.2)); return RARITIES[idx]
def build():
    pets, sigs, names = [], set(), set()
    for t in TOP: t.update(features=dict(horns='crystal',ears='none',tail='segmented',back='crystals',wings='energy',eyes=2,pattern='gradient')); sigs.add(t['id']); pets.append(t)
    per = 12
    for bi, (bid, bko, ben, pal, *_ ) in enumerate(BIOMES):
        arches = BIOME_ARCHE[bid]
        for k in range(per):
            arche = arches[k % len(arches)]
            for _try in range(200):
                f = {key: R.choice(v) for key, v in FEAT.items()}
                if arche in ('fish','octo','serpent','slime','spirit'): f['ears'] = R.choice(['none','fin'])
                if arche in ('slime','octo'): f['wings'] = 'none'
                sig = (arche, f['horns'], f['tail'], f['back'], f['wings'], f['ears'])
                if sig not in sigs: sigs.add(sig); break
            sp_ko, sp_en = split(R.choice(ARCHE[arche])); a_ko, a_en = split(ADJ[bid])
            ko, en = f'{a_ko} {sp_ko}', f'{a_en} {sp_en}'
            while ko in names: a2k, a2e = split(R.choice(ADJ2)); ko, en = f'{a2k} {a_ko} {sp_ko}', f'{a2e} {a_en} {sp_en}'
            names.add(ko); rar = rarity_for(k, per)
            pid = f'{bid}_{sp_en.lower()}_{k:02d}'
            pets.append(dict(id=pid, ko=ko, en=en, biome=bid, rarity=rar, arche=arche, features=f, seed=R.randrange(1 << 30),
                             pal=[jitter(pal[0]), jitter(pal[1]), pal[2]], proportions=dict(body=R.uniform(0.8, 1.25), head=R.uniform(0.8, 1.3), leg=R.uniform(0.7, 1.3))))
    for p in pets:
        ri = RARITIES.index(p['rarity']); p['income'] = round(2 * (3.2 ** ri) * (1 + 0.6 * [b[0] for b in BIOMES].index(p['biome'])), 1); p['model'] = f"pets/{p['id']}.glb"
    eggs = []
    SHAPES = ['classic','tall','round','faceted','twisted']; DECOS = ['leaves','crystals','rings','spikes','rocks','cracks','bands','gems','wings','halo','tentacles','flowers','gears','stars','scales','runes']
    esigs = set()
    for bi, (bid, bko, ben, pal, *_ ) in enumerate(BIOMES):
        n = 11 if bi < 6 else 12
        for k in range(n):
            for _ in range(200):
                shape, d1, d2 = R.choice(SHAPES), R.choice(DECOS), R.choice(DECOS)
                if d1 != d2 and (bid, shape, d1, d2) not in esigs: esigs.add((bid, shape, d1, d2)); break
            rar = rarity_for(k, n); a_ko, a_en = split(ADJ[bid])
            ko = f'{a_ko} {RAR_KO[RARITIES.index(rar)]} 알 {k+1}'; en = f'{a_en} {rar.title()} Egg {k+1}'
            eid = f'egg_{bid}_{k:02d}'
            pool = [p for p in pets if p['biome'] == bid]; ri = RARITIES.index(rar)
            table = [{'id': p['id'], 'w': round(100 / (1 + abs(RARITIES.index(p['rarity']) - ri)) ** 2.2, 3)} for p in pool]
            eggs.append(dict(id=eid, ko=ko, en=en, biome=bid, rarity=rar, shape=shape, decos=[d1, d2], seed=R.randrange(1 << 30), pal=[jitter(pal[0]), jitter(pal[1]), pal[2]],
                             weight=round(1 + ri * 0.9 + R.uniform(0, 1), 1), hatchSec=int(20 * (1.6 ** ri)), pets=table, model=f'eggs/{eid}.glb'))
    guardians = []
    G_NAMES = {'forest':'아이언비크|Ironbeak|bird','lake':'아쿠아크레스트|Aquacrest|serpent','desert':'샌드스팅 타이탄|Sandsting Titan|crab','jungle':'베놈팽|Venomfang|serpent','snow':'프로스트혼|Frosthorn|quadruped','volcano':'마그마자우|Magmasaur|dino','deepsea':'어비스메인|Abyssmane|octo','prehistoric':'크래그렉스|Cragrex|dino','cosmic':'네뷸라 드레이크|Nebula Drake|dragon','blossom':'블로섬 키린|Blossom Kirin|quadruped','enchanted':'루미너스 위스프|Luminous Wisp|spirit','alien':'보이드 세라프|Void Seraph|insect','storm':'썬더 콜로서스|Thunder Colossus|golem'}
    for bid, (bko, ben, pal, *_ ) in [(b[0], b[1:]) for b in BIOMES]:
        ko, en, ar = G_NAMES[bid].split('|'); f = {key: R.choice(v) for key, v in FEAT.items()}; f.update(horns=R.choice(['curved','antler','crystal','twin_spiral']), back=R.choice(['spikes','plates','crystals']))
        guardians.append(dict(id=f'guardian_{bid}', ko=ko, en=en, biome=bid, arche=ar, kind='guardian', features=f, seed=R.randrange(1 << 30), pal=[jitter(pal[0]), (0.35,0.35,0.4), (1.0,0.2,0.1)], model=f'guardians/guardian_{bid}.glb', chaseSpeed=round(9 + BIOMES.index(next(b for b in BIOMES if b[0]==bid)) * 0.45, 2)))
    BOSS = ['차원 파수꾼|Rift Warden|spirit','황금 폭풍왕|Golden Tempest|bird','외계 침공체|Invader Prime|mech','크리스탈 하이드라|Crystal Hydra|serpent','유성 거신|Meteor Titan|golem','그림자 군주|Shade Lord|quadruped','태엽 거미|Clockwork Spider|insect','해일 크라켄|Tidal Kraken|octo','화염 군단장|Flame Marshal|dino','오로라 피닉스|Aurora Phoenix|bird','늪의 거목|Bog Treant|golem','혜성 뱀|Comet Serpent|serpent','심판의 용|Judgement Dragon|dragon']
    for i, s in enumerate(BOSS):
        ko, en, ar = s.split('|'); b = BIOMES[i]; f = {key: R.choice(v) for key, v in FEAT.items()}; f.update(horns='twin_spiral', back='crystals', wings=R.choice(['bat','crystal','energy']) if ar in ('dragon','bird','insect') else 'none')
        guardians.append(dict(id=f'boss_{i:02d}', ko=ko, en=en, biome=b[0], arche=ar, kind='boss', features=f, seed=R.randrange(1 << 30), pal=[jitter(b[3][0]), b[3][1], b[3][2]], model=f'bosses/boss_{i:02d}.glb', chaseSpeed=round(11 + i * 0.4, 2)))
    TM_KO = ['기본','강철','청동','은빛','황금','에메랄드','사파이어','루비','자수정','프로스트','마그마','심해','화석','성운','벚꽃','루멘','제노','썬더','코스믹','디바인']
    treadmills = [dict(id=f'treadmill_{i:02d}', ko=f'{TM_KO[i]} 러닝머신', tier=i, cost=0 if i == 0 else int(500 * (4.2 ** (i - 1))), gain=round(1 * (3.0 ** i), 1), model=f'treadmills/treadmill_{i:02d}.glb', seed=R.randrange(1 << 30)) for i in range(20)]
    ENV_KINDS = {'forest':['tree_pine','tree_oak','mushroom','bush','rock','log','fern','flower','stump'],'lake':['reed','lily','rock','crystal','tree_willow','driftwood','shell','bush','pebbles'],
     'desert':['cactus','rock_arch','ruin_pillar','dune_rock','skull','palm','obelisk','bush_dry','urn'],'jungle':['tree_jungle','vine_pillar','giant_leaf','flower','temple_block','mushroom','fern','totem','rock'],
     'snow':['tree_snowpine','ice_spike','ice_crystal','snow_rock','snowman','igloo_block','frozen_log','ice_arch','pebbles'],'volcano':['lava_rock','obsidian_spike','vent','charred_tree','ember_crystal','basalt','skull','rock_arch','magma_pool'],
     'deepsea':['coral_branch','coral_fan','kelp','anemone','shell','sunken_pillar','anchor','bubble_rock','glow_crystal'],'prehistoric':['giant_fern','fossil_bone','cycad','amber_rock','rock','volcano_cone','dino_egg_nest','log','flower'],
     'cosmic':['star_crystal','planet_orb','floating_rock','meteor','nebula_tree','ring_arch','obelisk','crystal','asteroid'],'blossom':['tree_sakura','torii','lantern','bush','flower','petal_pile','bridge_small','rock','bamboo'],
     'enchanted':['glow_tree','glow_mushroom','rune_stone','crystal','wisp_lamp','fairy_ring','root_arch','flower','bush'],'alien':['alien_pod','tentacle_plant','alien_crystal','spore_tree','goo_pool','antenna_rock','egg_sac','floating_rock','mushroom'],
     'storm':['cloud_pillar','lightning_rod','storm_crystal','sky_rock','windmill','storm_tree','rune_stone','ruin_pillar','floating_rock']}
    env = []
    for b in BIOMES:
        for k, kind in enumerate(ENV_KINDS[b[0]]): env.append(dict(id=f'env_{b[0]}_{kind}', biome=b[0], kind=kind, pal=[b[3][0], b[3][1], b[3][2]], seed=R.randrange(1 << 30), model=f"environment/env_{b[0]}_{kind}.glb"))
    for extra in ['sky_island','big_rock','hill_tile','fence_post','sign_post','bench','street_lamp']: env.append(dict(id=f'env_common_{extra}', biome='base', kind=extra, pal=[(0.6,0.6,0.6),(0.4,0.3,0.2),(1,0.9,0.6)], seed=R.randrange(1 << 30), model=f'environment/env_common_{extra}.glb'))
    BUILD = ['base_platform','hatch_pedestal','pet_pen','fence','gate','safe_arch','shop_stall','index_kiosk','money_counter','tower','bridge','banner','lamp_post','stairs','upgrade_station','fishing_dock','event_stage','spawn_pad','expansion_floor','storage_crate','fountain','mailbox']
    builds = [dict(id=f'build_{n}', kind=n, seed=R.randrange(1 << 30), model=f'buildings/build_{n}.glb') for n in BUILD]
    builds += [dict(id=f'build_portal_{b[0]}', kind='portal', biome=b[0], pal=[b[3][0], b[3][1], b[3][2]], seed=R.randrange(1 << 30), model=f'buildings/build_portal_{b[0]}.glb') for b in BIOMES]
    EQUIP = [('rod', i) for i in range(8)] + [('bobber', i) for i in range(4)] + [('net', i) for i in range(3)] + [('backpack', i) for i in range(5)] + [('hat', i) for i in range(5)]
    equip = [dict(id=f'equip_{k}_{i}', kind=k, tier=i, seed=R.randrange(1 << 30), model=f'equipment/equip_{k}_{i}.glb') for k, i in EQUIP]
    MISC = [('coin', 0), ('gem', 0), ('gem', 1), ('gem', 2)] + [('chest', i) for i in range(5)] + [('key', 0), ('crown', 0), ('trophy', 0), ('trophy', 1), ('lantern', 0), ('candy', 0), ('star_fragment', 0), ('potion', 0), ('potion', 1), ('scroll', 0), ('rune', 0)] + [('fish', i) for i in range(12)] + [('egg_crack_shell', 0), ('halo_prop', 0), ('rift_shard', 0)]
    misc = [dict(id=f'misc_{k}_{i}', kind=k, tier=i, seed=R.randrange(1 << 30), model=f'misc/misc_{k}_{i}.glb') for k, i in MISC]
    players = [dict(id=f'player_{i}', kind='player', variant=i, seed=R.randrange(1 << 30), model=f'players/player_{i}.glb') for i in range(5)]
    cat = dict(version=1, rarities=[dict(id=r, ko=k, color=c) for r, k, c in zip(RARITIES, RAR_KO, RAR_COLOR)],
               biomes=[dict(id=b[0], ko=b[1], en=b[2], ground=b[4], sky=b[5], requiredSpeed=b[6], index=i) for i, b in enumerate(BIOMES)],
               pets=pets, eggs=eggs, guardians=guardians, treadmills=treadmills, environment=env, buildings=builds, equipment=equip, misc=misc, players=players)
    return cat
if __name__ == '__main__':
    c = build(); out = os.path.join(ROOT, 'public/assets/manifests/catalog.json'); os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump(c, open(out, 'w'), ensure_ascii=False)
    counts = {k: len(v) for k, v in c.items() if isinstance(v, list) and k not in ('rarities', 'biomes')}
    print(counts, 'TOTAL', sum(counts.values()))
    sig = {(p['arche'], *(p['features'][k] for k in ('horns', 'tail', 'back', 'wings', 'ears'))) for p in c['pets']}; print('unique pet signatures', len(sig), '/', len(c['pets']))
