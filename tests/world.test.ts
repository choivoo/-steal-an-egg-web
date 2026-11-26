import { describe, it, expect } from 'vitest';
import { World } from '../server/src/world';
import { NESTS, GUARDS, SAFE_LINE, biomeAt, LANE_END } from '../src/data/worldConsts';
import { BIOMES } from '../src/data/defs';
const run = (w: World, sec: number, now0: number) => { const evs: any[] = []; for (let t = 0; t < sec * 20; t++) evs.push(...w.tick(0.05, now0 + t * 50)); return evs; };
describe('lane world', () => {
  it('13 biomes x 3 nests, one guardian per biome, nests inside own biome', () => {
    expect(NESTS.length).toBe(BIOMES.length * 3); expect(GUARDS.length).toBe(BIOMES.length);
    for (const n of NESTS) expect(biomeAt(n.z)).toBe(n.biome); for (const g of GUARDS) expect(biomeAt(g.home.z)).toBe(g.biome);
    expect(LANE_END).toBeLessThan(-900);
  });
  it('race: only one player gets the egg', () => {
    const w = new World(); const n = NESTS[4]; w.pos.set('a', { x: n.x, z: n.z, t: 0 }); w.pos.set('b', { x: n.x, z: n.z, t: 0 });
    expect(w.steal('a', 4, 0)[0].msg.t).toBe('steal_ok'); expect(w.steal('b', 4, 0)[0].msg.reason).toBe('TAKEN');
  });
  it('only that biome guardian wakes', () => { const w = new World(); const n = NESTS[7]; w.pos.set('a', { x: n.x, z: n.z, t: 0 }); w.steal('a', 7, 0); expect(w.guards.filter(g => g.s === 'CHASE').length).toBe(1); expect(w.guards[n.biome].s).toBe('CHASE'); });
  it('too far / carrying twice rejected', () => {
    const w = new World(); w.pos.set('a', { x: 0, z: 0, t: 0 }); expect(w.steal('a', 0, 0)[0].msg.reason).toBe('TOO_FAR');
    const n = NESTS[0]; w.pos.set('b', { x: n.x, z: n.z, t: 0 }); w.steal('b', 0, 0); w.pos.get('b')!.x = NESTS[1].x; w.pos.get('b')!.z = NESTS[1].z; expect(w.steal('b', 1, 0)[0].msg.reason).toBe('ALREADY_CARRYING');
  });
  it('teleport clamped & lane walls enforced', () => { const w = new World(); w.report('a', 0, 0, 0); w.report('a', 0, -400, 100); expect(w.pos.get('a')!.z).toBeGreaterThan(-3); w.report('b', 0, -100, 0); w.report('b', 50, -100, 5000); expect(w.pos.get('b')!.x).toBeLessThan(13); });
  it('stationary carrier gets caught; egg back; no duplicate', () => {
    const w = new World(); const n = NESTS[0]; w.pos.set('a', { x: n.x, z: n.z, t: 0 }); w.steal('a', 0, 0); const ev = run(w, 20, 0);
    expect(ev.filter(e => e.msg.t === 'caught').length).toBe(1); expect(w.eggs[0].state).toBe('NEST');
  });
  it('crossing safe line returns egg once; guardian never enters base', () => {
    const w = new World(5, 1000); const n = NESTS[0]; w.pos.set('a', { x: n.x, z: n.z, t: 0 }); w.steal('a', 0, 0);
    w.pos.get('a')!.z = SAFE_LINE + 1; const ev = run(w, 1, 1000); expect(ev.filter(e => e.msg.t === 'returned').length).toBe(1); expect(w.eggs[0].state).toBe('COOLDOWN');
    run(w, 1, 3000); expect(w.eggs[0].state).toBe('NEST'); for (const g of w.guards) expect(g.z).toBeLessThan(SAFE_LINE);
  });
  it('disconnect releases egg', () => { const w = new World(); const n = NESTS[2]; w.pos.set('a', { x: n.x, z: n.z, t: 0 }); w.steal('a', 2, 0); w.remove('a', 10); expect(w.eggs[2].state).toBe('NEST'); });
});
