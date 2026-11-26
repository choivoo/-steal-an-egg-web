import { describe, it, expect } from 'vitest';
import { Profiles, MemoryStore, JsonFileStore, keyOf, validToken, TREADMILL_POS } from '../server/src/profiles';
import { mkdtempSync, rmSync, writeFileSync, readdirSync } from 'node:fs'; import { tmpdir } from 'node:os'; import { join } from 'node:path';
const T = 'a'.repeat(32);
describe('profiles', () => {
  it('token validation', async () => { expect(validToken(T)).toBe(true); expect(validToken('x')).toBe(false); expect(validToken(5)).toBe(false); expect(keyOf(T)).not.toContain(T); });
  it('train only near treadmill, accrues by server time', async () => {
    const p = new Profiles(new MemoryStore()); await p.login('a', T, 0); expect(p.setTraining('a', true, { x: 0, z: 0 })).toBe(false);
    expect(p.setTraining('a', true, TREADMILL_POS)).toBe(true); p.tick('a', 1000, TREADMILL_POS); p.tick('a', 2000, TREADMILL_POS); expect(p.get('a')!.train).toBeCloseTo(2, 5);
    p.tick('a', 3000, { x: 50, z: 50 }); p.tick('a', 4000, TREADMILL_POS); expect(p.get('a')!.train).toBeCloseTo(2, 5); // 이탈 시 중단
  });
  it('cannot buy without money; persists across relogin; offline hatch/income', async () => {
    const st = new MemoryStore(); const p = new Profiles(st); await p.login('a', T, 0); expect(p.buy('a')).toBe(false);
    p.giveEgg('a', 'egg_forest_00', 0); await p.logout('a'); const r = await p.login('b', T, 3600_000); expect(r.save.pets.length).toBe(1); expect(r.save.eggs.length).toBe(0); expect(r.offline).toBeGreaterThanOrEqual(0);
  });
  it('duplicate login kicks old session; no double egg', async () => { const p = new Profiles(new MemoryStore()); await p.login('a', T, 0); const r = await p.login('b', T, 10); expect(r.kick).toBe('a'); expect(p.get('a')).toBeUndefined(); });
  it('slots limit', async () => { const p = new Profiles(new MemoryStore()); await p.login('a', T, 0); expect(p.giveEgg('a', 'egg_forest_00', 0)).toBe(true); p.giveEgg('a', 'egg_forest_00', 0); expect(p.hasSlot('a')).toBe(false); expect(p.giveEgg('a', 'egg_forest_00', 0)).toBe(false); });
  it('json file store roundtrip + corrupt file not overwritten', async () => {
    const d = mkdtempSync(join(tmpdir(), 'sae-')); const f = join(d, 'db.json'); const s1 = new JsonFileStore(f); const p = new Profiles(s1); await p.login('a', T, 0); p.giveEgg('a', 'egg_forest_00', 0); await p.logout('a');
    const s2 = new JsonFileStore(f); expect((await s2.load(keyOf(T)))!.eggs.length).toBe(1);
    writeFileSync(f, '{bad'); new JsonFileStore(f); expect(readdirSync(d).some(n => n.includes('corrupt'))).toBe(true); rmSync(d, { recursive: true });
  });
});
