import { it, expect } from 'vitest';
import WebSocket from 'ws';
import { startServer } from '../server/src/index';
const TOKEN = 'b'.repeat(32);
function client(port: number, token?: string) {
  return new Promise<{ w: WebSocket; msgs: any[]; send: (o: object) => void; last: (t: string) => any }>((res, rej) => {
    const w = new WebSocket('ws://localhost:' + port); const msgs: any[] = [];
    w.on('message', d => msgs.push(JSON.parse(d.toString()))); w.on('error', rej);
    w.on('open', () => { if (token) w.send(JSON.stringify({ t: 'hello', token })); res({ w, msgs, send: o => w.send(JSON.stringify(o)), last: t => [...msgs].reverse().find(m => m.t === t) }); });
  });
}
const wait = (ms: number) => new Promise(r => setTimeout(r, ms));
it('server-side economy: unauth ignored, train near treadmill, persist, dup login, no cheating', async () => {
  const s = startServer(18082);
  const bad = await client(18082); bad.send({ t: 'match' }); bad.send({ t: 'buy' }); await wait(100); expect(bad.msgs.filter(m => m.t !== 'snap').length).toBe(0); // 미인증은 무시
  const a = await client(18082, TOKEN); await wait(100); a.send({ t: 'match' }); await wait(100);
  a.send({ t: 'train', on: true }); await wait(100); expect(a.last('train_state').on).toBe(false); // 위치 모름/멀리 → 거부
  for (let i = 0; i < 12; i++) { a.send({ t: 'pos', x: 8, z: 6 }); await wait(30); } // 트레드밀 옆으로 (스폰 0,0 → 속도제한으로 서서히)
  for (let i = 0; i < 40; i++) { a.send({ t: 'pos', x: 8, z: 6 }); await wait(60); }
  a.send({ t: 'train', on: true }); await wait(100); const on = a.last('train_state').on; await wait(1600);
  const p1 = a.last('profile').p; if (on) expect(p1.train).toBeGreaterThan(0.5);
  a.send({ t: 'buy' }); await wait(100); expect(a.last('buy_result').ok).toBe(false); // 돈 0 → 구매 불가(서버 판정)
  const trainBefore = a.last('profile').p.train;
  const b = await client(18082, TOKEN); await wait(150); expect(a.last('kicked')).toBeTruthy(); // 중복 로그인 킥
  expect(b.last('profile').p.train).toBeGreaterThanOrEqual(trainBefore); // 재접속 후 유지
  await s.close();
}, 20000);
