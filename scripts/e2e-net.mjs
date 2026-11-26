// 사용: 서버(8080)와 vite preview(4173) 기동 후 실행
import { chromium } from 'playwright';
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--no-sandbox'] });
const mk = async () => { const p = await b.newPage({ viewport: { width: 844, height: 390 } }); await p.goto('http://localhost:4173/?ws=ws://localhost:8080'); return p; };
const A = await mk(), B = await mk(); await A.waitForTimeout(3500);
await A.evaluate(() => { window.__game.player.position.set(20, 0, 20); }); await A.waitForTimeout(1200);
console.log('A HUD:', await A.textContent('#net'));
console.log('B sees remotes:', await B.evaluate(() => [...window.__game.remotes.values()].map(r => [r.o.position.x.toFixed(1), r.o.position.z.toFixed(1)])));
await A.close(); await B.waitForTimeout(1200);
console.log('after A left, B remotes:', await B.evaluate(() => window.__game.remotes.size), '| B HUD:', await B.textContent('#net'));
await b.close();
