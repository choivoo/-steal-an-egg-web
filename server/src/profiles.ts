import { createHash } from 'node:crypto';
import { mkdirSync, readFileSync, writeFileSync, renameSync, existsSync } from 'node:fs';
import { dirname } from 'node:path';
import { Save, newSave, addEgg, hatchReady, tickIncome, buyTreadmill } from '../../src/engine/logic';
import { TREADMILLS } from '../../src/data/defs';
export interface Store { load(k: string): Promise<Save | undefined>; set(k: string, v: Save): void; flush(): Promise<void> }
export class MemoryStore implements Store { m = new Map<string, Save>(); async load(k: string) { const v = this.m.get(k); return v && structuredClone(v); } set(k: string, v: Save) { this.m.set(k, structuredClone(v)); } async flush() {} }
/** 로컬 JSON 파일 저장소(임시). 운영에서는 Postgres 어댑터로 교체 예정 — Store 인터페이스 동일. */
export class JsonFileStore implements Store {
  private d: Record<string, Save> = {}; private dirty = false;
  constructor(private path: string) { if (existsSync(path)) { try { this.d = JSON.parse(readFileSync(path, 'utf8')); } catch { /* 손상 시 덮어쓰지 않도록 백업 */ try { renameSync(path, path + '.corrupt-' + Date.now()); } catch {} } } }
  async load(k: string) { return this.d[k] && structuredClone(this.d[k]); } set(k: string, v: Save) { this.d[k] = structuredClone(v); this.dirty = true; }
  async flush() { if (!this.dirty) return; mkdirSync(dirname(this.path), { recursive: true }); writeFileSync(this.path + '.tmp', JSON.stringify(this.d)); renameSync(this.path + '.tmp', this.path); this.dirty = false; }
}
export const keyOf = (token: string) => createHash('sha256').update(token).digest('hex');
export const validToken = (t: unknown): t is string => typeof t === 'string' && /^[0-9a-f]{32,64}$/.test(t);
export const TREADMILL_POS = { x: 8, z: 6 }, TREADMILL_RANGE = 4.5;
interface Session { key: string; save: Save; training: boolean; lastTick: number; dirty: boolean }
export class Profiles {
  s = new Map<string, Session>(); constructor(private store: Store) {}
  /** 로그인. 오프라인 수익/부화는 서버 시계 기준으로 정산. 같은 계정의 기존 세션 pid를 반환(중복 접속 처리용) */
  async login(pid: string, token: string, now: number): Promise<{ save: Save; offline: number; kick?: string }> {
    const key = keyOf(token); let kick: string | undefined; for (const [p, x] of this.s) if (x.key === key) { kick = p; this.persist(p); this.s.delete(p); } // 이전 세션을 먼저 저장
    const loaded = await this.store.load(key);
    const save = loaded ?? newSave(now); const offline = tickIncome(save, now); hatchReady(save, now);
    this.s.set(pid, { key, save, training: false, lastTick: now, dirty: true }); return { save, offline, kick };
  }
  get(pid: string) { return this.s.get(pid)?.save; }
  setTraining(pid: string, on: boolean, pos?: { x: number; z: number }) { const x = this.s.get(pid); if (!x) return false; if (on && (!pos || Math.hypot(pos.x - TREADMILL_POS.x, pos.z - TREADMILL_POS.z) > TREADMILL_RANGE)) return false; x.training = on; return true; }
  /** 서버 틱: 수익, 부화, 훈련(위치 검증). 변경이 있으면 true */
  tick(pid: string, now: number, pos?: { x: number; z: number }, mult: { train?: number; income?: number } = {}): boolean {
    const x = this.s.get(pid); if (!x) return false; const dt = Math.min(1, Math.max(0, (now - x.lastTick) / 1000)); x.lastTick = now; let ch = false;
    if (x.training) { if (pos && Math.hypot(pos.x - TREADMILL_POS.x, pos.z - TREADMILL_POS.z) <= TREADMILL_RANGE) { x.save.train += TREADMILLS[x.save.treadmill].gain * (mult.train ?? 1) * dt; ch = true; } else x.training = false; }
    const before = x.save.money; tickIncome(x.save, now); x.save.money += (x.save.money - before) * ((mult.income ?? 1) - 1); if (x.save.money !== before) ch = true; if (hatchReady(x.save, now).length) { ch = true; } if (ch) x.dirty = true; return ch;
  }
  buy(pid: string) { const x = this.s.get(pid); if (!x) return false; const ok = buyTreadmill(x.save); if (ok) { x.dirty = true; this.persist(pid); } return ok; }
  hasSlot(pid: string) { const x = this.s.get(pid); return !!x && x.save.eggs.length < x.save.slots; }
  giveEgg(pid: string, eggId: string, now: number, hatchMult = 1) { const x = this.s.get(pid); if (!x) return false; const e = addEgg(x.save, eggId, now); if (e && hatchMult > 1) e.hatchAt = now + (e.hatchAt - now) / hatchMult; if (e) { x.dirty = true; this.persist(pid); } return !!e; }
  persist(pid: string) { const x = this.s.get(pid); if (x) { x.save.last = Date.now(); this.store.set(x.key, x.save); x.dirty = false; } }
  async logout(pid: string) { this.persist(pid); this.s.delete(pid); await this.store.flush(); }
  async periodic() { for (const [pid, x] of this.s) if (x.dirty) this.persist(pid); await this.store.flush(); }
}
