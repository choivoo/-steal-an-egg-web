import { describe, it, expect } from 'vitest';
import { EGGS, PETS } from '../src/data/defs';
import { fmt, worldSpeed, newSave, addEgg, hatchReady, tickIncome, buyTreadmill, pickPet, carrySpeed } from '../src/engine/logic';
describe('logic', () => {
  it('fmt big numbers', () => { expect(fmt(1500)).toBe('1.50K'); expect(fmt(2.5e12)).toBe('2.50T'); expect(fmt(-5)).toBe('0'); });
  it('worldSpeed bounded & monotonic', () => { expect(worldSpeed(1e30)).toBeLessThan(16.01); expect(worldSpeed(100)).toBeGreaterThan(worldSpeed(1)); });
  it('hatch once, slots limited', () => {
    const s = newSave(0); expect(addEgg(s, 'egg_forest_00', 0)).toBeTruthy(); addEgg(s, 'egg_forest_00', 0); expect(addEgg(s, 'egg_forest_00', 0)).toBeNull();
    expect(hatchReady(s, 5000).length).toBe(0); expect(hatchReady(s, 21000).length).toBe(2); expect(hatchReady(s, 99999).length).toBe(0); expect(s.pets.length).toBe(2);
  });
  it('offline hatch & income by timestamp', () => {
    const s = newSave(0); addEgg(s, 'egg_forest_00', 0); hatchReady(s, 3600_000, () => 0); expect(s.pets[0].petId).toBe(EGGS.find(e => e.id === 'egg_forest_00')!.pets[0].id);
    s.last = 0; const inc = PETS.find(p => p.id === s.pets[0].petId)!.income; const g = tickIncome(s, 100_000); expect(g).toBeCloseTo(inc * 100); expect(s.money).toBeCloseTo(inc * 100);
  });
  it('no negative money on purchase', () => { const s = newSave(0); expect(buyTreadmill(s)).toBe(false); s.money = 500; expect(buyTreadmill(s)).toBe(true); expect(s.money).toBe(0); });
  it('pickPet distribution matches displayed weights', () => {
    const egg = EGGS.find(e => e.id === 'egg_forest_00')!; const tot = egg.pets.reduce((a, p) => a + p.w, 0); const cnt: Record<string, number> = {};
    for (let i = 0; i < 40000; i++) { const id = pickPet(egg.id); cnt[id] = (cnt[id] ?? 0) + 1; }
    for (const p of egg.pets) expect(Math.abs((cnt[p.id] ?? 0) / 40000 - p.w / tot)).toBeLessThan(0.012);
    expect(Object.keys(cnt).every(id => PETS.some(p => p.id === id))).toBe(true);
  });
  it('carry penalty', () => { expect(carrySpeed(10, 6)).toBeLessThan(10); expect(carrySpeed(10, 100)).toBe(4.5); });
});
