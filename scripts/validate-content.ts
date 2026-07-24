/**
 * 内容仓库校验脚本（SPEC §6 六条规则）。
 * 用法：pnpm validate
 * 聚合报告所有错误/警告；有错误则退出码 1。
 */
import { readFileSync, readdirSync } from 'node:fs';
import { join } from 'node:path';
import process from 'node:process';
import {
  Category,
  Concept,
  Edge,
  Entry,
  PopularitySnapshot,
  RankingSystem,
  StackRecipe,
  Vendor,
  isSymmetric,
} from '@vh/core';
import type { z } from 'zod';

const CONTENT_DIR = join(process.cwd(), 'content');
const STALE_DAYS = 180;

interface Problem {
  code: string;
  file: string;
  msg: string;
}
const errors: Problem[] = [];
const warnings: Problem[] = [];

function readDir(sub: string): { file: string; item: unknown }[] {
  const dir = join(CONTENT_DIR, sub);
  let files: string[];
  try {
    files = readdirSync(dir).filter((f) => f.endsWith('.json'));
  } catch {
    return [];
  }
  const out: { file: string; item: unknown }[] = [];
  for (const f of files) {
    const path = join(sub, f);
    try {
      const data = JSON.parse(readFileSync(join(dir, f), 'utf8'));
      const arr = Array.isArray(data) ? data : [data];
      for (const item of arr) out.push({ file: path, item });
    } catch (e) {
      errors.push({ code: 'E_JSON', file: path, msg: `JSON 解析失败: ${String(e)}` });
    }
  }
  return out;
}

// Rule 1: schema 校验
function parseAll<T>(sub: string, schema: z.ZodType<T>): { file: string; value: T }[] {
  const rows = readDir(sub);
  const out: { file: string; value: T }[] = [];
  for (const { file, item } of rows) {
    const r = schema.safeParse(item);
    if (r.success) out.push({ file, value: r.data });
    else {
      for (const issue of r.error.issues) {
        errors.push({
          code: 'E_SCHEMA',
          file,
          msg: `${issue.path.join('.') || '(root)'}: ${issue.message}`,
        });
      }
    }
  }
  return out;
}

// categories.json 位于 content 根，单独处理
const categoryRows: { file: string; value: z.infer<typeof Category> }[] = [];
try {
  const data = JSON.parse(readFileSync(join(CONTENT_DIR, 'categories.json'), 'utf8'));
  for (const item of data as unknown[]) {
    const r = Category.safeParse(item);
    if (r.success) categoryRows.push({ file: 'categories.json', value: r.data });
    else
      for (const issue of r.error.issues)
        errors.push({ code: 'E_SCHEMA', file: 'categories.json', msg: issue.message });
  }
} catch (e) {
  errors.push({ code: 'E_JSON', file: 'categories.json', msg: String(e) });
}

// ranking-systems.json：权威排行体系注册表
const rankingSystemRows: { file: string; value: z.infer<typeof RankingSystem> }[] = [];
try {
  const data = JSON.parse(readFileSync(join(CONTENT_DIR, 'ranking-systems.json'), 'utf8'));
  if (!Array.isArray(data)) {
    errors.push({ code: 'E_SCHEMA', file: 'ranking-systems.json', msg: '须为数组' });
  } else {
    for (const item of data as unknown[]) {
      const r = RankingSystem.safeParse(item);
      if (r.success) rankingSystemRows.push({ file: 'ranking-systems.json', value: r.data });
      else
        for (const issue of r.error.issues)
          errors.push({
            code: 'E_SCHEMA',
            file: 'ranking-systems.json',
            msg: `${issue.path.join('.') || '(root)'}: ${issue.message}`,
          });
    }
  }
} catch (e) {
  if ((e as NodeJS.ErrnoException).code !== 'ENOENT') {
    errors.push({ code: 'E_JSON', file: 'ranking-systems.json', msg: String(e) });
  }
}

const entries = parseAll('entries', Entry);
const edges = parseAll('edges', Edge);
const vendors = parseAll('vendors', Vendor);
const concepts = parseAll('concepts', Concept);
const recipes = parseAll('recipes', StackRecipe);

// 节点 id 集合（供边引用）
const nodeIds = new Set<string>();
const idOwner = new Map<string, string>();
function registerId(id: string, file: string) {
  // Rule 3: 全局 id 唯一
  if (idOwner.has(id)) {
    errors.push({
      code: 'E_DUP_ID',
      file,
      msg: `id "${id}" 重复（另见 ${idOwner.get(id)}）`,
    });
  } else {
    idOwner.set(id, file);
  }
  nodeIds.add(id);
}
for (const { file, value } of entries) registerId(value.id, file);
for (const { file, value } of vendors) registerId(value.id, file);
for (const { file, value } of concepts) registerId(value.id, file);
for (const { file, value } of recipes) registerId(value.id, file);
for (const { file, value } of categoryRows) registerId(value.id, file);

// feeds.json：情报订阅源（entryId 须存在）
try {
  const feedsRaw = JSON.parse(readFileSync(join(CONTENT_DIR, 'feeds.json'), 'utf8')) as unknown;
  if (!Array.isArray(feedsRaw)) {
    errors.push({ code: 'E_SCHEMA', file: 'feeds.json', msg: '须为数组' });
  } else {
    feedsRaw.forEach((item, i) => {
      if (!item || typeof item !== 'object') {
        errors.push({ code: 'E_SCHEMA', file: 'feeds.json', msg: `[${i}] 须为对象` });
        return;
      }
      const row = item as { entryId?: unknown; url?: unknown };
      if (typeof row.entryId !== 'string' || typeof row.url !== 'string') {
        errors.push({
          code: 'E_SCHEMA',
          file: 'feeds.json',
          msg: `[${i}] 需要 string 字段 entryId、url`,
        });
        return;
      }
      try {
        new URL(row.url);
      } catch {
        errors.push({ code: 'E_SCHEMA', file: 'feeds.json', msg: `[${i}] url 非法: ${row.url}` });
      }
      if (!nodeIds.has(row.entryId)) {
        errors.push({
          code: 'E_REF',
          file: 'feeds.json',
          msg: `[${i}] entryId "${row.entryId}" 不存在`,
        });
      }
    });
  }
} catch (e) {
  // feeds.json 可选：不存在则跳过
  if ((e as NodeJS.ErrnoException).code !== 'ENOENT') {
    errors.push({ code: 'E_JSON', file: 'feeds.json', msg: String(e) });
  }
}

const categoryIds = new Set(categoryRows.map((c) => c.value.id));
const vendorIds = new Set(vendors.map((v) => v.value.id));
const rankingSystemIds = new Set(rankingSystemRows.map((r) => r.value.id));
const rankingSystemById = new Map(rankingSystemRows.map((r) => [r.value.id, r.value]));

// 排行体系：id 唯一 + categories 引用存在；仅 leaf 建议 1–2 套（section 不挂排行）
const systemsPerCategory = new Map<string, string[]>();
const categoryById = new Map(categoryRows.map((r) => [r.value.id, r.value]));
for (const { file, value } of rankingSystemRows) {
  if (idOwner.has(value.id)) {
    errors.push({
      code: 'E_DUP_ID',
      file,
      msg: `排行体系 id "${value.id}" 与 ${idOwner.get(value.id)} 冲突`,
    });
  } else {
    idOwner.set(value.id, file);
  }
  for (const cat of value.categories) {
    if (!categoryIds.has(cat))
      errors.push({
        code: 'E_REF',
        file,
        msg: `排行体系 ${value.id} 的 category "${cat}" 不存在`,
      });
    else if (categoryById.get(cat)?.kind === 'section')
      warnings.push({
        code: 'W_RANKING_SECTION',
        file,
        msg: `排行体系 ${value.id} 挂在 section "${cat}" 上；应挂 leaf（可比较单元）`,
      });
    const list = systemsPerCategory.get(cat) ?? [];
    list.push(value.id);
    systemsPerCategory.set(cat, list);
  }
}
for (const { value: cat } of categoryRows) {
  if (cat.kind !== 'leaf') continue;
  if (cat.parent && !categoryIds.has(cat.parent))
    errors.push({
      code: 'E_REF',
      file: 'categories.json',
      msg: `leaf "${cat.id}" 的 parent "${cat.parent}" 不存在`,
    });
  else if (cat.parent && categoryById.get(cat.parent)?.kind !== 'section')
    errors.push({
      code: 'E_REF',
      file: 'categories.json',
      msg: `leaf "${cat.id}" 的 parent 必须是 section`,
    });
  const n = systemsPerCategory.get(cat.id)?.length ?? 0;
  if (n === 0)
    warnings.push({
      code: 'W_RANKING_GAP',
      file: 'ranking-systems.json',
      msg: `叶类 "${cat.id}" 尚未配置权威排行体系（建议 1–2 套）`,
    });
  else if (n > 3)
    warnings.push({
      code: 'W_RANKING_MANY',
      file: 'ranking-systems.json',
      msg: `叶类 "${cat.id}" 配置了 ${n} 套排行体系（建议收敛到 1–2 套主榜）`,
    });
}

// Rule 7(附加): entry.category / vendorId / rankings.systemId 引用存在
for (const { file, value } of entries) {
  if (!categoryIds.has(value.category))
    errors.push({ code: 'E_REF', file, msg: `category "${value.category}" 不存在` });
  else if (categoryById.get(value.category)?.kind === 'section')
    errors.push({
      code: 'E_REF',
      file,
      msg: `category "${value.category}" 是图廓 section；条目必须挂 leaf`,
    });
  if (value.vendorId && !vendorIds.has(value.vendorId))
    errors.push({ code: 'E_REF', file, msg: `vendorId "${value.vendorId}" 不存在` });
  const seenSystems = new Set<string>();
  for (const [i, rk] of value.rankings.entries()) {
    if (!rankingSystemIds.has(rk.systemId)) {
      errors.push({
        code: 'E_REF',
        file,
        msg: `rankings[${i}].systemId "${rk.systemId}" 不存在`,
      });
      continue;
    }
    if (seenSystems.has(rk.systemId))
      errors.push({
        code: 'E_DUP_RANKING',
        file,
        msg: `rankings 重复引用体系 "${rk.systemId}"`,
      });
    seenSystems.add(rk.systemId);
    const sys = rankingSystemById.get(rk.systemId);
    if (sys && !sys.categories.includes(value.category))
      warnings.push({
        code: 'W_RANKING_CAT',
        file,
        msg: `rankings[${i}] 体系 "${rk.systemId}" 未声明适用于分类 "${value.category}"`,
      });
  }
  // Rule 6(warning): 超期未复核
  const days = (Date.now() - new Date(value.lastReviewed).getTime()) / 86_400_000;
  if (days > STALE_DAYS)
    warnings.push({
      code: 'E_CONTENT_STALE',
      file,
      msg: `lastReviewed 已超 ${STALE_DAYS} 天（${Math.round(days)} 天），建议复核`,
    });
}

// signals/popularity.json：结构校验 + entryId 引用存在（外部抓取产物，非人工编辑）
try {
  const popRaw = JSON.parse(
    readFileSync(join(CONTENT_DIR, 'signals', 'popularity.json'), 'utf8'),
  ) as unknown;
  const parsed = PopularitySnapshot.safeParse(popRaw);
  if (!parsed.success) {
    for (const issue of parsed.error.issues)
      errors.push({
        code: 'E_SCHEMA',
        file: 'signals/popularity.json',
        msg: `${issue.path.join('.') || '(root)'}: ${issue.message}`,
      });
  } else {
    for (const id of Object.keys(parsed.data.entries)) {
      if (!nodeIds.has(id))
        warnings.push({
          code: 'W_POP_ORPHAN',
          file: 'signals/popularity.json',
          msg: `流行度条目 "${id}" 已无对应 entry（重跑 pnpm gen:popularity 可清理）`,
        });
    }
  }
} catch (e) {
  // 可选文件：不存在则跳过
  if ((e as NodeJS.ErrnoException).code !== 'ENOENT') {
    errors.push({ code: 'E_JSON', file: 'signals/popularity.json', msg: String(e) });
  }
}

// recipe.layers 引用存在
for (const { file, value } of recipes) {
  for (const [layer, id] of Object.entries(value.layers)) {
    if (!nodeIds.has(id))
      errors.push({ code: 'E_REF', file, msg: `layer "${layer}" 指向不存在的条目 "${id}"` });
  }
}

// Rule 2/4/5: 边引用、自环、对称重复、冲突互斥
const edgeSeen = new Map<string, string>(); // from|type|to
const symSeen = new Map<string, string>(); // type|sorted(pair)
const pairTypes = new Map<string, Set<string>>(); // sorted(pair) -> {conflicts_with, commonly_used_with}
const edgeIds = new Map<string, string>();

for (const { file, value } of edges) {
  if (edgeIds.has(value.id))
    errors.push({ code: 'E_DUP_ID', file, msg: `边 id "${value.id}" 重复` });
  else edgeIds.set(value.id, file);

  // Rule 2: 端点存在
  if (!nodeIds.has(value.from))
    errors.push({ code: 'E_REF', file, msg: `边 ${value.id} 的 from "${value.from}" 不存在` });
  if (!nodeIds.has(value.to))
    errors.push({ code: 'E_REF', file, msg: `边 ${value.id} 的 to "${value.to}" 不存在` });

  // Rule 4: 自环
  if (value.from === value.to)
    errors.push({ code: 'E_SELF_LOOP', file, msg: `边 ${value.id} 为自环` });

  // Rule 4: 精确重复
  const exact = `${value.from}|${value.type}|${value.to}`;
  if (edgeSeen.has(exact))
    errors.push({
      code: 'E_DUP_EDGE',
      file,
      msg: `重复边 ${exact}（另见 ${edgeSeen.get(exact)}）`,
    });
  else edgeSeen.set(exact, file);

  // Rule 4: 对称边反向重复
  const sortedPair = [value.from, value.to].sort().join('~');
  if (isSymmetric(value.type)) {
    const symKey = `${value.type}|${sortedPair}`;
    if (symSeen.has(symKey))
      errors.push({
        code: 'E_DUP_SYM',
        file,
        msg: `对称边 ${value.type} (${sortedPair}) 重复（另见 ${symSeen.get(symKey)}）`,
      });
    else symSeen.set(symKey, file);
  }

  // Rule 5: 收集 conflicts / commonly_used
  if (value.type === 'conflicts_with' || value.type === 'commonly_used_with') {
    const set = pairTypes.get(sortedPair) ?? new Set<string>();
    set.add(value.type);
    pairTypes.set(sortedPair, set);
  }

  // 国内外对标：约定 domestic → overseas；地区字段交叉检查
  if (value.type === 'domestic_equivalent_of' || value.type === 'overseas_equivalent_of') {
    const fromEntry = entries.find((e) => e.value.id === value.from)?.value;
    const toEntry = entries.find((e) => e.value.id === value.to)?.value;
    if (fromEntry && toEntry) {
      if (value.type === 'domestic_equivalent_of') {
        if (fromEntry.region === 'overseas')
          warnings.push({
            code: 'W_REGION_EDGE',
            file,
            msg: `边 ${value.id}: domestic_equivalent_of 的 from 宜为国内/both（现为 ${fromEntry.region}）`,
          });
        if (toEntry.region === 'domestic')
          warnings.push({
            code: 'W_REGION_EDGE',
            file,
            msg: `边 ${value.id}: domestic_equivalent_of 的 to 宜为国外/both（现为 ${toEntry.region}）`,
          });
      }
      if (value.type === 'overseas_equivalent_of') {
        warnings.push({
          code: 'W_REGION_EDGE',
          file,
          msg: `边 ${value.id}: 请改写为国内 --domestic_equivalent_of--> 国外，勿手写 overseas_equivalent_of`,
        });
      }
    }
  }
}

// Rule 5: 同一对不可同时冲突与常搭配
for (const [pair, types] of pairTypes) {
  if (types.has('conflicts_with') && types.has('commonly_used_with'))
    errors.push({
      code: 'E_CONFLICT_PARADOX',
      file: 'edges',
      msg: `节点对 ${pair} 同时存在 conflicts_with 与 commonly_used_with`,
    });
}

// 报告
const fmt = (p: Problem) => `  [${p.code}] ${p.file}: ${p.msg}`;
console.log('VibeHolding 内容校验');
console.log(
  `  条目 ${entries.length} · 边 ${edges.length} · 厂商 ${vendors.length} · 概念 ${concepts.length} · 方案 ${recipes.length} · 分类 ${categoryRows.length} · 排行体系 ${rankingSystemRows.length}`,
);
if (warnings.length) {
  console.log(`\n警告 (${warnings.length}):`);
  for (const w of warnings) console.log(fmt(w));
}
if (errors.length) {
  console.error(`\n错误 (${errors.length}):`);
  for (const e of errors) console.error(fmt(e));
  console.error('\n校验未通过。');
  process.exit(1);
}
console.log('\n校验通过 ✓');
