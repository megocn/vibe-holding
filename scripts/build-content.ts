/**
 * 从 content/ 生成前端可直接 import 的单一 content.json（无运行时 fs 依赖）。
 * 用法：pnpm gen:content
 */
import { mkdirSync, readFileSync, readdirSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import process from 'node:process';
import { type SearchDoc, buildBundle, buildSearchDocs } from '@vh/core';

const CONTENT_DIR = join(process.cwd(), 'content');
const OUT = join(process.cwd(), 'apps/desktop/src/generated/content.json');

function readDir(sub: string): unknown[] {
  const dir = join(CONTENT_DIR, sub);
  let files: string[];
  try {
    files = readdirSync(dir).filter((f) => f.endsWith('.json'));
  } catch {
    return [];
  }
  const out: unknown[] = [];
  for (const f of files) {
    const data = JSON.parse(readFileSync(join(dir, f), 'utf8'));
    if (Array.isArray(data)) out.push(...data);
    else out.push(data);
  }
  return out;
}

function readRootJson(name: string): unknown[] {
  try {
    return JSON.parse(readFileSync(join(CONTENT_DIR, name), 'utf8'));
  } catch {
    return [];
  }
}

function readJsonObject(relPath: string): unknown {
  try {
    return JSON.parse(readFileSync(join(CONTENT_DIR, relPath), 'utf8'));
  } catch {
    return undefined;
  }
}

const bundle = {
  entries: readDir('entries'),
  edges: readDir('edges'),
  vendors: readDir('vendors'),
  concepts: readDir('concepts'),
  recipes: readDir('recipes'),
  categories: readRootJson('categories.json'),
  rankingSystems: readRootJson('ranking-systems.json'),
  popularity: readJsonObject('signals/popularity.json'),
};

// 预计算检索文档：运行时可直接装配索引，免去每次启动重建 haystack。
// 内容非法时（应由 `pnpm validate` 先拦截）跳过预计算，运行时回退即时构建。
let searchDocs: SearchDoc[] | undefined;
try {
  searchDocs = buildSearchDocs(buildBundle(bundle));
} catch (e) {
  console.warn(`⚠ 预计算检索索引跳过（内容未通过校验，运行时将回退即时构建）：${String(e)}`);
}

const out = searchDocs ? { ...bundle, searchDocs } : bundle;
mkdirSync(dirname(OUT), { recursive: true });
writeFileSync(OUT, `${JSON.stringify(out, null, 2)}\n`, 'utf8');
console.log(
  `已生成 ${OUT}\n  条目 ${bundle.entries.length} · 边 ${bundle.edges.length} · 厂商 ${bundle.vendors.length} · 概念 ${bundle.concepts.length} · 方案 ${bundle.recipes.length} · 分类 ${bundle.categories.length} · 排行体系 ${bundle.rankingSystems.length} · 检索文档 ${searchDocs?.length ?? 0}`,
);
