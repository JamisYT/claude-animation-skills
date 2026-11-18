// node render.js [--snap 1.2,5,9] : renders index.html frame by frame into video.mp4 (silent) + events.json
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

const FPS = 30, HERE = __dirname;
(async () => {
  const snapArg = process.argv.indexOf('--snap');
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  const voFile = path.join(HERE, 'vo', 'vo.json');
  if (fs.existsSync(voFile)) await page.addInitScript(d => { window.VO = d; }, JSON.parse(fs.readFileSync(voFile)).durs);
  await page.goto('file://' + path.join(HERE, 'index.html'));
  await page.evaluate(async () => { await Promise.all(['IT', 'I7', 'I6', 'M'].map(f => document.fonts.load(`40px ${f}`))); });
  const { total, events } = await page.evaluate(() => ({ total: window.TOTAL, events: window.EVENTS }));
  fs.writeFileSync(path.join(HERE, 'events.json'), JSON.stringify({ total, events }, null, 1));
  const grab = async t => Buffer.from((await page.evaluate(t => { render(t); return document.getElementById('c').toDataURL('image/jpeg', 0.95); }, t)).split(',')[1], 'base64');

  if (snapArg > 0) {
    const dir = path.join(HERE, 'snaps'); fs.mkdirSync(dir, { recursive: true });
    for (const t of process.argv[snapArg + 1].split(',').map(Number)) fs.writeFileSync(path.join(dir, `t${t.toFixed(2)}.jpg`), await grab(t));
    console.log('snaps written'); await browser.close(); return;
  }
  const n = Math.round(total * FPS);
  const ff = spawn('ffmpeg', ['-v', 'error', '-y', '-f', 'image2pipe', '-c:v', 'mjpeg', '-framerate', String(FPS), '-i', '-',
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', path.join(HERE, 'video.mp4')], { stdio: ['pipe', 'inherit', 'inherit'] });
  for (let i = 0; i < n; i++) {
    const buf = await grab(i / FPS);
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if (i % 60 === 0) process.stdout.write(`\rframe ${i}/${n}`);
  }
  ff.stdin.end(); await new Promise(r => ff.on('close', r));
  console.log(`\nrendered ${n} frames (${total.toFixed(2)} s)`);
  await browser.close();
})();
