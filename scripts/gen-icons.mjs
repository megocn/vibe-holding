/**
 * 占位纯色图标（仅紧急兜底）。
 * 正式图标：宣纸底 + 朱砂方印竖排「墨台」
 *   python3 scripts/gen-app-icon.py
 *   pnpm --filter @vh/desktop exec tauri icon public/brand/app-icon-1024.png -o src-tauri/icons
 * 用法：node scripts/gen-icons.mjs
 */
import { mkdirSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { deflateSync } from 'node:zlib';

const OUT_DIR = join(process.cwd(), 'apps/desktop/src-tauri/icons');
const COLOR = [176, 58, 42]; // 朱砂近似，与 gen-app-icon.py 一致

const CRC_TABLE = (() => {
  const table = new Int32Array(256);
  for (let n = 0; n < 256; n++) {
    let c = n;
    for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
    table[n] = c;
  }
  return table;
})();

function crc32(buf) {
  let c = 0xffffffff;
  for (let i = 0; i < buf.length; i++) c = CRC_TABLE[(c ^ buf[i]) & 0xff] ^ (c >>> 8);
  return (c ^ 0xffffffff) >>> 0;
}

function chunk(type, data) {
  const typeBuf = Buffer.from(type, 'ascii');
  const len = Buffer.alloc(4);
  len.writeUInt32BE(data.length, 0);
  const crc = Buffer.alloc(4);
  crc.writeUInt32BE(crc32(Buffer.concat([typeBuf, data])), 0);
  return Buffer.concat([len, typeBuf, data, crc]);
}

function png(size, [r, g, b]) {
  const sig = Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]);
  const ihdr = Buffer.alloc(13);
  ihdr.writeUInt32BE(size, 0);
  ihdr.writeUInt32BE(size, 4);
  ihdr[8] = 8;
  ihdr[9] = 6;
  const row = Buffer.alloc(1 + size * 4);
  for (let x = 0; x < size; x++) {
    const o = 1 + x * 4;
    row[o] = r;
    row[o + 1] = g;
    row[o + 2] = b;
    row[o + 3] = 255;
  }
  const raw = Buffer.concat(Array.from({ length: size }, () => row));
  const idat = deflateSync(raw, { level: 9 });
  return Buffer.concat([sig, chunk('IHDR', ihdr), chunk('IDAT', idat), chunk('IEND', Buffer.alloc(0))]);
}

const sizes = {
  32: '32x32.png',
  128: '128x128.png',
  256: '128x128@2x.png',
  512: 'icon.png',
};

mkdirSync(OUT_DIR, { recursive: true });
for (const [size, name] of Object.entries(sizes)) {
  writeFileSync(join(OUT_DIR, name), png(Number(size), COLOR));
}
console.log(
  `已生成占位图标于 ${OUT_DIR}（正式请用 scripts/gen-app-icon.py + tauri icon）: ${Object.values(sizes).join(', ')}`,
);
