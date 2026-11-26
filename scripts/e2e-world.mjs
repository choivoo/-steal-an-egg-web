import { chromium } from 'playwright';
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--no-sandbox'] });
const mk = async () => { const p = await b.newPage({ viewport: { width: 844, height: 390 } }); await p.goto('http://localhost:4173/?ws=ws://localhost:8080'); return p; };
const A = await mk(), B = await mk(); await A.waitForTimeout(3000);
const goto = (p, x, z) => p.evaluate(([x, z]) => window.__game.player.position.set(x, 0, z), [x, z]);
await goto(A, -12, -64); await goto(B, -12, -64); await A.waitForTimeout(5000); // 서버 속도제한 때문에 도착 대기
const st = p => p.evaluate(() => ({ carried: !!window.__game.carried, eggTaken: window.__game.wild.map(w => w.taken) }));
await A.evaluate(() => window.__game.interact()); await B.evaluate(() => window.__game.interact()); await A.waitForTimeout(800);
console.log('A', await st(A)); console.log('B', await st(B));
await A.waitForTimeout(9000); console.log('A after chase (stationary => caught)', await st(A)); console.log('B egg view', await st(B));
console.log('A msg:', await A.textContent('#msg'));
await b.close();
