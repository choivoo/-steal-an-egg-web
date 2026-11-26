import { describe, it, expect } from 'vitest';
import { GlobalEvents, scheduled } from '../server/src/events';
import { runCommand, parseRoles, AdminCtx, Role } from '../server/src/admin';
const kst = (h: number, m = 0) => Date.UTC(2026, 10, 26, h - 9, m);
describe('global events', () => {
  it('CLASSIC_CUSTOM 15~17 KST treadmill 8x, restored purely from time', () => {
    expect(scheduled(kst(15, 30), 'CLASSIC_CUSTOM').find(e => e.kind === 'treadmill')?.mult).toBe(8);
    expect(scheduled(kst(17, 5), 'CLASSIC_CUSTOM').find(e => e.kind === 'treadmill')).toBeUndefined();
    expect(scheduled(kst(15, 30), 'ORIGINAL').length).toBe(0);
    expect(scheduled(kst(10, 31), 'CLASSIC_CUSTOM').some(e => e.kind === 'cosmic_eclipse')).toBe(true);
    expect(scheduled(kst(10, 40), 'CLASSIC_CUSTOM').some(e => e.kind === 'cosmic_eclipse')).toBe(false);
  });
  it('multipliers do not stack multiplicatively; expire', () => {
    const g = new GlobalEvents(); g.start('treadmill', 4, 10, 0); g.start('treadmill', 8, 10, 0); expect(g.mult('treadmill', 1000)).toBe(8); expect(g.mult('treadmill', 11 * 60_000)).toBe(1);
  });
  it('persist/load', () => { const g = new GlobalEvents(); const e = g.start('income', 2, 60, 0); const h = new GlobalEvents(); h.load(JSON.parse(JSON.stringify(g.dump()))); expect(h.active(1000)[0].id).toBe(e.id); });
});
const ctx = (role: Role, log: object[] = [], ann: string[] = []): AdminCtx => ({ role, actor: 'x', now: 0, events: new GlobalEvents(), announce: m => ann.push(m), status: () => ({ online: 1 }), kick: () => true, drain: () => true, audit: e => log.push(e) });
describe('admin', () => {
  it('player cannot run commands; audited', () => { const log: object[] = []; expect(runCommand('/event start treadmill 8 120', ctx('PLAYER', log)).ok).toBe(false); expect(log.length).toBe(1); });
  it('event manager starts/stops event, announcement goes out', () => {
    const ann: string[] = []; const c = ctx('EVENT_MANAGER', [], ann); const r = runCommand('/event start treadmill 8x 120m global', c); expect(r.ok).toBe(true);
    expect(c.events.mult('treadmill', 1000)).toBe(8); expect(ann[0]).toContain('ADMIN EVENT'); expect(runCommand('/event stop ' + (r.data as any).id, c).ok).toBe(true);
    expect(runCommand('/server drain ABCDEF', c).ok).toBe(false); // ADMIN 필요
  });
  it('rejects bad input & unknown commands (no shell)', () => { const c = ctx('OWNER'); expect(runCommand('/event start treadmill 1000x 5m', c).ok).toBe(false); expect(runCommand('rm -rf /', c).ok).toBe(false); expect(runCommand('/announce global', c).ok).toBe(false); });
  it('roles only from valid env entries', () => { const k = 'a'.repeat(64); const m = parseRoles(`${k}:OWNER, bad:ADMIN, ${'b'.repeat(64)}:GOD`); expect(m.get(k)).toBe('OWNER'); expect(m.size).toBe(1); });
});
