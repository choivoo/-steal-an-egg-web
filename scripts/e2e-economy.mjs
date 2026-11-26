import { chromium } from 'playwright';
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--no-sandbox'] });
const ctx = await b.newContext({ viewport: { width: 844, height: 390 } }); const p = await ctx.newPage(); const errs = [];
p.on('pageerror', e => errs.push(String(e)));
const URL = 'http://localhost:4173/?ws=ws://localhost:8080';
await p.goto(URL); await p.waitForTimeout(3000);
await p.evaluate(() => window.__game.player.position.set(8, 0, 6)); await p.waitForTimeout(2500); // 서버 속도제한 때문에 도착 대기
await p.evaluate(() => window.__game.interact()); await p.waitForTimeout(3500);
const tr = await p.evaluate(() => window.__game.save().train); console.log('server-driven train after ~3.5s:', tr.toFixed(2));
await p.evaluate(() => { window.__game.save().money = 1e12; }); // 로컬 조작
console.log('tampered money (local):', await p.evaluate(() => window.__game.save().money));
await p.click('#shop', { force: true }).catch(() => {}); await p.evaluate(() => document.getElementById('shop').dispatchEvent(new PointerEvent('pointerdown', { bubbles: true }))); await p.waitForTimeout(2500);
console.log('after server sync, money:', await p.evaluate(() => window.__game.save().money), 'treadmill:', await p.evaluate(() => window.__game.save().treadmill));
await p.evaluate(() => window.__game.interact()); await p.waitForTimeout(700);
const t1 = await p.evaluate(() => window.__game.save().train);
await p.reload(); await p.waitForTimeout(3500);
const t2 = await p.evaluate(() => window.__game.save().train); console.log('train before reload', t1.toFixed(2), 'after reload', t2.toFixed(2)); console.log('HUD:', await p.textContent('#net'), '| errors', errs);
await b.close();
