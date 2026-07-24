/**
 * 一次性迁移：把 content/{edges,vendors,concepts}/seed.json 巨型数组拆成「一条一文件」。
 * 目的：降低社区共建时的 merge 冲突、便于逐条 review 与 git blame。
 * 用法：node scripts/split-content.mjs
 * 幂等：seed.json 不存在则跳过；已拆分的目录再次运行无副作用。
 */
import { readFileSync, readdirSync, rmSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import process from 'node:process';

const CONTENT_DIR = join(process.cwd(), 'content');
const SUBS = ['edges', 'vendors', 'concepts'];

/** 文件名安全化：id 已受 schema 约束，这里仅兜底非法字符。 */
function safeName(id) {
  return String(id).replace(/[^a-zA-Z0-9._-]/g, '_');
}

for (const sub of SUBS) {
  const dir = join(CONTENT_DIR, sub);
  const seed = join(dir, 'seed.json');
  let arr;
  try {
    arr = JSON.parse(readFileSync(seed, 'utf8'));
  } catch (e) {
    if (e.code === 'ENOENT') {
      console.log(`· ${sub}/seed.json 不存在，跳过`);
      continue;
    }
    throw e;
  }
  if (!Array.isArray(arr)) {
    console.warn(`⚠ ${sub}/seed.json 非数组，跳过`);
    continue;
  }

  const seen = new Set();
  let written = 0;
  for (const item of arr) {
    const id = item?.id;
    if (!id) {
      console.warn(`⚠ ${sub}: 存在缺少 id 的条目，跳过 ${JSON.stringify(item).slice(0, 80)}`);
      continue;
    }
    const name = safeName(id);
    if (seen.has(name)) {
      console.warn(`⚠ ${sub}: 文件名冲突 ${name}.json（id "${id}"），后者覆盖前者`);
    }
    seen.add(name);
    writeFileSync(join(dir, `${name}.json`), `${JSON.stringify(item, null, 2)}\n`, 'utf8');
    written++;
  }

  rmSync(seed);
  console.log(`✓ ${sub}: 拆分 ${written} 条 → 一条一文件，已删除 seed.json`);

  const remaining = readdirSync(dir).filter((f) => f.endsWith('.json')).length;
  console.log(`  当前 ${sub}/ 下 ${remaining} 个 .json`);
}

console.log('\n拆分完成。请运行 `pnpm validate` 与 `pnpm gen:content` 验证。');
