import { describe, it, expect } from 'vitest';
import { World } from '../server/src/world';
import { eggSpawn } from '../src/data/worldConsts';
const run = (w: World, sec: number, now0: number) => { const evs: any[] = []; for (let t = 0; t < sec * 20; t++) evs.push(...w.tick(0.05, now0 + t * 50)); return evs; };
describe('server world', () => {
  it('two players race for same egg: only one wins', () => {
    const w = new World(); const s = eggSpawn(0); w.report('a', s.x, s.z + 2, 0); w.report('b', s.x, s.z + 2, 0);
    expect(w.steal('a', 0, 0)[0].msg.t).toBe('steal_ok'); expect(w.steal('b', 0, 0)[0].msg).toEqual({ t: 'steal_fail', reason: 'TAKEN' });
  });
  it('too far / carrying twice rejected', () => {
    const w = new World(); w.report('a', 0, 0, 0); expect(w.steal('a', 0, 0)[0].msg.reason).toBe('TOO_FAR');
    const s = eggSpawn(0); const w2 = new World(); w2.report('a', s.x, s.z, 0); w2.steal('a', 0, 0); expect(w2.steal('a', 1, 0)[0].msg.reason).toBe('ALREADY_CARRYING');
  });
  it('teleport clamped', () => { const w = new World(); w.report('a', 0, 0, 0); w.report('a', 100, 0, 100); expect(w.pos.get('a')!.x).toBeLessThan(3); });
  it('guardian catches stationary carrier; egg back in nest; no duplicate', () => {
    const w = new World(); const s = eggSpawn(0); w.report('a', s.x, s.z + 2, 0); w.steal('a', 0, 0); const ev = run(w, 10, 0);
    expect(ev.filter(e => e.msg.t === 'caught').length).toBe(1); expect(w.eggs[0].state).toBe('NEST'); expect(w.eggs[0].carrier).toBeNull(); expect(w.g.s === 'RETURN' || w.g.s === 'SLEEP').toBe(true);
  });
  it('reaching safe zone returns egg once, then cooldown & respawn', () => {
    const w = new World(5, 1000); const s = eggSpawn(1); w.report('a', s.x, s.z, 0); w.steal('a', 1, 0); w.report('a', s.x, s.z + 2.5, 5000); // small steps
    for (let k = 1; k <= 40; k++) w.report('a', 0, -70 + k * 1.7, 100 + k * 100); w.pos.get('a')!.x = 0; w.pos.get('a')!.z = 5;
    const ev = run(w, 1, 20000); expect(ev.filter(e => e.msg.t === 'returned').length).toBe(1); expect(w.eggs[1].state).toBe('COOLDOWN');
    run(w, 1, 22000); expect(w.eggs[1].state).toBe('NEST');
  });
  it('carrier disconnect releases egg', () => { const w = new World(); const s = eggSpawn(2); w.report('a', s.x, s.z, 0); w.steal('a', 2, 0); w.remove('a', 10); expect(w.eggs[2].state).toBe('NEST'); });
});
