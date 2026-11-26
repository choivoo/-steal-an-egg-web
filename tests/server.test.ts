import { it, expect } from 'vitest';
import WebSocket from 'ws';
import { startServer } from '../server/src/index';
const open = (port: number) => new Promise<WebSocket>((res, rej) => { const w = new WebSocket('ws://localhost:' + port); w.on('open', () => res(w)); w.on('error', rej); });
const ask = (w: WebSocket, msg: object) => new Promise<any>(res => { w.once('message', d => res(JSON.parse(d.toString()))); w.send(JSON.stringify(msg)); });
it('15 real sockets -> 7+7+1, code join, pos sync, disconnect', async () => {
  const s = startServer(18081); const ws: WebSocket[] = []; const infos: any[] = [];
  for (let i = 0; i < 15; i++) { const w = await open(18081); ws.push(w); infos.push(await ask(w, { t: 'match' })); }
  const sizes = s.mgr.list().map(r => r.players).sort((a, b) => b - a); expect(sizes).toEqual([7, 7, 1]); expect(infos[14].online).toBe(15);
  const full = infos[0].code; const extra = await open(18081); expect((await ask(extra, { t: 'code', code: full })).error).toBe('FULL');
  expect((await ask(extra, { t: 'code', code: 'x' })).error).toBe('BAD_CODE');
  const got = new Promise<any>(r => ws[1].once('message', d => r(JSON.parse(d.toString())))); ws[0].send(JSON.stringify({ t: 'pos', x: 3, z: 4 }));
  expect((await got).x).toBe(3);
  ws[0].close(); await new Promise(r => setTimeout(r, 100)); expect(s.mgr.online()).toBe(14);
  await s.close();
});
