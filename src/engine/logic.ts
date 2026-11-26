import { EGGS, PETS, TREADMILLS } from '../data/defs';
const SUF = ['', 'K', 'M', 'B', 'T', 'Qa', 'Qi', 'Sx', 'Sp', 'Oc', 'No', 'Dc'];
export function fmt(n: number): string {
  if (!isFinite(n) || n < 0) return '0';
  if (n < 1000) return Math.floor(n).toString();
  let i = 0; while (n >= 1000 && i < SUF.length - 1) { n /= 1000; i++; }
  return n.toFixed(n < 10 ? 2 : n < 100 ? 1 : 0) + SUF[i];
}
/** 훈련량 -> 월드 이동속도 (로그형 포화: 무한 증가 방지) */
export function worldSpeed(train: number): number { return 6 + 10 * (1 - Math.exp(-Math.log10(1 + train) / 3)); }
export function carrySpeed(base: number, eggWeight: number): number { return base * Math.max(0.45, 1 - 0.06 * eggWeight); }
export function pickPet(eggId: string, rnd: () => number = Math.random): string {
  const egg = EGGS.find(e => e.id === eggId)!; const tot = egg.pets.reduce((s, p) => s + p.w, 0);
  let r = rnd() * tot; for (const p of egg.pets) { if ((r -= p.w) < 0) return p.id; } return egg.pets[egg.pets.length - 1].id;
}
export interface OwnedEgg { uid: string; eggId: string; hatchAt: number }
export interface Save { v: 1; money: number; train: number; treadmill: number; pets: { uid: string; petId: string }[]; eggs: OwnedEgg[]; slots: number; last: number; uid: number }
export const newSave = (now: number): Save => ({ v: 1, money: 0, train: 0, treadmill: 0, pets: [], eggs: [], slots: 2, last: now, uid: 1 });
export const incomePerSec = (s: Save) => s.pets.reduce((a, p) => a + PETS.find(x => x.id === p.petId)!.income, 0);
/** 경과시간 기반 수익(오프라인 포함). 상한 8시간 */
export function tickIncome(s: Save, now: number): number {
  const dt = Math.min(Math.max(0, (now - s.last) / 1000), 8 * 3600); s.last = now;
  const g = incomePerSec(s) * dt; s.money += g; return g;
}
export function buyTreadmill(s: Save): boolean {
  const n = TREADMILLS[s.treadmill + 1]; if (!n || s.money < n.cost) return false; s.money -= n.cost; s.treadmill++; return true;
}
export function addEgg(s: Save, eggId: string, now: number): OwnedEgg | null {
  if (s.eggs.length >= s.slots) return null;
  const e: OwnedEgg = { uid: 'e' + s.uid++, eggId, hatchAt: now + EGGS.find(x => x.id === eggId)!.hatchSec * 1000 };
  s.eggs.push(e); return e;
}
/** 부화: 시간 도달한 알만, 1회만 펫 생성 */
export function hatchReady(s: Save, now: number, rnd?: () => number) {
  const out: { uid: string; petId: string }[] = [];
  s.eggs = s.eggs.filter(e => { if (now < e.hatchAt) return true; const p = { uid: 'p' + s.uid++, petId: pickPet(e.eggId, rnd) }; s.pets.push(p); out.push(p); return false; });
  return out;
}
