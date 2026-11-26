import { WebSocketServer, WebSocket } from 'ws';
import { RoomManager, MAX_PLAYERS_PER_ROOM } from './rooms';
export function startServer(port: number, mgr = new RoomManager()) {
  const wss = new WebSocketServer({ port, maxPayload: 4096 });
  const conns = new Map<string, WebSocket>(); let seq = 0;
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
      else if (m.t === 'pos' && Number.isFinite(m.x) && Number.isFinite(m.z) && Math.abs(m.x) < 500 && Math.abs(m.z) < 500) broadcast(pid, { t: 'pos', id: pid, x: m.x, z: m.z, ry: Number(m.ry) || 0 });
    });
    ws.on('close', () => { clearInterval(iv); const rr = roomOf(pid); broadcast(pid, { t: 'left', id: pid }); conns.delete(pid); mgr.leave(pid); announce(rr); });
  });
  return { wss, mgr, close: () => new Promise<void>(res => { for (const c of wss.clients) c.terminate(); wss.close(() => res()); }) };
}
if (process.argv[1]?.endsWith('index.ts') || process.argv[1]?.endsWith('index.js')) { startServer(Number(process.env.PORT ?? 8080)); console.log('listening'); }
