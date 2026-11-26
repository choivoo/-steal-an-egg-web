export const MAX_PLAYERS_PER_ROOM = 7;
export type RoomState = 'OPEN' | 'FULL' | 'DRAINING' | 'CLOSED';
export interface Room { id: number; code: string; players: Set<string>; reserved: Map<string, number>; state: RoomState; emptySince: number | null }
const ALPHA = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
export type JoinResult = { ok: true; room: Room } | { ok: false; error: 'BAD_CODE' | 'NOT_FOUND' | 'FULL' | 'DRAINING' };
export class RoomManager {
  rooms = new Map<number, Room>(); private seq = 0; private byPlayer = new Map<string, number>();
  constructor(private rnd: () => number = Math.random, private emptyGraceMs = 30_000, private reserveMs = 15_000) {}
  private count(r: Room) { return r.players.size + r.reserved.size; }
  private code(): string { for (;;) { let c = ''; for (let i = 0; i < 6; i++) c += ALPHA[Math.floor(this.rnd() * ALPHA.length)]; if (![...this.rooms.values()].some(r => r.code === c)) return c; } }
  private create(): Room { const r: Room = { id: ++this.seq, code: this.code(), players: new Set(), reserved: new Map(), state: 'OPEN', emptySince: null }; this.rooms.set(r.id, r); return r; }
  private refresh(r: Room) { if (r.state === 'OPEN' || r.state === 'FULL') r.state = this.count(r) >= MAX_PLAYERS_PER_ROOM ? 'FULL' : 'OPEN'; }
  /** 슬롯 점유(동기 = 원자적). 이미 접속한 플레이어는 이전 방에서 먼저 제거(중복 접속 방지). */
  private seat(r: Room, pid: string, now: number): Room { this.leave(pid, now); r.players.add(pid); this.byPlayer.set(pid, r.id); r.emptySince = null; this.refresh(r); return r; }
  /** 자동 매칭: 사람이 있는 OPEN 방 우선(가장 많은 방), 없으면 새 방 */
  autoMatch(pid: string, now = Date.now()): Room {
    this.expire(now);
    const cur = this.byPlayer.get(pid); if (cur != null && this.rooms.has(cur)) return this.rooms.get(cur)!;
    const cands = [...this.rooms.values()].filter(r => r.state === 'OPEN' && this.count(r) < MAX_PLAYERS_PER_ROOM && !r.players.has(pid));
    cands.sort((a, b) => b.players.size - a.players.size || a.id - b.id);
    return this.seat(cands[0] ?? this.create(), pid, now);
  }
  joinByCode(pid: string, code: string, now = Date.now()): JoinResult {
    if (!/^[A-Z0-9]{6}$/.test(code.toUpperCase())) return { ok: false, error: 'BAD_CODE' };
    const r = [...this.rooms.values()].find(x => x.code === code.toUpperCase() && x.state !== 'CLOSED');
    if (!r) return { ok: false, error: 'NOT_FOUND' };
    if (r.state === 'DRAINING') return { ok: false, error: 'DRAINING' };
    if (r.players.has(pid)) return { ok: true, room: r };
    if (this.count(r) >= MAX_PLAYERS_PER_ROOM) return { ok: false, error: 'FULL' };
    return { ok: true, room: this.seat(r, pid, now) };
  }
  leave(pid: string, now = Date.now()) { const id = this.byPlayer.get(pid); if (id == null) return; this.byPlayer.delete(pid); const r = this.rooms.get(id); if (!r) return; r.players.delete(pid); if (r.state === 'FULL') r.state = 'OPEN'; if (r.players.size === 0) r.emptySince = now; }
  /** 빈 방 유예 후 종료 */
  expire(now: number) { for (const [id, r] of this.rooms) if (r.players.size === 0 && r.emptySince != null && now - r.emptySince >= this.emptyGraceMs) { r.state = 'CLOSED'; this.rooms.delete(id); } }
  online(): number { return this.byPlayer.size; }
  list() { return [...this.rooms.values()].map(r => ({ id: r.id, code: r.code, players: r.players.size, max: MAX_PLAYERS_PER_ROOM, state: r.state })); }
}
