import { describe, it, expect } from 'vitest';
import { fmt, worldSpeed, newSave, addEgg, hatchReady, tickIncome, buyTreadmill, pickPet, carrySpeed } from '../src/engine/logic';
describe('logic', () => {
  it('fmt big numbers', () => { expect(fmt(1500)).toBe('1.50K'); expect(fmt(2.5e12)).toBe('2.50T'); expect(fmt(-5)).toBe('0'); });
  it('worldSpeed bounded & monotonic', () => { expect(worldSpeed(1e30)).toBeLessThan(16.01); expect(worldSpeed(100)).toBeGreaterThan(worldSpeed(1)); });
  it('hatch once, slots limited', () => {
    const s = newSave(0); expect(addEgg(s, 'forest_egg', 0)).toBeTruthy(); addEgg(s, 'forest_egg', 0); expect(addEgg(s, 'forest_egg', 0)).toBeNull();
    expect(hatchReady(s, 5000).length).toBe(0); expect(hatchReady(s, 11000).length).toBe(2); expect(hatchReady(s, 99999).length).toBe(0); expect(s.pets.length).toBe(2);
  });
  it('offline hatch & income by timestamp', () => {
    const s = newSave(0); addEgg(s, 'forest_egg', 0); hatchReady(s, 3600_000, () => 0); expect(s.pets[0].petId).toBe('moss_fox');
    s.last = 0; const g = tickIncome(s, 100_000); expect(g).toBe(100); expect(s.money).toBe(100);
  });
  it('no negative money on purchase', () => { const s = newSave(0); expect(buyTreadmill(s)).toBe(false); s.money = 500; expect(buyTreadmill(s)).toBe(true); expect(s.money).toBe(0); });
  it('pickPet distribution matches weights', () => { let d = 0; for (let i = 0; i < 20000; i++) if (pickPet('forest_egg') === 'ember_drake') d++; expect(d / 20000).toBeGreaterThan(0.01); expect(d / 20000).toBeLessThan(0.035); });
  it('carry penalty', () => { expect(carrySpeed(10, 6)).toBeLessThan(10); expect(carrySpeed(10, 100)).toBe(4.5); });
});
