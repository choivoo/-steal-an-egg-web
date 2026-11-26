import { EGG_TYPES, eggSpawn, GUARDIAN_HOME, MAX_SPEED, SAFE_R, STEAL_RANGE } from '../../src/data/worldConsts';
export type GState = 'SLEEP' | 'CHASE' | 'ATTACK' | 'RETURN';
export interface WEgg { i: number; eggId: string; state: 'NEST' | 'CARRIED' | 'COOLDOWN'; carrier: string | null; respawnAt: number }
export type Ev = { to: string; msg: any };
export class World {
  eggs: WEgg[] = EGG_TYPES.map((eggId, i) => ({ i, eggId, state: 'NEST', carrier: null, respawnAt: 0 }));
  g = { x: GUARDIAN_HOME.x, z: GUARDIAN_HOME.z, s: 'SLEEP' as GState, carrier: null as string | null, t: 0 };
  pos = new Map<string, { x: number; z: number; t: number }>();
  constructor(private chaseSpeed = 12, private respawnMs = 30_000) {}
  /** 클라이언트 위치 보고. 속도 한계를 넘는 이동은 잘라냄(순간이동 방지). */
  report(pid: string, x: number, z: number, now: number) {
    const p = this.pos.get(pid); if (!p) { this.pos.set(pid, { x, z, t: now }); return; }
    const dt = Math.max(0.05, (now - p.t) / 1000), max = MAX_SPEED * dt + 0.5; const dx = x - p.x, dz = z - p.z, d = Math.hypot(dx, dz);
    if (d > max) { p.x += dx / d * max; p.z += dz / d * max; } else { p.x = x; p.z = z; } p.t = now;
  }
  remove(pid: string, now: number): Ev[] { this.pos.delete(pid); const e = this.eggs.find(e => e.carrier === pid); return e ? this.release(e, false, now) : []; }
  private release(e: WEgg, success: boolean, now: number): Ev[] {
    const to = e.carrier!; e.carrier = null; e.state = success ? 'COOLDOWN' : 'NEST'; e.respawnAt = now + this.respawnMs;
    if (this.g.carrier === to) { this.g.carrier = null; this.g.s = 'RETURN'; }
    return [{ to, msg: success ? { t: 'returned', i: e.i, eggId: e.eggId } : { t: 'caught', i: e.i } }];
  }
  steal(pid: string, i: number, now: number): Ev[] {
    const e = this.eggs[i], p = this.pos.get(pid); if (!e || !p) return [{ to: pid, msg: { t: 'steal_fail', reason: 'INVALID' } }];
    if (this.eggs.some(x => x.carrier === pid)) return [{ to: pid, msg: { t: 'steal_fail', reason: 'ALREADY_CARRYING' } }];
    if (e.state !== 'NEST') return [{ to: pid, msg: { t: 'steal_fail', reason: 'TAKEN' } }];
    const sp = eggSpawn(i); if (Math.hypot(p.x - sp.x, p.z - sp.z) > STEAL_RANGE + 1) return [{ to: pid, msg: { t: 'steal_fail', reason: 'TOO_FAR' } }];
    e.state = 'CARRIED'; e.carrier = pid; if (this.g.s === 'SLEEP' || this.g.s === 'RETURN' || !this.g.carrier) { this.g.carrier = pid; this.g.s = 'CHASE'; this.g.t = 0; }
    return [{ to: pid, msg: { t: 'steal_ok', i, eggId: e.eggId } }];
  }
  tick(dt: number, now: number): Ev[] {
    const ev: Ev[] = [];
    for (const e of this.eggs) { if (e.state === 'COOLDOWN' && now >= e.respawnAt) e.state = 'NEST'; if (e.state === 'CARRIED') { const p = this.pos.get(e.carrier!); if (p && Math.hypot(p.x, p.z) < SAFE_R) ev.push(...this.release(e, true, now)); } }
    const g = this.g;
    if (g.s === 'CHASE' || g.s === 'ATTACK') {
      const c = g.carrier && this.pos.get(g.carrier); const holding = this.eggs.find(e => e.carrier === g.carrier);
      if (!c || !holding) { g.s = 'RETURN'; g.carrier = null; }
      else if (g.s === 'CHASE') { const dx = c.x - g.x, dz = c.z - g.z, d = Math.hypot(dx, dz) || 1; g.x += dx / d * this.chaseSpeed * dt; g.z += dz / d * this.chaseSpeed * dt; const r = Math.hypot(g.x, g.z); if (r < SAFE_R + 2) { g.x *= (SAFE_R + 2) / r; g.z *= (SAFE_R + 2) / r; } if (d < 3) { g.s = 'ATTACK'; g.t = 0; } }
      else { g.t += dt; if (g.t > 0.5) { if (Math.hypot(c.x - g.x, c.z - g.z) < 4.5) { ev.push(...this.release(holding, false, now)); const gp = this.pos.get(holding.carrier ?? ''); void gp; } else { g.s = 'CHASE'; g.t = 0; } } }
    } else if (g.s === 'RETURN') { const dx = GUARDIAN_HOME.x - g.x, dz = GUARDIAN_HOME.z - g.z, d = Math.hypot(dx, dz); if (d < 0.5) g.s = 'SLEEP'; else { g.x += dx / d * 8 * dt; g.z += dz / d * 8 * dt; } }
    return ev;
  }
  snap() { return { t: 'snap', eggs: this.eggs.map(e => e.state === 'NEST' ? 0 : e.state === 'CARRIED' ? 1 : 2), carriers: this.eggs.map(e => e.carrier), g: { x: +this.g.x.toFixed(2), z: +this.g.z.toFixed(2), s: this.g.s, c: this.g.carrier } }; }
}
