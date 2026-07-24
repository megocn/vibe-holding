import { readFile } from 'node:fs/promises';
import { join } from 'node:path';
import type { FeedSource, Region } from '@vh/core';
import { feedItemToUpdate, parseFeedXml } from '@vh/core';
import { type Command, Option } from 'commander';
import { entryName, getContext } from './context.ts';
import { fail, printJson, printLines } from './format.ts';

export function registerSearch(program: Command): void {
  program
    .command('search')
    .description('检索条目')
    .argument('<kw>', '关键词')
    .option('--category <id>', '分类 id')
    .option('--region <region>', 'domestic | overseas | both')
    .option('--tag <tag>', '标签（可重复）', (v, acc: string[]) => [...acc, v], [] as string[])
    .option('--json', 'JSON 输出', false)
    .addOption(new Option('--limit <n>', '最多结果数').default('20'))
    .action(
      async (
        kw: string,
        opts: {
          category?: string;
          region?: string;
          tag: string[];
          json?: boolean;
          limit: string;
        },
      ) => {
        const { bundle, index } = await getContext();
        const region = opts.region as Region | undefined;
        if (region && !['domestic', 'overseas', 'both'].includes(region)) {
          fail(`无效 region: ${region}`);
        }
        const hits = index.query(kw, {
          category: opts.category,
          region,
          tags: opts.tag.length ? opts.tag : undefined,
        });
        const limit = Math.max(1, Number(opts.limit) || 20);
        const rows = hits.slice(0, limit).map((h) => {
          const e = bundle.entries.get(h.id);
          return {
            id: h.id,
            name: e?.name ?? h.id,
            score: Number(h.score.toFixed(3)),
            category: e?.category,
            region: e?.region,
            oneLiner: e?.oneLiner,
          };
        });
        if (opts.json) {
          printJson(rows);
          return;
        }
        if (rows.length === 0) {
          printLines(['(无结果)']);
          return;
        }
        printLines(
          rows.map(
            (r) =>
              `${r.id.padEnd(22)} ${String(r.score).padStart(5)}  ${r.name}  · ${r.category}/${r.region}\n  ${r.oneLiner ?? ''}`,
          ),
        );
      },
    );
}

export function registerShow(program: Command): void {
  program
    .command('show')
    .description('显示条目详情（含关联摘要）')
    .argument('<id>', '条目 id')
    .option('--json', 'JSON 输出', false)
    .action(async (id: string, opts: { json?: boolean }) => {
      const { bundle, graph } = await getContext();
      const entry = bundle.entries.get(id);
      if (!entry) fail(`条目不存在: ${id}`);
      const related = graph.related(id);
      if (opts.json) {
        printJson({ entry, related });
        return;
      }
      const lines = [
        `# ${entry.name} (${entry.id})`,
        entry.oneLiner,
        '',
        `分类: ${entry.category} · 区域: ${entry.region} · 成熟度: ${entry.maturity}`,
        `定价: ${entry.pricing.model}${entry.pricing.notes ? ` · ${entry.pricing.notes}` : ''}`,
        entry.officialUrl ? `官网: ${entry.officialUrl}` : '',
        '',
        '## 关联',
      ];
      const keys = Object.keys(related).sort();
      if (keys.length === 0) lines.push('(无)');
      for (const k of keys) {
        const ids = related[k] ?? [];
        lines.push(`- ${k}: ${ids.map((tid) => `${entryName(bundle, tid)} (${tid})`).join(', ')}`);
      }
      printLines(lines.filter((l) => l !== undefined));
    });
}

export function registerRelated(program: Command): void {
  program
    .command('related')
    .description('显示关系边')
    .argument('<id>', '条目 id')
    .option('--type <type>', '仅某种关系类型')
    .option('--json', 'JSON 输出', false)
    .action(async (id: string, opts: { type?: string; json?: boolean }) => {
      const { bundle, graph } = await getContext();
      if (!bundle.entries.has(id) && !bundle.concepts.has(id)) {
        fail(`节点不存在: ${id}`);
      }
      let related = graph.related(id);
      if (opts.type) {
        related = { [opts.type]: related[opts.type] ?? [] };
      }
      if (opts.json) {
        printJson({ id, related });
        return;
      }
      const lines: string[] = [];
      for (const [type, ids] of Object.entries(related).sort(([a], [b]) => a.localeCompare(b))) {
        if (!ids.length) continue;
        lines.push(`${type}:`);
        for (const tid of ids) {
          lines.push(`  - ${entryName(bundle, tid)} (${tid})`);
        }
      }
      printLines(lines.length ? lines : ['(无关联)']);
    });
}

export function registerAlt(program: Command): void {
  program
    .command('alt')
    .description('替代品 / 国内平替')
    .argument('<id>', '条目 id')
    .option('--json', 'JSON 输出', false)
    .action(async (id: string, opts: { json?: boolean }) => {
      const { bundle, graph } = await getContext();
      if (!bundle.entries.has(id)) fail(`条目不存在: ${id}`);
      const alternatives = graph.alternatives(id);
      const domestic = graph.domesticEquivalents(id);
      if (opts.json) {
        printJson({ id, alternatives, domestic });
        return;
      }
      printLines([
        '## 替代 / 开源平替',
        ...(alternatives.length
          ? alternatives.map((tid) => `- ${entryName(bundle, tid)} (${tid})`)
          : ['(无)']),
        '',
        '## 国内对标',
        ...(domestic.length
          ? domestic.map((tid) => `- ${entryName(bundle, tid)} (${tid})`)
          : ['(无)']),
      ]);
    });
}

export function registerRecipe(program: Command): void {
  program
    .command('recipe')
    .description('列出或查看方案模板')
    .argument('[id]', '方案 id（省略则列出全部）')
    .option('--json', 'JSON 输出', false)
    .action(async (id: string | undefined, opts: { json?: boolean }) => {
      const { bundle, graph } = await getContext();
      if (!id) {
        const list = [...bundle.recipes.values()].map((r) => ({
          id: r.id,
          name: r.name,
          target: r.target,
          layers: Object.keys(r.layers).length,
        }));
        if (opts.json) {
          printJson(list);
          return;
        }
        printLines(
          list.length
            ? list.map((r) => `${r.id.padEnd(28)} ${r.name}  (${r.layers} 层)\n  ${r.target}`)
            : ['(无方案)'],
        );
        return;
      }
      const recipe = bundle.recipes.get(id);
      if (!recipe) fail(`方案不存在: ${id}`);
      const issues = graph.validateStack(recipe.layers);
      if (opts.json) {
        printJson({ recipe, issues });
        return;
      }
      const lines = [
        `# ${recipe.name} (${recipe.id})`,
        recipe.target,
        '',
        '## 层',
        ...Object.entries(recipe.layers).map(
          ([layer, eid]) => `- ${layer}: ${entryName(bundle, eid)} (${eid})`,
        ),
        '',
        `预估成本: ${recipe.estimatedCost ?? '—'}`,
        '',
        '## 校验',
        ...(issues.length
          ? issues.map((i) =>
              i.kind === 'conflict'
                ? `- 冲突: ${i.a} ↔ ${i.b}`
                : `- 供应商集中: ${i.vendorId} ×${i.count}`,
            )
          : ['- 通过（无冲突 / 无过度集中）']),
      ];
      if (recipe.caveats?.length) {
        lines.push('', '## 注意', ...recipe.caveats.map((c) => `- ${c}`));
      }
      printLines(lines);
    });
}

export function registerStack(program: Command): void {
  const stack = program.command('stack').description('技术栈相关');

  stack
    .command('validate')
    .description('校验一套 stack（JSON 文件：{ layers: { layer: entryId } } 或直接 layers 对象）')
    .argument('<file>', 'JSON 文件路径')
    .option('--json', 'JSON 输出', false)
    .action(async (file: string, opts: { json?: boolean }) => {
      const { readFile } = await import('node:fs/promises');
      const { resolve } = await import('node:path');
      const { bundle, graph } = await getContext();
      let raw: unknown;
      try {
        raw = JSON.parse(await readFile(resolve(file), 'utf8'));
      } catch (e) {
        fail(`无法读取 JSON: ${e instanceof Error ? e.message : String(e)}`);
      }
      const layers =
        raw &&
        typeof raw === 'object' &&
        'layers' in raw &&
        typeof (raw as { layers: unknown }).layers === 'object'
          ? ((raw as { layers: Record<string, string> }).layers ?? {})
          : (raw as Record<string, string>);
      if (!layers || typeof layers !== 'object' || Array.isArray(layers)) {
        fail('JSON 需为 { layers: { ... } } 或 layers 对象');
      }
      const missing = Object.entries(layers).filter(([, id]) => !bundle.entries.has(id));
      const issues = graph.validateStack(layers);
      if (opts.json) {
        printJson({ layers, missing: missing.map(([k, v]) => ({ layer: k, id: v })), issues });
        return;
      }
      const lines = [
        '## 层',
        ...Object.entries(layers).map(
          ([layer, eid]) =>
            `- ${layer}: ${entryName(bundle, eid)} (${eid})${bundle.entries.has(eid) ? '' : ' ⚠ 未知条目'}`,
        ),
        '',
        '## 结果',
      ];
      if (missing.length === 0 && issues.length === 0) {
        lines.push('通过');
      } else {
        for (const [layer, eid] of missing) {
          lines.push(`- 未知条目: ${layer} → ${eid}`);
        }
        for (const i of issues) {
          lines.push(
            i.kind === 'conflict'
              ? `- 冲突: ${i.a} ↔ ${i.b}`
              : `- 供应商集中: ${i.vendorId} ×${i.count}`,
          );
        }
      }
      printLines(lines);
      if (missing.length || issues.some((i) => i.kind === 'conflict')) process.exitCode = 2;
    });
}

export function registerIntel(program: Command): void {
  const intel = program.command('intel').description('情报抓取（RSS/Atom → 草稿候选）');

  intel
    .command('feeds')
    .description('列出 content/feeds.json 订阅源')
    .option('--json', 'JSON 输出', false)
    .action(async (opts: { json?: boolean }) => {
      const { contentDir, bundle } = await getContext();
      const feeds = await loadFeeds(contentDir);
      const rows = feeds.map((f) => ({
        ...f,
        entryExists: bundle.entries.has(f.entryId),
        entryName: entryName(bundle, f.entryId),
      }));
      if (opts.json) {
        printJson(rows);
        return;
      }
      if (rows.length === 0) {
        printLines(['(无订阅源)']);
        return;
      }
      printLines(
        rows.map(
          (r) => `${r.entryId.padEnd(20)} ${r.entryExists ? '✓' : '✗'}  ${r.label ?? ''}  ${r.url}`,
        ),
      );
    });

  intel
    .command('scrape')
    .description('抓取订阅源并输出草稿候选（不写入磁盘）')
    .option('--entry <id>', '仅抓取指定条目')
    .option('--json', 'JSON 输出', false)
    .addOption(new Option('--limit <n>', '每源最多条数').default('3'))
    .action(async (opts: { entry?: string; json?: boolean; limit: string }) => {
      const { contentDir, bundle } = await getContext();
      const feeds = (await loadFeeds(contentDir)).filter((f) => {
        if (opts.entry && f.entryId !== opts.entry) return false;
        return bundle.entries.has(f.entryId);
      });
      if (feeds.length === 0) fail(opts.entry ? `无匹配订阅源: ${opts.entry}` : '无可用订阅源');

      const limit = Math.max(1, Number(opts.limit) || 3);
      const drafts: Array<{
        entryId: string;
        entryName: string;
        feed: string;
        update: ReturnType<typeof feedItemToUpdate>;
      }> = [];
      const errors: Array<{ entryId: string; url: string; error: string }> = [];

      for (const feed of feeds) {
        try {
          const res = await fetch(feed.url, {
            redirect: 'follow',
            headers: {
              Accept: 'application/rss+xml, application/atom+xml, application/xml, text/xml, */*',
              'User-Agent': 'VibeHolding-CLI/0.1',
            },
          });
          if (!res.ok) throw new Error(`HTTP ${res.status}`);
          const xml = await res.text();
          const items = parseFeedXml(xml).slice(0, limit);
          for (const item of items) {
            drafts.push({
              entryId: feed.entryId,
              entryName: entryName(bundle, feed.entryId),
              feed: feed.label ?? feed.url,
              update: feedItemToUpdate(item),
            });
          }
        } catch (err) {
          errors.push({
            entryId: feed.entryId,
            url: feed.url,
            error: err instanceof Error ? err.message : String(err),
          });
        }
      }

      if (opts.json) {
        printJson({ drafts, errors });
        return;
      }
      printLines([
        `## 草稿候选 ${drafts.length}`,
        ...drafts.map(
          (d) =>
            `- [${d.entryId}] ${d.update.date} ${d.update.type}  ${d.update.summary}${d.update.source ? `\n  ${d.update.source}` : ''}`,
        ),
      ]);
      if (errors.length) {
        printLines(['', '## 失败', ...errors.map((e) => `- ${e.entryId}: ${e.error}`)]);
      }
      if (errors.length && drafts.length === 0) process.exitCode = 2;
    });
}

async function loadFeeds(contentDir: string): Promise<FeedSource[]> {
  try {
    const raw = await readFile(join(contentDir, 'feeds.json'), 'utf8');
    const data = JSON.parse(raw) as unknown;
    if (!Array.isArray(data)) return [];
    return data.filter(
      (x): x is FeedSource =>
        x &&
        typeof x === 'object' &&
        typeof (x as FeedSource).entryId === 'string' &&
        typeof (x as FeedSource).url === 'string',
    );
  } catch {
    return [];
  }
}
