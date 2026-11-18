// node render.js [--snap 1,5,9] : serves the repo, renders index.html frame by frame -> video.mp4 (silent) + events.json
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const http = require('http'), fs = require('fs'), path = require('path');

const FPS = 30, HERE = __dirname, ROOT = path.resolve(HERE, '..', '..');
const TYPES = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json', '.woff2': 'font/woff2' };
const server = http.createServer((req, res) => {
  const f = path.join(ROOT, decodeURIComponent(req.url.split('?')[0]));
  if (!f.startsWith(ROOT) || !fs.existsSync(f) || fs.statSync(f).isDirectory()) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'Content-Type': TYPES[path.extname(f)] || 'application/octet-stream' }); fs.createReadStream(f).pipe(res);
});
(async () => {
  await new Promise(r => server.listen(0, '127.0.0.1', r));
  const url = `http://127.0.0.1:${server.address().port}/${path.relative(ROOT, HERE)}/index.html`;
  const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  page.on('pageerror', e => console.error('page error:', e.message));
  page.on('console', m => { if (m.type() === 'error') console.error('console:', m.text()); });
  await page.goto(url);
  await page.waitForFunction(() => window.READY === true, null, { timeout: 60000 });
  const info = await page.evaluate(() => ({ total: window.TOTAL, events: window.EVENTS, music_off: window.MUSIC_OFF, sections: window.SECTIONS }));
  fs.writeFileSync(path.join(HERE, 'events.json'), JSON.stringify(info, null, 1));
  const grab = async t => Buffer.from((await page.evaluate(t => { render(t); return document.getElementById('c').toDataURL('image/jpeg', 0.93); }, t)).split(',')[1], 'base64');
  const snap = process.argv.indexOf('--snap');
  if (snap > 0) {
    const dir = path.join(HERE, 'snaps'); fs.mkdirSync(dir, { recursive: true });
    for (const t of process.argv[snap + 1].split(',').map(Number)) fs.writeFileSync(path.join(dir, `t${String(t.toFixed(2)).padStart(5, '0')}.jpg`), await grab(t));
    console.log(`snaps written (total ${info.total.toFixed(2)} s)`);
  } else {
    const n = Math.round(info.total * FPS);
    const ff = spawn('ffmpeg', ['-v', 'error', '-y', '-f', 'image2pipe', '-c:v', 'mjpeg', '-framerate', String(FPS), '-i', '-',
      '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', path.join(HERE, 'video.mp4')], { stdio: ['pipe', 'inherit', 'inherit'] });
    const t0 = Date.now();
    for (let i = 0; i < n; i++) {
      const buf = await grab(i / FPS);
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
      if (i % 90 === 0) console.log(`frame ${i}/${n}  ${((Date.now() - t0) / 1000).toFixed(0)} s`);
    }
    ff.stdin.end(); await new Promise(r => ff.on('close', r));
    console.log(`rendered ${n} frames (${info.total.toFixed(2)} s)`);
  }
  await browser.close(); server.close();
})();
