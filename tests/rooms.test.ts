import { describe, it, expect } from 'vitest';
import { RoomManager, MAX_PLAYERS_PER_ROOM } from '../server/src/rooms';
const dist = (m: RoomManager) => m.list().map(r => r.players).sort((a, b) => b - a);
describe('rooms', () => {
  it('max 7', () => expect(MAX_PLAYERS_PER_ROOM).toBe(7));
  it('1/7/8/15/22/100 distribution', () => {
    for (const [n, exp] of [[1, [1]], [7, [7]], [8, [7, 1]], [15, [7, 7, 1]], [22, [7, 7, 7, 1]]] as [number, number[]][]) {
      const m = new RoomManager(); for (let i = 0; i < n; i++) m.autoMatch('p' + i); expect(dist(m)).toEqual(exp); expect(m.online()).toBe(n);
    }
    const m = new RoomManager(); for (let i = 0; i < 100; i++) m.autoMatch('p' + i); expect(m.list().length).toBe(15); expect(Math.max(...m.list().map(r => r.players))).toBe(7);
  });
  it('code join: full / bad / unknown / ok', () => {
    const m = new RoomManager(); for (let i = 0; i < 5; i++) m.autoMatch('p' + i); const code = m.list()[0].code;
    expect(m.joinByCode('a', code).ok).toBe(true); expect(m.joinByCode('b', code).ok).toBe(true);
    expect(m.joinByCode('c', code)).toEqual({ ok: false, error: 'FULL' });
    expect(m.joinByCode('c', 'zz')).toEqual({ ok: false, error: 'BAD_CODE' }); expect(m.joinByCode('c', 'AAAAAA')).toEqual({ ok: false, error: 'NOT_FOUND' });
    expect(dist(m)).toEqual([7]);
  });
  it('last slot race: only one wins', () => {
    const m = new RoomManager(); for (let i = 0; i < 6; i++) m.autoMatch('p' + i); const code = m.list()[0].code;
    const rs = ['x', 'y', 'z'].map(p => m.joinByCode(p, code)); expect(rs.filter(r => r.ok).length).toBe(1);
  });
  it('same player never counted twice; leave frees slot; empty room closes', () => {
    const m = new RoomManager(); m.autoMatch('a', 0); m.autoMatch('a', 0); expect(m.online()).toBe(1); expect(m.list()[0].players).toBe(1);
    m.leave('a', 1000); expect(m.online()).toBe(0); m.expire(1000 + 29_000); expect(m.list().length).toBe(1); m.expire(1000 + 30_000); expect(m.list().length).toBe(0);
  });
  it('unique codes', () => { const m = new RoomManager(); for (let i = 0; i < 70; i++) m.autoMatch('p' + i); const c = m.list().map(r => r.code); expect(new Set(c).size).toBe(c.length); });
});
