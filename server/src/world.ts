import { NESTS, GUARDS, MAX_SPEED, SAFE_LINE, STEAL_RANGE, clampToWorld, LANE_HALF } from '../../src/data/worldConsts';
export type GState = 'SLEEP' | 'CHASE' | 'ATTACK' | 'RETURN';
export interface WEgg { i: number; eggId: string; biome: number; state: 'NEST' | 'CARRIED' | 'COOLDOWN'; carrier: string | null; respawnAt: number }
export interface WGuard { x: number; z: number; s: GState; carrier: string | null; t: number; speed: number; home: { x: number; z: number } }
export type Ev = { to: string; msg: any };
/** 방(Room)별 서버 권위 월드: 39개 둥지 + 지역별 수호자 13. */
export class World {
  eggs: WEgg[] = NESTS.map((n, i) => ({ i, eggId: n.eggId, biome: n.biome, state: 'NEST', carrier: null, respawnAt: 0 }));
  guards: WGuard[] = GUARDS.map(g => ({ x: g.home.x, z: g.home.z, s: 'SLEEP', carrier: null, t: 0, speed: g.speed, home: g.home }));
  pos = new Map<string, { x: number; z: number; t: number }>();
  constructor(private speedScale = 1, private respawnMs = 30_000) {}
  get g() { return this.guards[0]; } // (호환) 첫 지역 수호자
  report(pid: string, x: number, z: number, now: number) {
    [x, z] = clampToWorld(x, z); const p = this.pos.get(pid); if (!p) { this.pos.set(pid, { x, z, t: now }); return; }
    const dt = Math.max(0.05, (now - p.t) / 1000), max = MAX_SPEED * dt + 0.5; const dx = x - p.x, dz = z - p.z, d = Math.hypot(dx, dz);
    if (d > max) { p.x += dx / d * max; p.z += dz / d * max; } else { p.x = x; p.z = z; } p.t = now;
  }
  remove(pid: string, now: number): Ev[] { this.pos.delete(pid); const e = this.eggs.find(e => e.carrier === pid); return e ? this.release(e, false, now) : []; }
  private release(e: WEgg, success: boolean, now: number): Ev[] {
    const to = e.carrier!; e.carrier = null; e.state = success ? 'COOLDOWN' : 'NEST'; e.respawnAt = now + this.respawnMs;
    for (const g of this.guards) if (g.carrier === to) { g.carrier = null; g.s = 'RETURN'; }
    return [{ to, msg: success ? { t: 'returned', i: e.i, eggId: e.eggId } : { t: 'caught', i: e.i, biome: e.biome } }];
  }
  steal(pid: string, i: number, now: number): Ev[] {
    const e = this.eggs[i], p = this.pos.get(pid); if (!e || !p) return [{ to: pid, msg: { t: 'steal_fail', reason: 'INVALID' } }];
    if (this.eggs.some(x => x.carrier === pid)) return [{ to: pid, msg: { t: 'steal_fail', reason: 'ALREADY_CARRYING' } }];
    if (e.state !== 'NEST') return [{ to: pid, msg: { t: 'steal_fail', reason: 'TAKEN' } }];
    const n = NESTS[i]; if (Math.hypot(p.x - n.x, p.z - n.z) > STEAL_RANGE + 1) return [{ to: pid, msg: { t: 'steal_fail', reason: 'TOO_FAR' } }];
    e.state = 'CARRIED'; e.carrier = pid; const g = this.guards[e.biome];
    if (!g.carrier) { g.carrier = pid; g.s = 'CHASE'; g.t = 0; }
    return [{ to: pid, msg: { t: 'steal_ok', i, eggId: e.eggId } }];
  }
  tick(dt: number, now: number): Ev[] {
    const ev: Ev[] = [];
    for (const e of this.eggs) { if (e.state === 'COOLDOWN' && now >= e.respawnAt) e.state = 'NEST'; if (e.state === 'CARRIED') { const p = this.pos.get(e.carrier!); if (p && p.z > SAFE_LINE) ev.push(...this.release(e, true, now)); } }
    for (const g of this.guards) {
      if (g.s === 'CHASE' || g.s === 'ATTACK') {
        const c = g.carrier && this.pos.get(g.carrier); const holding = this.eggs.find(e => e.carrier === g.carrier);
        if (!c || !holding) { g.s = 'RETURN'; g.carrier = null; }
        else if (g.s === 'CHASE') {
          const dx = c.x - g.x, dz = c.z - g.z, d = Math.hypot(dx, dz) || 1; const sp = g.speed * this.speedScale;
          g.x += dx / d * sp * dt; g.z += dz / d * sp * dt; g.x = Math.max(-LANE_HALF + 1, Math.min(LANE_HALF - 1, g.x)); g.z = Math.min(g.z, SAFE_LINE - 2); // 안전구역 진입 불가
          if (d < 3) { g.s = 'ATTACK'; g.t = 0; }
        } else { g.t += dt; if (g.t > 0.5) { if (Math.hypot(c.x - g.x, c.z - g.z) < 4.5) ev.push(...this.release(holding, false, now)); else { g.s = 'CHASE'; g.t = 0; } } }
      } else if (g.s === 'RETURN') { const dx = g.home.x - g.x, dz = g.home.z - g.z, d = Math.hypot(dx, dz); if (d < 0.5) g.s = 'SLEEP'; else { const st = Math.min(d, 9 * dt); g.x += dx / d * st; g.z += dz / d * st; } }
    }
    return ev;
  }
  snap() { return { t: 'snap', eggs: this.eggs.map(e => e.state === 'NEST' ? 0 : e.state === 'CARRIED' ? 1 : 2), g: this.guards.map(g => [+g.x.toFixed(1), +g.z.toFixed(1), g.s === 'SLEEP' ? 0 : g.s === 'RETURN' ? 2 : 1]) }; }
}
