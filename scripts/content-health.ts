/**
 * 内容不变量体检（模块 12 / T-AQUA-3）。
 * 比 validate 更高一层：拦「合法但退化」的自动变更。
 *
 * 用法：
 *   pnpm health
 *   pnpm health --write-baseline   # 在有意扩种后刷新基线
 *
 * CI / aqua Publisher 在 validate + gen:content 之后调用；失败则退出码 1。
 */
import { existsSync, mkdirSync, readFileSync, readdirSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import process from 'node:process';

const ROOT = process.cwd();
const CONTENT = join(ROOT, 'content');
const ENTRIES = join(CONTENT, 'entries');
const CONCEPTS = join(CONTENT, 'concepts');
const BASELINE = join(CONTENT, 'signals', 'health-baseline.json');

const writeBaseline = process.argv.includes('--write-baseline');

interface Baseline {
  generatedAt: string;
  entryCount: number;
  edgeCount: number;
  conceptCount: number;
  avgDescriptionLen: number;
  avgOneLinerLen: number;
  entriesWithoutSources: number;
  emptyLeaves: string[];
}

interface Problem {
  level: 'error' | 'warn';
  code: string;
  msg: string;
}

function readJson<T>(path: string): T {
  return JSON.parse(readFileSync(path, 'utf8')) as T;
}

function listJson(dir: string): string[] {
  try {
    return readdirSync(dir).filter((f) => f.endsWith('.json'));
  } catch {
    return [];
  }
}

function main(): void {
  const problems: Problem[] = [];

  const entryFiles = listJson(ENTRIES);
  const edgeFiles = listJson(join(CONTENT, 'edges'));
  const conceptFiles = listJson(CONCEPTS);
  const categories = readJson<Array<{ id: string; kind: string }>>(join(CONTENT, 'categories.json'));
  const leaves = categories.filter((c) => c.kind === 'leaf').map((c) => c.id);

  let descLenSum = 0;
  let oneLinerLenSum = 0;
  let withoutSources = 0;
  const perLeaf = new Map<string, number>();
  for (const leaf of leaves) perLeaf.set(leaf, 0);

  // 品类标签型 oneLiner 的粗糙启发式：过短或以「是一种/一个」开头
  let weakOneLiners = 0;

  for (const f of entryFiles) {
    const e = readJson<{
      id: string;
      category: string;
      oneLiner?: string;
      descriptionMd?: string;
      sources?: string[];
    }>(join(ENTRIES, f));
    const desc = e.descriptionMd ?? '';
    const ol = e.oneLiner ?? '';
    descLenSum += desc.length;
    oneLinerLenSum += ol.length;
    if (!e.sources || e.sources.length === 0) withoutSources++;
    perLeaf.set(e.category, (perLeaf.get(e.category) ?? 0) + 1);
    if (ol.length < 12 || /^(一种|一个|是)/.test(ol)) weakOneLiners++;
  }

  const entryCount = entryFiles.length;
  const avgDescriptionLen = entryCount ? descLenSum / entryCount : 0;
  const avgOneLinerLen = entryCount ? oneLinerLenSum / entryCount : 0;
  const emptyLeaves = leaves.filter((id) => (perLeaf.get(id) ?? 0) === 0);

  // —— 绝对闸门 ——
  if (emptyLeaves.length > 0) {
    problems.push({
      level: 'error',
      code: 'H_EMPTY_LEAF',
      msg: `空叶类：${emptyLeaves.join(', ')}`,
    });
  }
  if (avgDescriptionLen < 100) {
    problems.push({
      level: 'error',
      code: 'H_DESC_TOO_SHORT',
      msg: `descriptionMd 平均长度 ${avgDescriptionLen.toFixed(1)} < 100`,
    });
  }
  if (weakOneLiners / Math.max(entryCount, 1) > 0.15) {
    problems.push({
      level: 'error',
      code: 'H_WEAK_ONELINER',
      msg: `弱 oneLiner 占比 ${(
        (100 * weakOneLiners) /
        entryCount
      ).toFixed(1)}% > 15%（过短或以「一种/一个/是」开头）`,
    });
  }
  if (withoutSources / Math.max(entryCount, 1) > 0.35) {
    problems.push({
      level: 'warn',
      code: 'H_NO_SOURCES',
      msg: `无 sources 条目占比 ${(
        (100 * withoutSources) /
        entryCount
      ).toFixed(1)}%（建议逐步补齐）`,
    });
  }

  // —— 相对基线 ——
  let baseline: Baseline | null = null;
  if (existsSync(BASELINE)) {
    try {
      baseline = readJson<Baseline>(BASELINE);
    } catch {
      problems.push({
        level: 'warn',
        code: 'H_BASELINE_BAD',
        msg: 'health-baseline.json 无法解析，跳过相对检查',
      });
    }
  } else if (!writeBaseline) {
    problems.push({
      level: 'warn',
      code: 'H_BASELINE_MISSING',
      msg: '尚无 health-baseline.json；跑 pnpm health --write-baseline 生成',
    });
  }

  if (baseline) {
    const drop = (baseline.entryCount - entryCount) / Math.max(baseline.entryCount, 1);
    if (drop > 0.02) {
      problems.push({
        level: 'error',
        code: 'H_ENTRY_DROP',
        msg: `条目数下降 ${(100 * drop).toFixed(1)}%（${baseline.entryCount} → ${entryCount}），超过 2%`,
      });
    }
    const descDrop =
      (baseline.avgDescriptionLen - avgDescriptionLen) / Math.max(baseline.avgDescriptionLen, 1);
    if (descDrop > 0.05) {
      problems.push({
        level: 'error',
        code: 'H_DESC_DROP',
        msg: `descriptionMd 平均长度下降 ${(100 * descDrop).toFixed(1)}%（${baseline.avgDescriptionLen.toFixed(0)} → ${avgDescriptionLen.toFixed(0)}）`,
      });
    }
    if (conceptFiles.length + 5 < baseline.conceptCount) {
      problems.push({
        level: 'error',
        code: 'H_CONCEPT_DROP',
        msg: `概念数异常下降（${baseline.conceptCount} → ${conceptFiles.length}）`,
      });
    }
  }

  const snap: Baseline = {
    generatedAt: new Date().toISOString().slice(0, 10),
    entryCount,
    edgeCount: edgeFiles.length,
    conceptCount: conceptFiles.length,
    avgDescriptionLen: Math.round(avgDescriptionLen * 10) / 10,
    avgOneLinerLen: Math.round(avgOneLinerLen * 10) / 10,
    entriesWithoutSources: withoutSources,
    emptyLeaves,
  };

  console.log('VibeHolding 内容体检');
  console.log(
    `  条目 ${snap.entryCount} · 边 ${snap.edgeCount} · 概念 ${snap.conceptCount} · 叶类 ${leaves.length}（空 ${emptyLeaves.length}）`,
  );
  console.log(
    `  descriptionMd 均长 ${snap.avgDescriptionLen} · oneLiner 均长 ${snap.avgOneLinerLen} · 无 sources ${withoutSources} · 弱 oneLiner ${weakOneLiners}`,
  );

  if (writeBaseline) {
    mkdirSync(join(CONTENT, 'signals'), { recursive: true });
    writeFileSync(BASELINE, `${JSON.stringify(snap, null, 2)}\n`, 'utf8');
    console.log(`\n已写入基线 ${BASELINE}`);
  }

  const warns = problems.filter((p) => p.level === 'warn');
  const errs = problems.filter((p) => p.level === 'error');
  if (warns.length) {
    console.log(`\n警告 (${warns.length}):`);
    for (const w of warns) console.log(`  [${w.code}] ${w.msg}`);
  }
  if (errs.length) {
    console.error(`\n错误 (${errs.length}):`);
    for (const e of errs) console.error(`  [${e.code}] ${e.msg}`);
    console.error('\n内容体检未通过。');
    process.exit(1);
  }
  console.log('\n内容体检通过 ✓');
}

main();
