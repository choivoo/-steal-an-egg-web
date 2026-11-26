import { it, expect } from 'vitest';
import WebSocket from 'ws';
import { startServer } from '../server/src/index';
import { RoomManager } from '../server/src/rooms';
import { MemoryStore, keyOf } from '../server/src/profiles';
const OWNER = 'd'.repeat(32), P1 = 'e'.repeat(32), P2 = 'f'.repeat(32);
const wait = (ms: number) => new Promise(r => setTimeout(r, ms));
function client(port: number, token: string) { return new Promise<{ msgs: any[]; send: (o: object) => void; last: (t: string) => any }>(res => { const w = new WebSocket('ws://localhost:' + port); const msgs: any[] = []; w.on('message', d => msgs.push(JSON.parse(d.toString()))); w.on('open', () => { w.send(JSON.stringify({ t: 'hello', token })); res({ msgs, send: o => w.send(JSON.stringify(o)), last: t => [...msgs].reverse().find(m => m.t === t) }); }); }); }
it('global admin event reaches every public server; players cannot use admin; /status & /health real', async () => {
  const store = new MemoryStore(); const s = startServer(18083, new RoomManager(), store, { roles: `${keyOf(OWNER)}:OWNER` });
  const players = []; for (let i = 0; i < 8; i++) { const c = await client(18083, (i + 1).toString(16).padStart(32, 'a')); await wait(40); c.send({ t: 'match' }); players.push(c); }
  await wait(200); expect(s.mgr.list().map(r => r.players).sort()).toEqual([1, 7]); // 서버 2개
  const p = await client(18083, P1); await wait(60); p.send({ t: 'admin', cmd: '/event start treadmill 8x 120m global' }); await wait(100); expect(p.last('admin_result').ok).toBe(false);
  const o = await client(18083, OWNER); await wait(60); expect(o.last('hello_ok').role).toBe('OWNER');
  o.send({ t: 'admin', cmd: '/event start treadmill 8x 120m global' }); await wait(200); expect(o.last('admin_result').ok).toBe(true);
  for (const c of players) { expect(c.last('events').list.some((e: any) => e.kind === 'treadmill' && e.mult === 8)).toBe(true); expect(c.last('announce').text).toContain('ADMIN EVENT'); } // 두 서버 모두
  const late = await client(18083, P2); await wait(100); expect(late.last('events').list[0].mult).toBe(8); // 이벤트 중 신규 접속자도 적용
  const st = await (await fetch('http://localhost:18083/status')).json(); expect(st.online).toBe(8); expect(st.servers).toBe(2); expect(st.events.length).toBe(1);
  expect((await fetch('http://localhost:18083/health')).status).toBe(200);
  await s.close();
  const s2 = startServer(18084, new RoomManager(), store); await wait(100); expect(s2.events.active(Date.now()).length).toBe(1); await s2.close(); // 재시작 후 이벤트 복원
}, 20000);
