import { WebSocketServer, WebSocket } from 'ws';
import { World } from './world';
import { RoomManager, MAX_PLAYERS_PER_ROOM } from './rooms';
export function startServer(port: number, mgr = new RoomManager()) {
  const wss = new WebSocketServer({ port, maxPayload: 4096 });
  const conns = new Map<string, WebSocket>(); let seq = 0; const worlds = new Map<number, World>();
  const worldOf = (pid: string) => { const r = roomOf(pid); if (!r) return undefined; let w = worlds.get(r.id); if (!w) { w = new World(); worlds.set(r.id, w); } return w; };
  const send = (evs: { to: string; msg: any }[]) => { for (const e of evs) conns.get(e.to)?.send(JSON.stringify(e.msg)); };
  const loop = setInterval(() => { const now = Date.now(); let n = 0; for (const [id, w] of worlds) { const r = mgr.rooms.get(id); if (!r) { worlds.delete(id); continue; } send(w.tick(0.05, now)); if (++n >= 0 && now % 100 < 50) { const m = JSON.stringify(w.snap()); for (const q of r.players) conns.get(q)?.send(m); } } mgr.expire(now); }, 50);
  const roomOf = (pid: string) => mgr.rooms.get([...mgr.rooms.values()].find(r => r.players.has(pid))?.id ?? -1);
  const broadcast = (pid: string, msg: object) => { const r = roomOf(pid); if (!r) return; const s = JSON.stringify(msg); for (const q of r.players) if (q !== pid) conns.get(q)?.send(s); };
  const info = (pid: string) => { const r = roomOf(pid)!; return { t: 'joined', you: pid, others: [...r.players].filter(q => q !== pid), room: r.id, code: r.code, players: r.players.size, max: MAX_PLAYERS_PER_ROOM, online: mgr.online(), servers: mgr.rooms.size }; };
  const announce = (r: { players: Set<string> } | undefined) => { if (!r) return; const m = JSON.stringify({ t: 'count', players: r.players.size, online: mgr.online(), servers: mgr.rooms.size }); for (const q of r.players) conns.get(q)?.send(m); };
  wss.on('connection', ws => {
    const pid = 'u' + ++seq; conns.set(pid, ws); let rate = 0; const iv = setInterval(() => rate = 0, 1000);
    ws.on('message', raw => {
      if (++rate > 60) return; let m: any; try { m = JSON.parse(raw.toString()); } catch { return; }
      if (m.t === 'match') { mgr.autoMatch(pid); ws.send(JSON.stringify(info(pid))); announce(roomOf(pid)); }
      else if (m.t === 'code') { const r = mgr.joinByCode(pid, String(m.code ?? '')); ws.send(JSON.stringify(r.ok ? info(pid) : { t: 'error', error: r.error })); if (r.ok) announce(roomOf(pid)); }
      else if (m.t === 'pos' && Number.isFinite(m.x) && Number.isFinite(m.z) && Math.abs(m.x) < 500 && Math.abs(m.z) < 500) { const w = worldOf(pid); w?.report(pid, m.x, m.z, Date.now()); const pp = w?.pos.get(pid); broadcast(pid, { t: 'pos', id: pid, x: pp?.x ?? m.x, z: pp?.z ?? m.z, ry: Number(m.ry) || 0 }); }
      else if (m.t === 'steal' && Number.isInteger(m.i)) { const w = worldOf(pid); if (w) send(w.steal(pid, m.i, Date.now())); }
    });
    ws.on('close', () => { clearInterval(iv); const rr = roomOf(pid); send(worldOf(pid)?.remove(pid, Date.now()) ?? []); broadcast(pid, { t: 'left', id: pid }); conns.delete(pid); mgr.leave(pid); announce(rr); });
  });
  return { wss, mgr, close: () => new Promise<void>(res => { clearInterval(loop); for (const c of wss.clients) c.terminate(); wss.close(() => res()); }) };
}
if (process.argv[1]?.endsWith('index.ts') || process.argv[1]?.endsWith('index.js')) { startServer(Number(process.env.PORT ?? 8080)); console.log('listening'); }
