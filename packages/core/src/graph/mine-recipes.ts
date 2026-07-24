import type { Id } from '../schema/common.ts';
import type { StackRecipe } from '../schema/recipe.ts';
import type { ContentBundle } from '../types.ts';
import { buildGraph } from './engine.ts';

/** 挖矿时优先覆盖的层（分类 id） */
const PRIORITY_LAYERS = [
  'coding-agent',
  'llm',
  'framework',
  'ui-library',
  'baas-auth',
  'cloud-deploy',
  'payment',
  'database-storage',
  'model-gateway',
] as const;

type PairKey = string;

function pairKey(a: Id, b: Id): PairKey {
  return a < b ? `${a}|${b}` : `${b}|${a}`;
}

function slugify(parts: string[]): string {
  const raw = `draft-co-${parts.slice(0, 4).join('-')}`.toLowerCase();
  return (
    raw
      .replace(/[^a-z0-9-]/g, '-')
      .replace(/-+/g, '-')
      .replace(/^-|-$/g, '') || 'draft-co'
  );
}

/**
 * G7：从方案共现 + 公共 commonly_used_with 边挖掘 StackRecipe 草稿。
 * 贪心：以高频共现对为种子，按分类补全一层，校验无冲突后输出。
 */
export function mineRecipeDrafts(
  bundle: ContentBundle,
  opts?: {
    /** 额外共现来源（如我的技术栈） */
    extraStacks?: Array<{ layers?: Record<string, string> }>;
    maxDrafts?: number;
  },
): StackRecipe[] {
  const maxDrafts = opts?.maxDrafts ?? 6;
  const graph = buildGraph(bundle);
  const pairScore = new Map<PairKey, number>();

  const bump = (a: Id, b: Id, w: number) => {
    if (a === b) return;
    if (!bundle.entries.has(a) || !bundle.entries.has(b)) return;
    const k = pairKey(a, b);
    pairScore.set(k, (pairScore.get(k) ?? 0) + w);
  };

  const stacks = [...bundle.recipes.values(), ...(opts?.extraStacks ?? [])];
  for (const stack of stacks) {
    const ids = [...new Set(Object.values(stack.layers ?? {}))].filter(Boolean) as Id[];
    for (let i = 0; i < ids.length; i++) {
      for (let j = i + 1; j < ids.length; j++) {
        bump(ids[i] as Id, ids[j] as Id, 1);
      }
    }
  }

  for (const e of bundle.edges) {
    if (
      e.type !== 'commonly_used_with' &&
      e.type !== 'compatible_with' &&
      e.type !== 'integrates_with'
    )
      continue;
    bump(e.from, e.to, e.weight);
  }

  if (pairScore.size === 0) return [];

  const sortedPairs = [...pairScore.entries()].sort((a, b) => b[1] - a[1]);
  const existingSigs = new Set(
    [...bundle.recipes.values()].map((r) => Object.values(r.layers).slice().sort().join('|')),
  );

  const drafts: StackRecipe[] = [];
  const usedSeeds = new Set<string>();

  for (const [key, score] of sortedPairs) {
    if (drafts.length >= maxDrafts) break;
    const [a, b] = key.split('|') as [Id, Id];
    const seedKey = key;
    if (usedSeeds.has(seedKey)) continue;

    const ea = bundle.entries.get(a);
    const eb = bundle.entries.get(b);
    if (!ea || !eb) continue;
    if (ea.category === eb.category) continue;

    const layers: Record<string, Id> = {
      [ea.category]: a,
      [eb.category]: b,
    };

    // 按层贪心补全：选与已选共现分最高且无冲突的候选
    const selected = new Set<Id>([a, b]);
    for (const cat of PRIORITY_LAYERS) {
      if (layers[cat]) continue;
      let best: { id: Id; s: number } | null = null;
      for (const [id, entry] of bundle.entries) {
        if (entry.category !== cat) continue;
        if (selected.has(id)) continue;
        let s = 0;
        for (const sid of selected) {
          s += pairScore.get(pairKey(id, sid)) ?? 0;
        }
        if (s <= 0) continue;
        if (!best || s > best.s) best = { id, s };
      }
      if (!best) continue;
      // 临时加入校验冲突
      const trial = { ...layers, [cat]: best.id };
      const issues = graph.validateStack(trial);
      if (issues.some((i) => i.kind === 'conflict')) continue;
      layers[cat] = best.id;
      selected.add(best.id);
    }

    if (Object.keys(layers).length < 3) continue;

    const issues = graph.validateStack(layers);
    if (issues.some((i) => i.kind === 'conflict')) continue;

    const sig = Object.values(layers).slice().sort().join('|');
    if (existingSigs.has(sig)) continue;
    existingSigs.add(sig);
    usedSeeds.add(seedKey);

    const names = Object.values(layers)
      .map((id) => bundle.entries.get(id)?.name ?? id)
      .slice(0, 3);
    const id = slugify(Object.values(layers));
    // 保证唯一 id
    let finalId = id;
    let n = 2;
    while (bundle.recipes.has(finalId) || drafts.some((d) => d.id === finalId)) {
      finalId = `${id}-${n++}`;
    }

    drafts.push({
      id: finalId,
      name: `共现草案 · ${names.join(' + ')}`,
      target: '由方案/搭配共现自动挖掘，供人工确认后采用',
      layers,
      rationaleMd: `基于共现权重（种子对 ${ea.name}↔${eb.name} 分 ${score.toFixed(2)}）贪心补全各层；请核对冲突与预算后再采用。`,
      estimatedCost: '待评估',
      caveats: [
        '自动挖掘草稿，非人工核实方案',
        ...issues
          .filter((i) => i.kind === 'vendor-concentration')
          .map(
            (i) =>
              `供应商集中：${'vendorId' in i ? i.vendorId : ''} ×${'count' in i ? i.count : ''}`,
          ),
      ],
    });
  }

  return drafts;
}

/**
 * G8：沿 prerequisite_of / requires_knowledge 生成到目标节点的学习路径（拓扑序）。
 * 无前置边时返回 [targetId]（若存在）。
 */
export function learningPath(bundle: ContentBundle, targetId: Id): Id[] {
  if (!bundle.entries.has(targetId) && !bundle.concepts.has(targetId)) return [];
  const graph = buildGraph(bundle);
  const ancestors = new Set<Id>();
  const queue: Id[] = [targetId];
  const seen = new Set<Id>([targetId]);

  while (queue.length > 0) {
    const cur = queue.shift() as Id;
    const rel = graph.related(cur);
    const prereqs = rel.requires_knowledge ?? [];
    for (const p of prereqs) {
      if (seen.has(p)) continue;
      // 只保留条目或概念
      if (!bundle.entries.has(p) && !bundle.concepts.has(p)) continue;
      seen.add(p);
      ancestors.add(p);
      queue.push(p);
    }
  }

  if (ancestors.size === 0) return [targetId];

  // Kahn 拓扑：边 u→v 表示 u 是 v 的前置（先学 u）
  const nodes = [...ancestors, targetId];
  const nodeSet = new Set(nodes);
  const indeg = new Map<Id, number>();
  const outs = new Map<Id, Id[]>();
  for (const id of nodes) {
    indeg.set(id, 0);
    outs.set(id, []);
  }
  for (const id of nodes) {
    const prereqs = (graph.related(id).requires_knowledge ?? []).filter((p) => nodeSet.has(p));
    for (const p of prereqs) {
      outs.get(p)?.push(id);
      indeg.set(id, (indeg.get(id) ?? 0) + 1);
    }
  }

  const ready = nodes.filter((id) => (indeg.get(id) ?? 0) === 0);
  const order: Id[] = [];
  while (ready.length > 0) {
    // 稳定：按 id 排序取一
    ready.sort((x, y) => x.localeCompare(y));
    const u = ready.shift() as Id;
    order.push(u);
    for (const v of outs.get(u) ?? []) {
      const next = (indeg.get(v) ?? 1) - 1;
      indeg.set(v, next);
      if (next === 0) ready.push(v);
    }
  }

  // 有环则退回 BFS 顺序
  if (order.length !== nodes.length) {
    return [...ancestors].sort().concat(targetId);
  }
  return order;
}
